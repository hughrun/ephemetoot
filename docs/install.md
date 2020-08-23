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

### Complete install with pip
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

---

* [Options](./options.md)
* [Upgrading and uninstalling](./upgrade.md)