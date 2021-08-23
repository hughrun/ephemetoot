# standard library
from datetime import date, datetime, timedelta, timezone
import json
import os
import re
import urllib.parse
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

        sanitised = sanitise_input(value, name, tags)

        if len(value) > 0 and (sanitised == "ok" or sanitised == None):
            return value
        else:
            if len(value) > 0 and sanitised != None:
                print(sanitised)
            value = ""


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
        value = input(tags[0] + name + tags[1] + "(y or n):" + tags[2])
    return_val = "true" if value == "y" else "false"
    return return_val


def optional_input(tags, name, example):

    incomplete = True
    while incomplete:
        value = input(tags[0] + name + tags[1] + example + tags[2])
        sanitised = sanitise_input(value, name, tags)
        if len(value) > 0 and (sanitised == "ok" or sanitised == None):
            incomplete = False
            return value
        elif len(value) > 0 and sanitised != None:
            print(sanitised)
        else:
            return ""


def sanitise_input(value, input_type, tags):
    """
    Check that data entered when running --init complies with requirements
    """

    if input_type == "Username":
        return (
            "Do not include '@' in username, please try again"
            if value.startswith("@")
            else "ok"
        )

    if input_type == "Base URL":
        error = value.startswith("http") or value.find(".") == -1
        return (
            "Provide full domain without protocol prefix (e.g. "
            + tags[1]
            + "example.social"
            + tags[2]
            + ", not "
            + tags[1]
            + "http://example.social"
            + tags[2]
            + ")"
            if error
            else "ok"
        )

    if input_type == "Toots to keep":
        l = value.split(",")

        def check(s):
            d = s.strip()
            if not d.isdigit():
                return False

        allnum = map(check, l)
        return (
            "Toot IDs must be numeric and separated with commas"
            if False in list(allnum)
            else "ok"
        )

    if input_type == "Hashtags to keep":
        l = value.split(",")

        def check(s):
            d = s.strip()
            if d.isdigit():
                return False
            if not re.fullmatch(r"[\w]+", d, flags=re.IGNORECASE):
                return False

        complies = map(check, l)
        return_string = (
            "Hashtags must not include '#' and must match rules at "
            + tags[0]
            + "https://docs.joinmastodon.org/user/posting/#hashtags"
            + tags[2]
        )
        return return_string if False in list(complies) else "ok"

    if input_type == "Visibility to keep":
        l = value.split(",")
        viz_options = set(["public", "unlisted", "private", "direct"])

        def check(s):
            d = [s.strip().lower()]
            intersects = viz_options.intersection(d)
            if len(intersects) == 0:
                return False

        complies = map(check, l)
        return_string = "Valid values are one or more of 'public', 'unlisted', 'private' or 'direct'"
        return return_string if False in list(complies) else "ok"

    if input_type == "Archive path":
        path = (
            os.path.expanduser(value)
            if len(str(value)) > 0 and str(value)[0] == "~"
            else value
        )
        response = (
            "ok"
            if os.path.exists(path)
            else "That directory does not exist, please try again"
        )
        return response


def init():
    """
    Creates a config.yaml file in the current directory, based on user input.
    """
    try:

        # text colour markers (beginning, example, end)
        tags = ("\033[96m", "\033[2m", "\033[0m")

        print("\nCreate your config.yaml file.\n")
        print(
            "For help check out the docs at ",
            tags[0],
            "ephemetoot.hugh.run",
            tags[2],
            "\n",
            sep="",
        )

        conf_token = compulsory_input(tags, "Access token: ", None)
        conf_user = compulsory_input(
            tags, "Username", "(without the '@' - e.g. alice):"
        )
        conf_url = compulsory_input(tags, "Base URL", "(e.g. example.social):")
        conf_days = digit_input(tags, "Days to keep", "(default 365):")
        conf_pinned = yes_no_input(tags, "Keep pinned toots?")
        conf_keep_toots = optional_input(
            tags, "Toots to keep", "(optional list of IDs separated by commas):"
        )
        conf_keep_hashtags = optional_input(
            tags,
            "Hashtags to keep",
            "(optional list without '#' e.g. mastodon, gardening, cats):",
        )
        conf_keep_visibility = optional_input(
            tags, "Visibility to keep", "(optional list e.g. 'direct'):"
        )
        conf_archive = optional_input(
            tags, "Archive path", "(optional filepath for archive):"
        )

        if len(conf_archive) > 0:
            conf_archive_media = yes_no_input(tags, "Archive media?")

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
                configfile.write("\n  archive_media: " + conf_archive_media)

            configfile.close()

    except Exception as e:
        print(e)


def version(vnum):
    """
    Prints current and latest version numbers to console.
    """

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
            "To upgrade to the most recent version run \033[92mpip install --upgrade ephemetoot\033[0m"
        )

    except Exception as e:
        print("Something went wrong:", e)


def schedule(options):

    """
    Creates and loads a plist file for scheduled running with launchd. If --time flag is used, the scheduled time is set accordingly. Note that this is designed for use on MacOS.
    """
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
                "ephemetoot.scheduler.plist",
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
        if options.verbose:
            print(e)


def archive_toot_media(archive_path, full_url):
    url = urllib.parse.urlparse(full_url)
    (dir_name, file_name) = os.path.split(url.path)
    media_archive_path = os.path.join(archive_path, url.netloc, dir_name[1:])
    media_archive_file_path = os.path.join(media_archive_path, file_name)
    if os.path.isfile(media_archive_file_path):
        return
    os.makedirs(media_archive_path, exist_ok=True)
    r = requests.get(full_url)
    with open(media_archive_file_path, "wb") as f:
        f.write(r.content)


def archive_toot(config, toot):
    archive_media = "archive_media" in config and config["archive_media"]

    # define archive path
    if config["archive"][0] == "~":
        archive_path = os.path.expanduser(config["archive"])
    elif config["archive"][0] == "/":
        archive_path = config["archive"]
    else:
        archive_path = os.path.join(os.getcwd(), config["archive"])
    if archive_path[-1] != "/":
        archive_path += "/"

    filename = os.path.join(archive_path, str(toot.id) + ".json")

    # write to file
    with open(filename, "w") as f:
        f.write(json.dumps(toot, indent=4, default=jsondefault))
        f.close()

    if archive_media and "media_attachments" in toot:
        for media_attachment in toot["media_attachments"]:
            if "url" in media_attachment:
                archive_toot_media(archive_path, media_attachment["url"])


def jsondefault(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()


def tooted_date(toot):
    return toot.created_at.strftime("%d %b %Y")


def datestamp_now():
    return str(datetime.now(timezone.utc).strftime("%a %d %b %Y %H:%M:%S %z"))


def console_print(msg, options, skip):

    skip_announcement = True if (options.hide_skipped and skip) else False
    if not (skip_announcement or options.quiet):

        if options.datestamp:
            msg = datestamp_now() + " : " + msg

        print(msg)


def print_rate_limit_message(mastodon):

    now = time.time()
    diff = mastodon.ratelimit_reset - now

    print(
        "\nRate limit reached at",
        datestamp_now(),
        "- next reset due in",
        str(format(diff / 60, ".0f")),
        "minutes.\n",
    )


def retry_on_error(options, mastodon, toot, attempts=0):

    if attempts < 6:
        try:
            console_print(
                "Attempt " + str(attempts) + " at " + datestamp_now(), options, False
            )
            mastodon.status_delete(toot)
        except:
            attempts += 1
            time.sleep(60 * options.retry_mins)
            retry_on_error(options, mastodon, toot, attempts)
    else:
        raise TimeoutError("Gave up after 5 attempts")


def process_toot(config, options, mastodon, toot, deleted_count=0):

    keep_pinned = "keep_pinned" in config and config["keep_pinned"]
    toots_to_keep = config["toots_to_keep"] if "toots_to_keep" in config else []
    visibility_to_keep = (
        config["visibility_to_keep"] if "visibility_to_keep" in config else []
    )
    hashtags_to_keep = (
        set(config["hashtags_to_keep"]) if "hashtags_to_keep" in config else set()
    )
    days_to_keep = config["days_to_keep"] if "days_to_keep" in config else 365
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

    if toot.id and "archive" in config:

        if not options.archive_deleted:
            # write toot to archive
            archive_toot(config, toot)

    toot_tags = set()
    for tag in toot.tags:
        toot_tags.add(tag.name)

    try:
        if keep_pinned and hasattr(toot, "pinned") and toot.pinned:
            console_print("📌 skipping pinned toot - " + str(toot.id), options, True)

        elif toot.id in toots_to_keep:
            console_print("💾 skipping saved toot - " + str(toot.id), options, True)

        elif toot.visibility in visibility_to_keep:
            console_print(
                "👀 skipping " + toot.visibility + " toot - " + str(toot.id),
                options,
                True,
            )

        elif len(hashtags_to_keep.intersection(toot_tags)) > 0:
            console_print(
                "#️⃣  skipping toot with hashtag - " + str(toot.id), options, True
            )

        elif cutoff_date > toot.created_at:
            if hasattr(toot, "reblog") and toot.reblog:
                console_print(
                    "👎 unboosting toot "
                    + str(toot.id)
                    + " boosted "
                    + tooted_date(toot),
                    options,
                    False,
                )

                deleted_count += 1
                # unreblog the original toot (their toot), not the toot created by boosting (your toot)
                if not options.test:
                    if mastodon.ratelimit_remaining == 0:
                        console_print(
                            "Rate limit reached. Waiting for a rate limit reset",
                            options,
                            False,
                        )

                    # check for --archive-deleted
                    if options.archive_deleted and "id" in toot and "archive" in config:
                        # write toot to archive
                        archive_toot(config, toot)

                    mastodon.status_unreblog(toot.reblog)

            else:
                console_print(
                    "❌ deleting toot " + str(toot.id) + " tooted " + tooted_date(toot),
                    options,
                    False,
                )

                deleted_count += 1
                time.sleep(
                    2
                )  # wait 2 secs between deletes to be a bit nicer to the server

                if not options.test:
                    # deal with rate limits
                    if mastodon.ratelimit_remaining == 0 and not options.quiet:
                        print_rate_limit_message(mastodon)

                    # check for --archive-deleted
                    if options.archive_deleted and "id" in toot and "archive" in config:
                        archive_toot(config, toot)

                    # finally we actually delete the toot
                    mastodon.status_delete(toot)

        # return the deleted_count back so that it can be tallied within check_batch()
        return deleted_count

    except MastodonRatelimitError:

        print_rate_limit_message(mastodon)
        time.sleep(diff + 1)  # wait for rate limit to reset

    # If a server goes offline for maintenance etc halfway through a run, we don't necessarily
    # want to just error out. Handling it here allows us to give it time to sort itself out.
    except MastodonError as e:

        if options.verbose:
            print("🛑 ERROR deleting toot -", str(toot.id), "\n", e)
        else:
            print(
                "🛑 ERROR deleting toot -",
                str(toot.id),
                "-",
                str(e.args[0]),
                "-",
                str(e.args[3]),
            )

        console_print(
            "Waiting " + str(options.retry_mins) + " minutes before re-trying",
            options,
            False,
        )
        time.sleep(60 * options.retry_mins)
        retry_on_error(options, mastodon, toot, attempts=2)


def check_batch(config, options, mastodon, user_id, timeline, deleted_count=0):
    """
    Check a batch of up to 40 toots. This is usually triggered by check_toots, and then recursively calls itself until all toots within the time period specified have been checked.
    """

    try:
        for toot in timeline:
            # process_toot returns the value of the deleted_count so we can keep track here
            deleted_count = process_toot(config, options, mastodon, toot, deleted_count)

        # the account_statuses call is paginated with a 40-toot limit
        # get the id of the last toot to include as 'max_id' in the next API call.
        # then keep triggering new rounds of check_toots() until there are no more toots to check
        max_id = timeline[-1:][0].id
        next_batch = mastodon.account_statuses(user_id, limit=40, max_id=max_id)
        if len(next_batch) > 0:
            check_batch(config, options, mastodon, user_id, next_batch, deleted_count)
        else:
            if not options.test:
                if options.datestamp:
                    print("\n", datestamp_now(), end=" : ")

                # options.quiet can be None
                if (
                    (not options.quiet)
                    or options.quiet <= 1
                    or (options.quiet == 2 and deleted_count)
                ):
                    print(
                        "Removed "
                        + str(deleted_count)
                        + " toots for "
                        + config["username"]
                        + "@"
                        + config["base_url"]
                        + ".\n"
                    )

                if not options.quiet:
                    print("---------------------------------------")
                    print("🥳 ==> 🧼 ==> 😇 User cleanup complete!")
                    print("---------------------------------------\n")

            else:

                if options.quiet:
                    if options.datestamp:
                        print("\n", datestamp_now(), sep="", end=" : ")

                    print(
                        "Test run completed. This would have removed",
                        str(deleted_count),
                        "toots.\n",
                    )

                else:
                    print("---------------------------------------")
                    print("🥳 ==> 🧪 ==> 📋 Test run complete!")
                    print("This would have removed", str(deleted_count), "toots.")
                    print("---------------------------------------\n")

    except IndexError:
        if not options.quiet or options.quiet <= 1:
            print(
                "No toots found for "
                + config["username"]
                + "@"
                + config["base_url"]
                + ".\n"
            )


def check_toots(config, options, retry_count=0):
    """
    The main function, uses the Mastodon API to check all toots in the user timeline, and delete any that do not meet any of the exclusion criteria from the config file.
    """
    try:
        if not options.quiet:
            print(
                "Fetching account details for @",
                config["username"],
                "@",
                config["base_url"],
                sep="",
            )

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

        user_id = mastodon.account_verify_credentials().id  # verify user and get ID
        account = mastodon.account(user_id)  # get the account
        timeline = mastodon.account_statuses(user_id, limit=40)  # initial batch

        if not options.quiet:
            print("Checking", str(account.statuses_count), "toots")

        # check first batch
        # check_batch() then recursively keeps looping until all toots have been checked
        check_batch(config, options, mastodon, user_id, timeline)

    except KeyboardInterrupt:
        print("Operation aborted.")

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

        if options.verbose:
            print(e, "\n")

    except MastodonNetworkError as e:
        if retry_count == 0:
            print("\n📡  ephemetoot cannot connect to the server - are you online?")
            if options.verbose:
                print(e)
        if retry_count < 4:
            print("Waiting " + str(options.retry_mins) + " minutes before trying again")
            time.sleep(60 * options.retry_mins)
            retry_count += 1
            print("Attempt " + str(retry_count + 1))
            check_toots(config, options, retry_count)
        else:
            print("Gave up waiting for network\n")

    except Exception as e:
        if options.verbose:
            print("ERROR:", e)
        else:
            print("ERROR:", str(e.args[0]), "\n")
