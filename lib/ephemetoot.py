from datetime import date, datetime, timedelta, timezone
import json
from mastodon import (
    Mastodon,
    MastodonError,
    MastodonAPIError,
    MastodonNetworkError,
    MastodonRatelimitError,
)
import os
import requests
import subprocess
import sys
import time


def version(vnum):
    try:
        latest = requests.get(
            "https://api.github.com/repos/hughrun/ephemetoot/releases/latest"
        )
        res = latest.json()
        latest_version = res["name"]
        print("\nYou are using ephemetoot Version " + vnum)
        print("The latest release is " + latest_version + "\n")

    except Exception as e:
        print("Something went wrong:")
        print(e)


def schedule(options):
    try:
        with open(options.schedule + "/ephemetoot.scheduler.plist", "r") as file:
            lines = file.readlines()

            if options.schedule == ".":
                working_dir = os.getcwd()

            else:
                working_dir = options.schedule

            lines[7] = "		<string>" + working_dir + "</string>\n"
            lines[10] = "			<string>" + sys.argv[0] + "</string>\n"
            lines[12] = "			<string>" + working_dir + "/config.yaml</string>\n"

        if options.time:
            lines[21] = "			<integer>" + options.time[0] + "</integer>\n"
            lines[23] = "			<integer>" + options.time[1] + "</integer>\n"

        with open("ephemetoot.scheduler.plist", "w") as file:
            file.writelines(lines)

        sys.tracebacklimit = 0  # suppress Tracebacks
        # save the plist file into ~/Library/LaunchAgents
        subprocess.run(
            [
                "cp "
                + options.schedule
                + "/ephemetoot.scheduler.plist"
                + " ~/Library/LaunchAgents/"
            ],
            shell=True,
        )
        # unload any existing file (i.e. if this is an update to the file) and suppress any errors
        subprocess.run(
            ["launchctl unload ~/Library/LaunchAgents/ephemetoot.scheduler.plist"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        # load the new file and suppress any errors
        subprocess.run(
            ["launchctl load ~/Library/LaunchAgents/ephemetoot.scheduler.plist"],
            shell=True,
        )
        print("⏰ Scheduled!")
    except Exception:
        print("🙁 Scheduling failed.")


def checkToots(config, options, retry_count=0):

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
                    if config["archive"][0] == '~':
                        archive_path = os.path.expanduser(config["archive"])
                    elif config["archive"][0] == '/':
                        archive_path = config["archive"]
                    else:
                        archive_path = os.path.join( os.getcwd(), config["archive"] )
                    if archive_path[-1] != '/':
                        archive_path += '/'
                    print(archive_path)
                    filename = os.path.join(archive_path, str(toot["id"]) + ".json")
                    
                    # write toot to archive
                    with open(filename, "w") as f:
                        f.write(json.dumps(toot, indent=4, default=jsondefault))
                        f.close()

                toot_tags = set()
                for tag in toot.tags:
                    toot_tags.add(tag.name)
                try:
                    if keep_pinned and hasattr(toot, "pinned") and toot.pinned:
                        if not options.hide_skipped:
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
                        if not options.hide_skipped:
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
                        if not options.hide_skipped:
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
                        if not options.hide_skipped:
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
                                    print(
                                        "Rate limit reached. Waiting for a rate limit reset"
                                    )
                                mastodon.status_unreblog(toot.reblog)
                        else:
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
                                if mastodon.ratelimit_remaining == 0:

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
                    print(
                        "🛑 ERROR deleting toot - " + str(toot.id) + " - " + str(e.args)
                    )
                    print("Waiting 1 minute before re-trying")
                    time.sleep(60)
                    try:
                        print("Attempting delete again")
                        mastodon.status_delete(toot)
                        time.sleep(
                            2
                        )  # wait 2 secs between deletes to be a bit nicer to the server
                    except Exception as e:
                        print("🛑 ERROR deleting toot - " + str(toot.id))
                        print(e)
                        print("Exiting due to error.")
                        break
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

                    print("")
                    print("---------------------------------------")
                    print("🥳 ==> 🧼 ==> 😇 User cleanup complete!")
                    print("---------------------------------------\n")

            except IndexError:
                print("No toots found!")

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

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        user_id = mastodon.account_verify_credentials().id
        account = mastodon.account(user_id)
        timeline = mastodon.account_statuses(user_id, limit=40)

        print("Checking " + str(account.statuses_count) + " toots")

        checkBatch(timeline)

    except KeyError as val:
        print("\n⚠️  error with in your config.yaml file!")
        print("Please ensure there is a value for " + str(val) + "\n")

    except MastodonAPIError:
        print("\n🙅  User and/or access token does not exist or has been deleted")
    except MastodonNetworkError:
        print("\n📡  ephemetoot cannot connect to the server - are you online?")
        if retry_count < 4:
            print("Waiting 1 minute before trying again")
            time.sleep(60)
            retry_count += 1
            print("Attempt " + str(retry_count + 1))
            checkToots(config, options, retry_count)
        else:
            print("Gave up waiting for network")
