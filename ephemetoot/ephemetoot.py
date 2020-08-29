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


def init():

    '''
    Creates a config.yaml file in the current directory, based on user input.
    '''

    init_start = "\033[96m"
    init_end = "\033[0m"
    init_eg = "\033[2m"

    conf_token = ""
    while len(conf_token) < 1:
        conf_token = input(init_start + "Access token: " + init_end)

    conf_user = ""
    while len(conf_user) < 1:
        conf_user = input(
            init_start
            + "Username"
            + init_eg
            + "(without the '@' - e.g. alice):"
            + init_end
        )

    conf_url = ""
    while len(conf_url) < 1:
        conf_url = input(
            init_start + "Base URL" + init_eg + "(e.g. example.social):" + init_end
        )

    conf_days = ""
    while conf_days.isdigit() == False:
        conf_days = input(
            init_start + "Days to keep" + init_eg + "(default 365):" + init_end
        )

    conf_keep_pinned = ""
    while conf_keep_pinned not in ["y", "n"]:
        conf_keep_pinned = input(
            init_start + "Keep pinned toots?" + init_eg + "(y or n):" + init_end
        )

    conf_pinned = "true" if conf_keep_pinned == "y" else "false"

    conf_keep_toots = input(
        init_start
        + "Toots to keep"
        + init_eg
        + " (optional list of IDs separated by commas):"
        + init_end
    )

    conf_keep_hashtags = input(
        init_start
        + "Hashtags to keep"
        + init_eg
        + " (optional list separated by commas):"
        + init_end
    )

    conf_keep_visibility = input(
        init_start
        + "Visibility to keep"
        + init_eg
        + " (optional list separated by commas):"
        + init_end
    )

    conf_archive = input(
        init_start
        + "Archive path"
        + init_eg
        + " (optional filepath for archive):"
        + init_end
    )

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


def version(vnum):
    '''
    Prints current and latest version numbers to console.
    '''
    try:
        latest = requests.get(
            "https://api.github.com/repos/hughrun/ephemetoot/releases/latest"
        )
        res = latest.json()
        latest_version = res["name"]
        print("\nephemetoot ==> 🥳 ==> 🧼 ==> 😇")
        print("-------------------------------")
        print("Using:  \033[92mVersion " + vnum + "\033[0m")
        print("Latest: \033[92m" + latest_version + "\033[0m")
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
            os.path.expanduser("~/Library/LaunchAgents/")
            + "ephemetoot.scheduler.plist",
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
        print("🙁 Scheduling failed.")


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

        def jsondefault(obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()

        def checkBatch(timeline, deleted_count=0):
            for toot in timeline:
                if "id" in toot and "archive" in config:

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

                    if not options.archive_deleted:
                        # write toot to archive
                        with open(filename, "w") as f:
                            f.write(json.dumps(toot, indent=4, default=jsondefault))
                            f.close()

                toot_tags = set()
                for tag in toot.tags:
                    toot_tags.add(tag.name)
                try:
                    if keep_pinned and hasattr(toot, "pinned") and toot.pinned:
                        if not (options.hide_skipped or options.quiet):
                            if options.datestamp:
                                print(
                                    str(
                                        datetime.now(timezone.utc).strftime(
                                            "%a %d %b %Y %H:%M:%S %z"
                                        )
                                    ),
                                    end=" : ",
                                )

                            print("📌 skipping pinned toot - " + str(toot.id))
                    elif toot.id in toots_to_keep:
                        if not (options.hide_skipped or options.quiet):
                            if options.datestamp:
                                print(
                                    str(
                                        datetime.now(timezone.utc).strftime(
                                            "%a %d %b %Y %H:%M:%S %z"
                                        )
                                    ),
                                    end=" : ",
                                )

                            print("💾 skipping saved toot - " + str(toot.id))
                    elif toot.visibility in visibility_to_keep:
                        if not (options.hide_skipped or options.quiet):
                            if options.datestamp:
                                print(
                                    str(
                                        datetime.now(timezone.utc).strftime(
                                            "%a %d %b %Y %H:%M:%S %z"
                                        )
                                    ),
                                    end=" : ",
                                )

                            print(
                                "👀 skipping "
                                + toot.visibility
                                + " toot - "
                                + str(toot.id)
                            )
                    elif len(hashtags_to_keep.intersection(toot_tags)) > 0:
                        if not (options.hide_skipped or options.quiet):
                            if options.datestamp:
                                print(
                                    str(
                                        datetime.now(timezone.utc).strftime(
                                            "%a %d %b %Y %H:%M:%S %z"
                                        )
                                    ),
                                    end=" : ",
                                )

                            print("#️⃣  skipping toot with hashtag - " + str(toot.id))
                    elif cutoff_date > toot.created_at:
                        if hasattr(toot, "reblog") and toot.reblog:
                            if not options.quiet:
                                if options.datestamp:
                                    print(
                                        str(
                                            datetime.now(timezone.utc).strftime(
                                                "%a %d %b %Y %H:%M:%S %z"
                                            )
                                        ),
                                        end=" : ",
                                    )

                                print(
                                    "👎 unboosting toot "
                                    + str(toot.id)
                                    + " boosted "
                                    + toot.created_at.strftime("%d %b %Y")
                                )
                            deleted_count += 1
                            # unreblog the original toot (their toot), not the toot created by boosting (your toot)
                            if not options.test:
                                if mastodon.ratelimit_remaining == 0:
                                    if not options.quiet:
                                        print(
                                            "Rate limit reached. Waiting for a rate limit reset"
                                        )
                                # check for --archive-deleted
                                if (
                                    options.archive_deleted
                                    and "id" in toot
                                    and "archive" in config
                                ):
                                    # write toot to archive
                                    with open(filename, "w") as f:
                                        f.write(
                                            json.dumps(
                                                toot, indent=4, default=jsondefault
                                            )
                                        )
                                        f.close()
                                mastodon.status_unreblog(toot.reblog)
                        else:
                            if not options.quiet:
                                if options.datestamp:
                                    print(
                                        str(
                                            datetime.now(timezone.utc).strftime(
                                                "%a %d %b %Y %H:%M:%S %z"
                                            )
                                        ),
                                        end=" : ",
                                    )

                                print(
                                    "❌ deleting toot "
                                    + str(toot.id)
                                    + " tooted "
                                    + toot.created_at.strftime("%d %b %Y")
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
                                        "\nRate limit reached at "
                                        + str(
                                            datetime.now(timezone.utc).strftime(
                                                "%a %d %b %Y %H:%M:%S %z"
                                            )
                                        )
                                        + " - next reset due in "
                                        + str(format(diff / 60, ".0f"))
                                        + " minutes.\n"
                                    )
                                # check for --archive-deleted
                                if (
                                    options.archive_deleted
                                    and "id" in toot
                                    and "archive" in config
                                ):
                                    # write toot to archive
                                    with open(filename, "w") as f:
                                        f.write(
                                            json.dumps(
                                                toot, indent=4, default=jsondefault
                                            )
                                        )
                                        f.close()

                                mastodon.status_delete(toot)

                except MastodonRatelimitError:

                    now = time.time()
                    diff = mastodon.ratelimit_reset - now

                    print(
                        "\nRate limit reached at "
                        + str(
                            datetime.now(timezone.utc).strftime(
                                "%a %d %b %Y %H:%M:%S %z"
                            )
                        )
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
                                        + str(
                                            datetime.now(timezone.utc).strftime(
                                                "%a %d %b %Y %H:%M:%S %z"
                                            )
                                        )
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
                                + str(
                                    datetime.now(timezone.utc).strftime(
                                        "%a %d %b %Y %H:%M:%S %z"
                                    )
                                ),
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
                                + str(
                                    datetime.now(timezone.utc).strftime(
                                        "%a %d %b %Y %H:%M:%S %z"
                                    )
                                ),
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
                "\n🙅  User and/or access token does not exist or has been deleted (401)"
            )
        elif e.args[1] == 404:
            print("\n🔭  Can't find that server (404)")
        else:
            print("\n😕  Server has returned an error (5xx)")

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
            print("Gave up waiting for network")
