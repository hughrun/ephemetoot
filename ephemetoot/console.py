#!/usr/bin/env python3

#  #####################################################################
#     Ephemetoot - A command line tool to delete your old toots
#     Copyright (C) 2018 Hugh Rundle, 2019-2020 Hugh Rundle & others
#     Initial work based on tweet-deleting script by @flesueur
#     (https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f)
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

#     You can contact Hugh on Mastodon: @hugh@ausglam.space
#     or email: ephemetoot@hugh.run
#  #####################################################################

# import
import yaml

# from standard library
from argparse import ArgumentParser
from datetime import datetime, timezone
import os
import pkg_resources

# import funtions
from ephemetoot import ephemetoot as func

# version number from package info
vnum = pkg_resources.require("ephemetoot")[0].version

parser = ArgumentParser()
parser.add_argument(
    "--archive-deleted",
    action="store_true",
    help="Only archive toots that are being deleted",
)
parser.add_argument(
    "--config",
    action="store",
    metavar="filepath",
    default="config.yaml",
    help="Filepath of your config file, absolute or relative to the current directory. If no --config path is provided, ephemetoot will use 'config.yaml'in the current directory",
)
parser.add_argument(
    "--datestamp",
    action="store_true",
    help="Include a datetime stamp for every action (e.g. deleting a toot)",
)
parser.add_argument(
    "--hide-skipped",
    "--hide_skipped",
    action="store_true",
    help="Do not write to log when skipping saved toots",
)
parser.add_argument(
    "--init",
    action="store_true",
    help="Create a config file that is saved in the current directory",
)
parser.add_argument(
    "--pace",
    action="store_true",
    help="Slow deletion actions to match API rate limit to avoid pausing",
)
parser.add_argument(
    "-q",
    "--quiet",
    action="count",
    help="Limits logging to one line per account. Use -qq to limit logging to accounts with deleted toots and -qqq to completely suppress logging.",
)
parser.add_argument(
    "--retry-mins",
    action="store",
    metavar="minutes",
    nargs="?",
    const="1",
    default="1",
    type=int,
    help="Number of minutes to wait between retries, when an error is thrown",
)
parser.add_argument(
    "--schedule",
    action="store",
    metavar="filepath",
    nargs="?",
    const=".",
    help="Save and load plist file on MacOS",
)
parser.add_argument(
    "--test", action="store_true", help="Do a test run without deleting any toots"
)
parser.add_argument(
    "--time",
    action="store",
    metavar=("hour", "minute"),
    nargs="*",
    help="Hour and minute to schedule: e.g. 9 30 for 9.30am",
)
parser.add_argument(
    "--verbose",
    action="store_true",
    help="Log more information about errors and exceptions",
)
parser.add_argument(
    "--version",
    action="store_true",
    help="Display the version numbers of the installed and latest versions",
)

options = parser.parse_args()
if options.config[0] == "~":
    config_file = os.path.expanduser(options.config)
elif options.config[0] == "/":
    # make sure user isn't passing in something dodgy
    if os.path.exists(options.config):
        config_file = options.config
    else:
        config_file = ""
else:
    config_file = os.path.join(os.getcwd(), options.config)


def main():
    """
    Call ephemetoot.check_toots() on each user in the config file, with options set via flags from command line.
    """
    try:

        if options.init:
            func.init()
        elif options.version:
            func.version(vnum)
        elif options.schedule:
            func.schedule(options)
        else:
            if not options.quiet:
                print("")
                print("============= EPHEMETOOT v" + vnum + " ================")
                print(
                    "Running at "
                    + str(
                        datetime.now(timezone.utc).strftime("%a %d %b %Y %H:%M:%S %z")
                    )
                )
                print("================================================")
                print("")
            if options.test:
                print("This is a test run...\n")
            with open(config_file) as config:
                for accounts in yaml.safe_load_all(config):
                    for user in accounts:
                        func.check_toots(user, options)

    except FileNotFoundError as err:

        if err.filename == config_file:
            print("🕵️  Missing config file")
            print("Run \033[92mephemetoot --init\033[0m to create a new one\n")

        else:
            print("\n🤷‍♂️  The archive directory in your config file does not exist")
            print("Create the directory or correct your config before trying again\n")


if __name__ == "__main__":
    main()
