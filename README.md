A script for deleting old toots.

Based partially on [tweet-deleting script](https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f) by [@flesueur](https://github.com/flesueur)

# Usage

You can use this script to delete [Mastodon](https://github.com/tootsuite/mastodon) toots that are older than a certain number of days. By default it will keep any pinned toots, but you can change `save_pinned` to `False` in `config.py` if you want them to be deleted. You can also make a list toots that you want to save, by adding the ID numbers to the `toots_to_save` list in `config.py` (see point 9 below). The ID of a toot is the last part of its individual URL. e.g. for [https://ausglam.space/@hugh/101294246770105799](https://ausglam.space/@hugh/101294246770105799) the id is `101294246770105799`

This script requires Python3, the `mastodon.py` package and an API access token.

# Setup

1. Install Python3 if you don't already have it (recommended approach is to [use Homebrew](https://docs.brew.sh/Homebrew-and-Python) if you're on MacOS)
2. Install the mastodon package: `pip3 install mastodon.py`
3. Copy _example.config.py_ to a new file called _config.py_ (e.g. `cp example.config.py config.py`)
4. Log in to your Mastodon account using a web browser
    1. Click the settings cog
    2. Click on Development
    3. Click 'NEW APPLICATION'
    4. Enter an application name, and give the app 'read' and 'write' Scopes
    5. Click 'SUBMIT'
    6. Click on the name of the new app
    7. Copy the 'access token' string
5. Replace `YOUR_ACCESS_TOKEN_HERE` in config.py with the access token string
6. Set the `base_url` to match your mastodon server
7. Set the `days_to_keep` to the number of days you want to keep toots before deleting them
8. If you do **not** wish to keep all pinned toots regardless of age, change `save_pinned` to `False`
9. If there are any other toots you want to keep, put the ID numbers (without quotes) in the `toots_to_keep` list, separated by commas. For example:
```python
toots_to_keep = [100029521330725397, 100013562864734780, 100044187305250752]
```
10. If you want to keep toots with a particular hashtag, list each hashtag in the `hashtags_to_keep` set (omitting the `#`):
```python
hashtags_to_keep = {'introduction', 'announcement'}
```
11. You can keep toots with particular visibility (e.g. direct messages) by including that visibility in `visibility_to_keep`. For example the following would only delete public toots:
```python
visibility_to_keep = ['unlisted', 'private', 'direct']
```

# Running the script

## Test mode

To do a test-run without actually deleting anything, run the script with the `--test` flag:
```python
python3 ephemetoot.py --test
```
Depending on how many toots you have and how long you want to keep them, it may take a minute or two before you see any results.

## Live mode

Run the script with no flags:
```python
python3 ephemetoot.py
```

Depending on how many toots you have and how long you want to keep them, it may take a minute or two before you see any results.

## Scheduling

Deleting old toots daily is the best approach to keeping your timeline clean and avoiding problems wiht the API rate limit.

To run automatically every day you could try using crontab:

  1. `crontab -e`
  2. `@daily python3 ~/ephemetoot/ephemetoot.py`

Alternatively on MacOS you could use [launchd](https://www.launchd.info/) or Automator.

## Rate limits

As of v2.7.2 the Mastodon API has a rate limit of 30 deletions per 30 minutes. `mastodon.py` automatically handles this. If you are running `ephemetoot` for the first time and/or have a lot of toots to delete, it may take a while as the script will pause when it hits a rate limit, until the required time has expired.

## ASCII / utf-8 errors

Prior to Python 3.7, running a Python script on some BSD and Linux systems may throw an error. This can be resolved by:
* setting a _locale_ that encodes utf-8, by using the environment setting `PYTHONIOENCODING=utf-8` when running the script, or 
* upgrading your Python version to 3.7 or higher. See [Issue 11](https://github.com/hughrun/ephemetoot/issues/11) for more information.  

# Bugs and suggestions

Please check existing [issues](https://github.com/hughrun/ephemetoot/issues) and if your issue is not already listed, create a new one with as much detail as possible (but don't include your access token!).

# Contributing

Contributions are very welcome, but if you want to suggest any changes or improvements, please log an issue or have a chat to [me on Mastodon](https://ausglam.space/@hugh) _before_ lodging a pull request.

# License

GPL 3.0+
