#!/usr/bin/python

import argparse
import io
import re
import sys

if sys.version_info.major == 3:
    import configparser
else:
    import ConfigParser as configparser


def main(argv=None):
    parser = argparse.ArgumentParser(description="merges conf files in order")

    parser.add_argument(
        "-e",
        action="append",
        help="Substitution variable, e.g. -e 'my_ip=172.18.0.10' -e 'foo=bar'.  "
        "Hard-substitutes into files named '<filename>.fragment', otherwise is not used.",
    )
    parser.add_argument(
        "src",
        type=str,
        nargs='+',
        help="Source files, highest precedence is given to the leftmost file",
    )
    parser.add_argument("dest", type=str, help="Destination file")
    args = parser.parse_args()

    if args.e:
        environment_defaults = {
            m.group(1): m.group(2)
            for m in [
                re.match(r'([\w_]+)\s*=\s*(.*)', env)
                for env in args.e
            ] if m
        }
    else:
        environment_defaults = {}

    config = configparser.RawConfigParser()

    for src_file in reversed(args.src):
        if src_file.endswith(".fragment"):
            # don't use configparser interpolation, since services don't use it
            # and configparser.write() doesn't expand them;
            # instead, hard-interpolate the contents before adding to the config,
            # and only with our .fragment files that don't have lots of templated
            # stuff and comments in them
            with open(src_file) as file_:
                contents = file_.read()
                contents = contents % environment_defaults
            config.readfp(io.BytesIO(contents))
        else:
            config.read(src_file)

    with open(args.dest, "w") as file_:
        config.write(file_)


if __name__ == "__main__":
    main()
