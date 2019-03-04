#  #####################################################################
#     Ephemetoot - A script to delete your old toots
#     Copyright (C) 2018  Hugh Rundle
#     Based partially on tweet-deleting script by @flesueur
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

#     You can contact Hugh on Mastodon @hugh@ausglam.space
#     or on Twitter @hughrundle
#     or email hugh [at] hughrundle [dot] net
#  #####################################################################

import config
import json
from mastodon import Mastodon
from datetime import datetime, timedelta, timezone
import click


mastodon = Mastodon(access_token=config.access_token, api_base_url=config.base_url)

cutoff_date = datetime.now(timezone.utc) - timedelta(days=config.days_to_keep)
user_id = mastodon.account_verify_credentials().id
timeline = mastodon.account_statuses(user_id, limit=40)


@click.command()
@click.option("--test", is_flag=True, help="do a test run without deleting any toots")
def checkFlags(test):
    print("Fetching account details...")
    print("Checking " + str(account.statuses_count) + " toots...")
    if test:
        print("This is a test run...")
    checkToots(timeline, test)


def checkToots(timeline, test, deleted_count=0):
    for toot in timeline:
        try:
            if config.save_pinned and hasattr(toot, "pinned") and toot.pinned:
                print("📌 skipping pinned toot - " + str(toot.id))
            elif toot.id in config.toots_to_save:
                print("💾 skipping saved toot - " + str(toot.id))
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
                    mastodon.status_unreblog(toot.reblog)
                else:
                    print(
                        "❌ deleting toot "
                        + str(toot.id)
                        + " tooted "
                        + toot.created_at.strftime("%d %b %Y")
                    )
                    deleted_count += 1
                    if not test:
                        mastodon.status_delete(toot)
        except:
            print("🛑 **error** with toot - " + str(toot.id))

    # the account_statuses call is paginated with a 40-toot limit
    # get the id of the last toot to include as 'max_id' in the next API call.
    # then keep triggering new rounds of checkToots() until there are no more toots to check
    try:
        max_id = timeline[-1:][0].id
        next_batch = mastodon.account_statuses(user_id, limit=40, max_id=max_id)
        if len(next_batch) > 0:
            checkToots(next_batch, test, deleted_count)
        else:
            if test:
                print(
                    "Test run. This would have removed "
                    + str(deleted_count)
                    + " toots."
                )
            else:
                print("Removed " + str(deleted_count) + " toots.")
    except IndexError:
        print("No toots found!")


# trigger from here
if __name__ == "__main__":
    account = mastodon.account(user_id)
    checkFlags()
