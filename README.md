# 🥳 ==> 🧼 ==> 😇
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 

**ephemetoot** is a Python command line tool for deleting old toots.

# Prior work
The initial `ephemetoot` script was based on [this tweet-deleting script](https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f) by [@flesueur](https://github.com/flesueur)

`ephemetoot` relies heavily on the Mastodon.py package by [@halcy](https://github.com/halcy)

# Usage

You can use `ephemetoot` to delete [Mastodon](https://github.com/tootsuite/mastodon) toots that are older than a certain number of days (default is 365). Toots can optionally be saved from deletion if:
* they are pinned; or
* they include certain hashtags; or
* they have certain visibility; or
* they are individually listed to be kept

As of version 2, `ephemetoot` can be used for multiple accounts. If you have several 'alts', this can be useful. If you don't have your own server or Mac computer, your friend can now add you to their `ephemetoot` config and it will take care of your old toots as well as theirs. However, **note [the warning below](#obtain-an-access-token)**.

# Setup & Installation

## Install Python 3 and pip

You need to [install Python 3](https://wiki.python.org/moin/BeginnersGuide/Download) to use `ephemetoot`. Python 2 is now end-of-life, however it continued to be installed as the default Python on MacOS and many Linux distributions until very recently, so you should check. You will also need to check that `pip` is installed and pointing to Python3 (not Python2). On some systems this will mean using the command `pip3`.

## Install ephemetoot
### Option 1 - get code with git
If you already have `git` installed on the machine where you're running ephemetoot, you can download the latest release with:
```shell
git clone https://github.com/hughrun/ephemetoot.git
cd ephemetoot
git checkout [tagname]
```
### Option 2 - get the code by downloading the zip file 
If you don't have `git` or don't want to use it, you can download the zip file by clicking the green button above and selecting `Download ZIP`. You will then need to unzip the file into a new directory where you want to run it.

### install using pip
From a command line, move into the main `ephemetoot` directory (i.e. where the README file is) and run:
```shell
pip install .
```
With some Python 3 installations (e.g on MacOS with Homebrew) you may need to use:
```shell
pip3 install .
```
If you do not have permission to install python modules, you may need to use the `--user` flag:
```shell
pip install . --user
```
Note that you will need to run the script with the same user as ephemetoot will only be installed for that user and not globally.

## Obtain an access token

Now you've installed `ephemetoot`, in order to actually use it you will need an application "access token" from each user. Log in to your Mastodon account using a web browser:

1. Click the `settings` cog
2. Click on `Development`
3. Click `NEW APPLICATION`
4. Enter an application name (e.g. 'ephemetoot'), and give the app both 'read' and 'write' Scopes
5. Click `SUBMIT`
6. Click on the name of the new app, which should be a link
7. Copy the `Your access token` string


**NOTE**: Anyone who has your access token and the domain name of your Mastodon server will be able to:
* read all your private and direct toots, 
* publish toots and DMs, and 
* delete everything in your account.  

**Do not share your access token with anyone you do not 100% trust!!!**.

## Configuration file

As of version 2, you can use a single `ephemetoot` installation to delete toots from multiple accounts. Configuration for each user is set up in the `config.yaml` file. This uses [yaml syntax](https://yaml.org/spec/1.2/spec.html) and can be updated at any time without having to reload `ephemetoot`.

Copy `example-config.yaml` to a new file called `config.yaml`:
```shell
cp example-config.yam config.yaml
```
You can now enter the configuration details for each user:

| setting | description   |
| ---:  |   :---        |
| access_token | **required** - The alphanumeric access token string from the app you created in Mastodon |
| username | **required** - Your username without the '@' or server domain. e.g. `hugh`|
| base_url | **required** - The base url of your Mastodon server, without the 'https://'. e.g. `ausglam.space`|
| days_to_keep | Number of days to keep toots e.g. `30`. If not value is provided the default number is 365 |
| keep_pinned | Either `true` or `false` - if `true`, any pinned toots will be kept regardless of age |
| toots_to_keep | A list of toot ids indicating toots to be kept regardless of other settings. The ID of a toot is the last part of its individual URL. e.g. for [https://ausglam.space/@hugh/101294246770105799](https://ausglam.space/@hugh/101294246770105799) the id is `101294246770105799` |
| hashtags_to_keep | A list of hashtags, where any toots with any of these hashtags will be kept regardless of age. Do not include the '#' symbol. Do remember the [rules for hashtags](https://docs.joinmastodon.org/user/posting/#hashtags) |
| visibility_to_keep | Toots with any of the visibility settings in this list will be kept regardless of age. Options are: `public`, `unlisted`, `private`, `direct`. |
| archive | A string representing the filepath to your toot archive. If this is provided, for every toot checked, the full toot is archived into individual files named by the toot's `id` in this writeable directory. Note that the default is for **all** toots to be archived, not just those that are being deleted. It is generally best to use an absolute file path - relative paths will not work if you call `ephemetoot` from another directory. |

All values other than `access_token`, `username` and `base_url` are optional, however if you include `toots_to_keep`, `hashtags_to_keep`, or `visibility_to_keep` you must make each a list, even if it is empty:

```yaml
toots_to_keep: # this is not a list, it will throw an error
hashtags_to_keep: 
  - # this empty list is ok
visibility_to_keep: [ ] # this empty list is also ok
```

If you want to use `ephemetoot` for multiple accounts, separate the config for each user with a single dash (`-`), as shown in the example file.

# Running the script

For a short description of all available options, run `ephemetoot --help` from the command line.

It is **strongly recommended** that you do a test run before using `ephemetoot` live. There is no "undo"!

## Running in test mode (--test)

To do a test-run without actually deleting anything, run the script with the `--test` flag:
```shell
ephemetoot --test
```

## Running in "live" mode

To call the script call ephemetoot with no arguments:
```shell
ephemetoot
```

Depending on how many toots you have and how long you want to keep them, it may take a minute or two before you see any results.

## Specifying the config location (--config)

By default ephemetoot expects there to be a config file called `config.yaml` in the directory from where you run the `ephemetoot` command. If you want to call it from elsewhere (e.g. with `cron`), you need to specify where your config file is:

```shell
ephemetoot --config '~/directory/subdirectory/config.yaml'
```

## Slow down deletes to match API limit (--pace)

With the `--pace` flag, delete actions are slowed so that the API limit is never reached, using [`Mastodon.py`'s 'pace' method](https://mastodonpy.readthedocs.io/en/stable/index.html?highlight=pace#mastodon.Mastodon.__init__). This is recommended for your first run, as unless you have tooted fewer than 30 times you are guaranteed to hit the API limit for deletions the first time you run `ephemetoot`. If you do not toot very often on most days, it is probably more efficient to use the default behaviour for daily runs after the first time, but you can use `--pace` every time if you prefer.

## Do more

### Include datestamp with every action (--datestamp)

If you want to know exactly when each delete action occured, you can use the `--datestamp` flag to add a datestamp to the log output. This is useful when using `--pace` so you can see the rate you have been slowed down to.

## Do less

### Hide skipped items (--hide_skipped)

If you skip a lot of items (e.g. you skip direct messages) it may clutter your log file to list these every time you run the script. You can suppress them from the output by using the `--hide_skipped` flag.

### Hide everything (--quiet)

Use the `--quiet` flag to suppress all logging except for the account name being checked and the number of toots deleted. Exception messages will not be suppressed.

### Only archive deleted toots (--archive-deleted)

If you provide a value for `archive` in your config file, the default is that all toots will be archived in that location, regardless of whether or not it is being deleted. i.e. it will create a local archive of your entire toot history. If you run ephemetoot with the `--test` flag, this allows you to use create an archive without even deleting anything.

You can use the `--archive-deleted` flag to only archive deleted toots instead.

## Combining flag options

You can use several flags together:
```shell
ephemetoot --config 'directory/config.yaml' --test --hide_skipped
```
Use them in any order:
```shell
ephemetoot --pace --datestamp --config 'directory/config.yaml'
```
Instead of coming back to this page when you forget the flags, you can just use the help option:
```shell
ephemetoot --help
```

## Scheduling

Deleting old toots daily is the best approach to keeping your timeline clean and avoiding problems with the API rate limit.

### Linux and FreeBSD/Unix

To run automatically every day on a n*x server you could try using crontab:

  1. `crontab -e`
  2. enter a new line: `@daily /path/to/ephemetoot --config /path/to/ephemetoot/config.yaml`
  3. exit with `:qw` (Vi/Vim) or `Ctrl + x` (nano)

### MacOS

On **MacOS** you can use the `--schedule` flag to schedule a daily job with [launchd](https://www.launchd.info/). Note that this feature has not been widely tested so **please log an issue if you notice anything go wrong**.

Run from within your `ephemetoot` directory:
```shell
ephemetoot --schedule
``` 
 or from anywhere else run: 
```shell
ephemetoot --schedule directory
``` 
where `directory` is where you installed `ephemetoot`.  
For example if `ephemetoot` is saved to `/User/hugh/python/ephemetoot`:
```shell
ephemetoot --schedule /User/hugh/python/ephemetoot
```

By default, `ephemetoot` will run at 9am every day (as long as your machine is logged in and connected to the internet). You can change the time it is scheduled to run, using the `--time` flag with `--schedule`:
```shell
ephemetoot --schedule [directory] --time hour minute
``` 
For example to run at 2.25pm every day:
```shell
ephemetoot --schedule --time 14 25
``` 

## Rate limits

As of v2.7.2 the Mastodon API has a rate limit of 30 deletions per 30 minutes. `mastodon.py` automatically handles this. If you are running `ephemetoot` for the first time and/or have a lot of toots to delete, it may take a while as the script will pause when it hits a rate limit, until the required time has expired. You can use the `--pace` flag to slow down ephemetoot so that it never hits the limit - this is recommended on your first run. It will not speed up the process but will smooth it out.

Note that the rate limit is per access token, so using ephemetoot for multiple accounts on the same server shouldn't be a big problem, however one new user may delay action on subsequent accounts in the config file.

# ASCII / utf-8 errors

Prior to Python 3.7, running a Python script on some BSD and Linux systems may throw an error. This can be resolved by:
* setting a _locale_ that encodes utf-8, by using the environment setting `PYTHONIOENCODING=utf-8` when running the script, or 
* upgrading your Python version to 3.7 or higher. See [Issue 11](https://github.com/hughrun/ephemetoot/issues/11) for more information.  

# Upgrading

## Upgrading with git
To upgrade to a new version using git, run the following from inside the `ephemetoot` directory:

```shell
git fetch --tags
git checkout [tagname]
pip install .
```

## Upgrading with a ZIP file
To upgrade without using git:

* put your config file somewhere safe
* download and unzip the zip file into your `ephemetoot` directory over the top of your existing installation
* move your config file back in to the ephemetoot directory
* run `pip install .` from within the directory

# Uninstalling

Uninstall using pip:
```shell
pip uninstall ephemetoot
```

If you scheduled a `launchd` job on MacOS using `--schedule`, you will also need to unload and remove the scheduling file:
```shell
launchctl unload ~/Library/LaunchAgents/ephemetoot.scheduler.plist
rm ~/Library/LaunchAgents/ephemetoot.scheduler.plist
```

# Contributing

For all bugs, suggestions, pull requests or other contributions, please check the [contributing guide](./contributing.md).

# License

This project is [licensed](./LICENSE) under the GPL 3.0 or future version
