# standard library
from datetime import date, datetime, timedelta, timezone
import json
import os
import subprocess
import sys
import time

# third party
from mastodon import (
    Mastodon,
    MastodonError,
    MastodonAPIError,
    MastodonNetworkError,
    MastodonRatelimitError,
)
import requests

# local
from ephemetoot import plist

def compulsory_input(tags, name, example):

    value = ""
    while len(value) < 1:
        if example:
            value = input(tags[0] + name + tags[1] + example + tags[2])
        else:
            value = input(tags[0] + name + tags[2])

    return value

def digit_input(tags, name, example):

    value = ""
    while value.isdigit() == False:
        if example:
            value = input(tags[0] + name + tags[1] + example + tags[2])
        else:
            value = input(tags[0] + name + tags[2])

    return value

def yes_no_input(tags, name):
    value = ""
    while value not in ["y", "n"]:
        value = input(
            tags[0] + name + tags[1] + "(y or n):" + tags[2]
        )
    return_val = "true" if value == "y" else "false"
    return return_val

def optional_input(tags, name, example):
    value = input(tags[0] + name + tags[1] + example + tags[2])
    return value
        
def init():
    '''
    Creates a config.yaml file in the current directory, based on user input.
    '''
    try:

        # text colour markers (beginning, example, end)
        tags = ("\033[96m", "\033[2m", "\033[0m")

        conf_token = compulsory_input(tags, "Access token: ", None)
        conf_user = compulsory_input(tags, "Username", "(without the '@' - e.g. alice):")
        conf_url = compulsory_input(tags, "Base URL", "(e.g. example.social):")
        conf_days = digit_input(tags, "Days to keep", "(default 365):")
        conf_pinned = yes_no_input(tags, "Keep pinned toots?")
        conf_keep_toots = optional_input(tags, "Toots to keep", "(optional list of IDs separated by commas):")
        conf_keep_hashtags = optional_input(tags, "Hashtags to keep", "(optional list separated by commas):")
        conf_keep_visibility = optional_input(tags, "Visibility to keep", "(optional list separated by commas):")
        conf_archive = optional_input(tags, "Archive path", "(optional filepath for archive):")

        # write out the config file
        with open("config.yaml", "w") as configfile:

            configfile.write("-")
            configfile.write("\n  access_token: " + conf_token)
            configfile.write("\n  username: " + conf_user)
            configfile.write("\n  base_url: " + conf_url)
            configfile.write("\n  days_to_keep: " + conf_days)
            configfile.write("\n  keep_pinned: " + conf_pinned)

            if len(conf_keep_toots) > 0:
                keep_list = conf_keep_toots.split(",")
                configfile.write("\n  toots_to_keep:")
                for toot in keep_list:
                    configfile.write("\n    - " + toot.strip())

            if len(conf_keep_hashtags) > 0:
                tag_list = conf_keep_hashtags.split(",")
                configfile.write("\n  hashtags_to_keep:")
                for tag in tag_list:
                    configfile.write("\n    - " + tag.strip())

            if len(conf_keep_visibility) > 0:
                viz_list = conf_keep_visibility.split(",")
                configfile.write("\n  visibility_to_keep:")
                for mode in viz_list:
                    configfile.write("\n    - " + mode.strip())

            if len(conf_archive) > 0:
                configfile.write("\n  archive: " + conf_archive)

            configfile.close()

    except Exception as e:
        print(e)

def version(vnum):
    '''
    Prints current and latest version numbers to console.
    '''

    try:
        latest = requests.get(
            "https://api.github.com/repos/hughrun/ephemetoot/releases/latest"
        )
        res = latest.json()
        latest_version = res["tag_name"]
        print("\nephemetoot ==> 🥳 ==> 🧼 ==> 😇")
        print("-------------------------------")
        print("You are using release: \033[92mv", vnum, "\033[0m", sep="")
        print("The latest release is: \033[92m" + latest_version + "\033[0m")
        print(
            "To upgrade to the most recent version run \033[92mpip3 install --update ephemetoot\033[0m"
        )

    except Exception as e:
        print("Something went wrong:")


def schedule(options):

    '''
    Creates and loads a plist file for scheduled running with launchd. If --time flag is used, the scheduled time is set accordingly. Note that this is designed for use on MacOS.
    '''
    try:

        if options.schedule == ".":
            working_dir = os.getcwd()
        else:
            working_dir = options.schedule

        lines = plist.default_file.splitlines()
        lines[7] = "  <string>" + working_dir + "</string>"
        lines[10] = "    <string>" + sys.argv[0] + "</string>"
        lines[12] = "    <string>" + working_dir + "/config.yaml</string>"
        lines[15] = "  <string>" + working_dir + "/ephemetoot.log</string>"
        lines[17] = "  <string>" + working_dir + "/ephemetoot.error.log</string>"

        if options.time:
            lines[21] = "    <integer>" + options.time[0] + "</integer>"
            lines[23] = "    <integer>" + options.time[1] + "</integer>"

        # write out file directly to ~/Library/LaunchAgents
        f = open(
            os.path.join(
              os.path.expanduser("~/Library/LaunchAgents"),
              "ephemetoot.scheduler.plist"
            ),
            mode="w",
        )
        for line in lines:
            if line == lines[-1]:
                f.write(line)
            else:
                f.write(line + "\n")
        f.close()
        sys.tracebacklimit = 0  # suppress Tracebacks
        # unload any existing file (i.e. if this is an update to the file) and suppress any errors
        subprocess.run(
            ["launchctl unload ~/Library/LaunchAgents/ephemetoot.scheduler.plist"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        # load the new file
        subprocess.run(
            ["launchctl load ~/Library/LaunchAgents/ephemetoot.scheduler.plist"],
            shell=True,
        )
        print("⏰ Scheduled!")
    except Exception as e:
        print("🙁 Scheduling failed.", e)

def archive_toot(config, toot):
    # define archive path
    if config["archive"][0] == "~":
        archive_path = os.path.expanduser(config["archive"])
    elif config["archive"][0] == "/":
        archive_path = config["archive"]
    else:
        archive_path = os.path.join(os.getcwd(), config["archive"])
    if archive_path[-1] != "/":
        archive_path += "/"

    filename = os.path.join(archive_path, str(toot["id"]) + ".json")

    # write to file
    with open(filename, "w") as f:
        f.write(json.dumps(toot, indent=4, default=jsondefault))
        f.close()

def jsondefault(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()

def tooted_date(toot):
    return toot.created_at.strftime("%d %b %Y")

def datestamp_now():
    return str(
        datetime.now(timezone.utc).strftime(
            "%a %d %b %Y %H:%M:%S %z"
        )
    )

# TODO: move this out of checkToots and pass through all needed arg
# def checkBatch():
#   pass

# TODO: rename to check_toots
def checkToots(config, options, retry_count=0):

    '''
    The main function, uses the Mastodon API to check all toots in the user timeline, and delete any that do not meet any of the exclusion criteria from the config file.
    '''

    keep_pinned = "keep_pinned" in config and config["keep_pinned"]
    toots_to_keep = config["toots_to_keep"] if "toots_to_keep" in config else []
    visibility_to_keep = (
        config["visibility_to_keep"] if "visibility_to_keep" in config else []
    )
    hashtags_to_keep = (
        set(config["hashtags_to_keep"]) if "hashtags_to_keep" in config else set()
    )
    days_to_keep = config["days_to_keep"] if "days_to_keep" in config else 365

    try:
        print(
            "Fetching account details for @"
            + config["username"]
            + "@"
            + config["base_url"]
        )

        # TODO: rename this to check_batch
        def checkBatch(timeline, deleted_count=0):
            for toot in timeline:
                # TODO: move all this into a new testable function process_toot()
                if "id" in toot and "archive" in config:

                    if not options.archive_deleted:
                        # write toot to archive
                        archive_toot(config, toot)

                toot_tags = set()
                for tag in toot.tags:
                    toot_tags.add(tag.name)
                try:
                    if keep_pinned and hasattr(toot, "pinned") and toot.pinned:
                        if not (options.hide_skipped or options.quiet):

                            if options.datestamp:
                                print(datestamp_now(),end=" : ")

                            print("📌 skipping pinned toot -", str(toot.id))

                    elif toot.id in toots_to_keep:
                        if not (options.hide_skipped or options.quiet):

                            if options.datestamp:
                                print(datestamp_now(),end=" : ")

                            print("💾 skipping saved toot -", str(toot.id))

                    elif toot.visibility in visibility_to_keep:
                        if not (options.hide_skipped or options.quiet):

                            if options.datestamp:
                                print(datestamp_now(), end=" : ")

                            print(
                                "👀 skipping",
                                toot.visibility,
                                "toot -",
                                str(toot.id)
                            )

                    elif len(hashtags_to_keep.intersection(toot_tags)) > 0:
                        if not (options.hide_skipped or options.quiet):

                            if options.datestamp:
                                print(datestamp_now(), end=" : ")

                            print(
                              "#️⃣  skipping toot with hashtag -",
                              str(toot.id)
                            )

                    elif cutoff_date > toot.created_at:
                        if hasattr(toot, "reblog") and toot.reblog:
                            if not options.quiet:
                                if options.datestamp:
                                    print(datestamp_now(), end=" : ")

                                print(
                                    "👎 unboosting toot",
                                    str(toot.id),
                                    "boosted",
                                    tooted_date(toot)
                                )

                            deleted_count += 1
                            # unreblog the original toot (their toot), not the toot created by boosting (your toot)
                            if not options.test:
                                if mastodon.ratelimit_remaining == 0:

                                    if not options.quiet:
                                        print("Rate limit reached. Waiting for a rate limit reset")

                                # check for --archive-deleted
                                if (
                                    options.archive_deleted
                                    and "id" in toot
                                    and "archive" in config
                                ):
                                    # write toot to archive
                                    archive_toot(config, toot)
                                mastodon.status_unreblog(toot.reblog)
                        else:
                            if not options.quiet:
                                if options.datestamp:
                                    print(datestamp_now(), end=" : ")

                                print(
                                    "❌ deleting toot", 
                                    str(toot.id), "tooted", 
                                    tooted_date(toot)
                                )

                            deleted_count += 1
                            time.sleep(
                                2
                            )  # wait 2 secs between deletes to be a bit nicer to the server
                            if not options.test:
                                if (
                                    mastodon.ratelimit_remaining == 0
                                    and not options.quiet
                                ):

                                    now = time.time()
                                    diff = mastodon.ratelimit_reset - now

                                    print(
                                        "\nRate limit reached at",
                                        datestamp_now(),
                                        "- next reset due in",
                                        str(format(diff / 60, ".0f")),
                                        "minutes.\n"
                                    )
                                # check for --archive-deleted
                                if (
                                    options.archive_deleted
                                    and "id" in toot
                                    and "archive" in config
                                ):
                                    # write toot to archive
                                    archive_toot(config, toot)

                                mastodon.status_delete(toot)

                except MastodonRatelimitError:

                    now = time.time()
                    diff = mastodon.ratelimit_reset - now

                    print(
                        "\nRate limit reached at "
                        + datestamp_now()
                        + " - waiting for next reset due in "
                        + str(format(diff / 60, ".0f"))
                        + " minutes.\n"
                    )

                    time.sleep(diff + 1)  # wait for rate limit to reset

                except MastodonError as e:

                    def retry_on_error(attempts):

                        if attempts < 6:
                            try:
                                if not options.quiet:
                                    print(
                                        "Attempt "
                                        + str(attempts)
                                        + " at "
                                        + datestamp_now()
                                    )
                                mastodon.status_delete(toot)
                                time.sleep(
                                    2
                                )  # wait 2 secs between deletes to be a bit nicer to the server
                            except:
                                attempts += 1
                                time.sleep(60 * options.retry_mins)
                                retry_on_error(attempts)
                        else:
                            raise TimeoutError("Gave up after 5 attempts")

                    print(
                        "🛑 ERROR deleting toot - "
                        + str(toot.id)
                        + " - "
                        + str(e.args[0])
                        + " - "
                        + str(e.args[3])
                    )
                    if not options.quiet:
                        print(
                            "Waiting "
                            + str(options.retry_mins)
                            + " minutes before re-trying"
                        )
                    time.sleep(60 * options.retry_mins)
                    retry_on_error(attempts=2)

                except KeyboardInterrupt:
                    print("Operation aborted.")
                    break
                except KeyError as e:
                    print(
                        "⚠️  There is an error in your config.yaml file. Please add a value for "
                        + str(e)
                        + " and try again."
                    )
                    break
                except:
                    e = sys.exc_info()

                    print("🛑 Unknown ERROR deleting toot - " + str(toot.id))

                    print("ERROR: " + str(e[0]) + " - " + str(e[1]))

            # the account_statuses call is paginated with a 40-toot limit
            # get the id of the last toot to include as 'max_id' in the next API call.
            # then keep triggering new rounds of checkToots() until there are no more toots to check
            try:
                max_id = timeline[-1:][0].id
                next_batch = mastodon.account_statuses(user_id, limit=40, max_id=max_id)
                if len(next_batch) > 0:
                    checkBatch(next_batch, deleted_count)
                else:
                    if options.test:
                        if options.datestamp:
                            print(
                                "\n\n"
                                + datestamp_now(),
                                end=" : ",
                            )

                        print(
                            "Test run completed. This would have removed "
                            + str(deleted_count)
                            + " toots."
                        )
                    else:
                        if options.datestamp:
                            print(
                                "\n\n"
                                + datestamp_now(),
                                end=" : ",
                            )

                        print("Removed " + str(deleted_count) + " toots.")

                    if not options.quiet:
                        print("\n---------------------------------------")
                        print("🥳 ==> 🧼 ==> 😇 User cleanup complete!")
                        print("---------------------------------------\n")

            except IndexError:
                print("No toots found!")

            except Exception as e:
                print("ERROR: " + str(e.args[0]))

        if options.pace:
            mastodon = Mastodon(
                access_token=config["access_token"],
                api_base_url="https://" + config["base_url"],
                ratelimit_method="pace",
            )

        else:

            mastodon = Mastodon(
                access_token=config["access_token"],
                api_base_url="https://" + config["base_url"],
                ratelimit_method="wait",
            )

        # STARTS HERE
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        user_id = mastodon.account_verify_credentials().id
        account = mastodon.account(user_id)
        timeline = mastodon.account_statuses(user_id, limit=40)

        if not options.quiet:
            print("Checking " + str(account.statuses_count) + " toots")

        checkBatch(timeline)

    except KeyError as val:
        print("\n⚠️  error with in your config.yaml file!")
        print("Please ensure there is a value for " + str(val) + "\n")

    except MastodonAPIError as e:
        if e.args[1] == 401:
            print(
                "\n🙅  User and/or access token does not exist or has been deleted (401)\n"
            )
        elif e.args[1] == 404:
            print("\n🔭  Can't find that server (404)\n")
        else:
            print("\n😕  Server has returned an error (5xx)\n")

    except MastodonNetworkError:
        if retry_count == 0:
            print("\n📡  ephemetoot cannot connect to the server - are you online?")
        if retry_count < 4:
            print("Waiting " + str(options.retry_mins) + " minutes before trying again")
            time.sleep(60 * options.retry_mins)
            retry_count += 1
            print("Attempt " + str(retry_count + 1))
            checkToots(config, options, retry_count)
        else:
            print("Gave up waiting for network\n")
