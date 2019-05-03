# special subclass of FakeDriver that also adds OVS controls.
# this file should be copied into the Nova installation in the local
# Python, such as /usr/lib/python2.7/site-packages/nova/virt/fake_vif.py
# It then can be invoked from nova.conf via
# compute_driver=fake_vif.OVSFakeDriver

from oslo_log import log as logging

import nova.conf
from nova import exception
from nova import utils
from nova.virt import fake


CONF = nova.conf.CONF

LOG = logging.getLogger(__name__)


def _ovs_vsctl(args):
    full_args = ["ovs-vsctl", "--timeout=%s" % CONF.ovs_vsctl_timeout] + args
    LOG.info(
        "running ovs-vsctl command: %s",
        " ".join(str(arg) for arg in full_args),
    )
    try:
        return utils.execute(*full_args, run_as_root=True)
    except Exception as e:
        LOG.error(
            "Unable to execute %(cmd)s. Exception: %(exception)s",
            {"cmd": full_args, "exception": e},
        )
        raise exception.OvsConfigurationFailure(inner_exception=e)


class OVSFakeDriver(fake.FakeDriver):
    def __init__(self, *arg, **kw):
        LOG.info("Spinning up OVSFakeDriver")
        super(OVSFakeDriver, self).__init__(*arg, **kw)

    def spawn(
        self,
        context,
        instance,
        image_meta,
        injected_files,
        admin_password,
        allocations,
        network_info=None,
        block_device_info=None,
    ):
        self.plug_vifs(instance, network_info)
        return super(OVSFakeDriver, self).spawn(
            context,
            instance,
            image_meta,
            injected_files,
            admin_password,
            allocations,
            network_info=network_info,
            block_device_info=block_device_info,
        )

    def destroy(
        self,
        context,
        instance,
        network_info,
        block_device_info=None,
        destroy_disks=True,
    ):
        self.unplug_vifs(instance, network_info)
        return super(OVSFakeDriver, self).destroy(
            context,
            instance,
            network_info,
            block_device_info=block_device_info,
            destroy_disks=destroy_disks,
        )

    def plug_vif(self, instance, vif):
        bridge = "br-int"
        dev = vif.get("devname")
        port = vif.get("id")
        mac_address = vif.get("address")
        if not dev or not port or not mac_address:
            return
        else:
            cmds = [
                ["--", "--may-exist", "add-port", bridge, dev],
                ["--", "set", "Interface", dev, "type=internal"],
                [
                    "--",
                    "set",
                    "Interface",
                    dev,
                    "external-ids:iface-id=%s" % port,
                ],
                [
                    "--",
                    "set",
                    "Interface",
                    dev,
                    "external-ids:iface-status=active",
                ],
                [
                    "--",
                    "set",
                    "Interface",
                    dev,
                    "external-ids:attached-mac=%s" % mac_address,
                ],
            ]
            _ovs_vsctl(sum(cmds, []))

    def plug_vifs(self, instance, network_info):
        """Plug VIFs into networks."""
        for vif in network_info:
            self.plug_vif(instance, vif)

    def unplug_vif(self, instance, vif):
        bridge = "br-int"
        dev = vif.get("devname")
        port = vif.get("id")
        if not dev:
            if not port:
                return
            dev = "tap" + str(port[0:11])
        _ovs_vsctl(["--", "--if-exists", "del-port", bridge, dev])

    def unplug_vifs(self, instance, network_info):
        """Unplug VIFs from networks."""

        for vif in network_info:
            self.unplug_vif(instance, vif)
