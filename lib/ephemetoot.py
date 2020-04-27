from datetime import datetime, timedelta, timezone
import json
from mastodon import Mastodon, MastodonError, MastodonAPIError, MastodonNetworkError
import os
import requests
import subprocess
import sys
import time

def schedule(options):
    try:
        with open(options.schedule + '/ephemetoot.scheduler.plist', 'r') as file:
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
        with open('ephemetoot.scheduler.plist', 'w') as file:
            file.writelines(lines)

        sys.tracebacklimit = 0 # suppress Tracebacks
        # save the plist file into ~/Library/LaunchAgents
        subprocess.run(
            ["cp " + options.schedule + "/ephemetoot.scheduler.plist" + " ~/Library/LaunchAgents/"],
            shell=True
        )
        # unload any existing file (i.e. if this is an update to the file) and suppress any errors
        subprocess.run(
            ["launchctl unload ~/Library/LaunchAgents/ephemetoot.scheduler.plist"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            shell=True
        )
        # load the new file and suppress any errors
        subprocess.run(
            ["launchctl load ~/Library/LaunchAgents/ephemetoot.scheduler.plist"],
            shell=True
        )
        print('⏰ Scheduled!')
    except Exception:
        print('🙁 Scheduling failed.')

def checkToots(config, options, retry_count=0):

    print("Fetching account details for @" + config['username'] + "@" + config['base_url'] + "...")
    try:
        def checkBatch(timeline, deleted_count=0):
            for toot in timeline:
                toot_tags = set()
                for tag in toot.tags:
                    toot_tags.add(tag.name)
                try:
                    if config['keep_pinned'] and hasattr(toot, "pinned") and toot.pinned:
                        print("📌 skipping pinned toot - " + str(toot.id))
                    elif toot.id in config['toots_to_keep']:
                        print("💾 skipping saved toot - " + str(toot.id))
                    elif toot.visibility in config['visibility_to_keep']:
                        print("👀 skipping " + toot.visibility + " toot - " + str(toot.id))
                    elif len(config['hashtags_to_keep'].intersection(toot_tags)) > 0:
                        print("#️⃣  skipping toot with hashtag - " + str(toot.id))
                    elif cutoff_date > toot.created_at:
                        if hasattr(toot, "reblog") and toot.reblog:
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
                                        "Rate limit reached. Waiting for a rate limit reset..."
                                    )
                                mastodon.status_unreblog(toot.reblog)
                        else:
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
                                    print(
                                        "Rate limit reached. Waiting for a rate limit reset..."
                                    )
                                mastodon.status_delete(toot)
                except MastodonError as e:
                    print("🛑 ERROR deleting toot - " + str(toot.id) + " - " + e.args[3])
                    print("Waiting 1 minute before re-trying...")
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
                except Exception as e:
                    print("🛑 Unknown ERROR deleting toot - " + str(toot.id))
                    print(e)

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
                        print(
                            "Test run completed. This would have removed "
                            + str(deleted_count)
                            + " toots."
                        )
                    else:
                        print("Removed " + str(deleted_count) + " toots.")

                    print('')
                    print('---------------------------------------')
                    print('🥳 ==> 🧼 ==> 😇 User cleanup complete!')
                    print('---------------------------------------')

            except IndexError:
                print("No toots found!")
        
        mastodon = Mastodon(
            access_token=config['access_token'],
            api_base_url="https://" + config['base_url'],
            ratelimit_method="wait",
        )

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=config['days_to_keep'])
        user_id = mastodon.account_verify_credentials().id
        account = mastodon.account(user_id)
        timeline = mastodon.account_statuses(user_id, limit=40)

        print("Checking " + str(account.statuses_count) + " toots...")

        checkBatch(timeline)

    except MastodonAPIError:
        print('User and/or access token does not exist or has been deleted')
    except MastodonNetworkError:
        print('ephemetoot cannot connect to the server - are you online?')
        if retry_count < 4:
            print('Waiting 1 minute before trying again')
            time.sleep(60)
            retry_count += 1
            print( 'Attempt ' + str(retry_count + 1) )
            checkToots(config, options, retry_count)
        else:
            print('Gave up waiting for network')