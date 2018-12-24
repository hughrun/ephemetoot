A script for deleting old toots.
Based partially on tweet-deleting script by @flesueur (https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f)

# Usage

This script requires Python3, the `mastodon.py` package and an API access token.

1. Install Python3 if you don't already have it
2. Install the mastodon package: `pip3 install mastodon.py`
3. Copy example.config.py to a new file called config.py (e.g. `cp example.config.py config.py`)
4. Log in to you Mastodon account
  1. Click the settings cog
  2. Click on Development
  3. Click 'NEW APPLICATION'
  4. Enter an application name, and give the app 'read' and 'write' Scopes
  5. Click 'SUBMIT'
  6. Click on the name of the new app
  7. Copy the 'access token' string
5. Replace `YOUR_ACCESS_TOKEN_HERE` in config.py with the access token string
6. Set the base_url to match your mastodon server
7. Set the `days_to_keep` to the number of days you want to keep toots before deleting them
8. If you do **not** wish to keep all pinned toots regardless of age, change `saved_pinned` to `False`
9. If there are any other toots you want to keep, put the ID numbers (without quotes) in the `toots_to_save` list, separated by commas. For example:
`toots_to_save = [100029521330725397, 100013562864734780, 100044187305250752]`
10. Run the script with `python3 ephemetoot.py`. Depending on how many toots you have and how long you want to keep them, it may take a minute or two before you see any results.
11. To run every day use crontab:
  1. `crontab -e`
  2. `@daily python3 ~/ephemetoot/ephemetoot.py`

# Bugs

Please log an issue with as much detail as possible (but don't include your access token!).

# License

  GPL 3.0+
