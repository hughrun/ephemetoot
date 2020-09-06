[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 

**ephemetoot** is a Python command line tool for deleting old toots.

These docs apply to `ephemetoot` version 3.

Note that throughout these docs the `pip` command is referred to as `pip3`. This is to help new Python users on systems running both Python 2 and Python 3, which is currently still common and a frequent source of confusion. On some systems, `pip` will be the appropriate command, as it points to Python 3 environments.

**NOTE:** to install ephemetoot from pypi currently you must pin the beta version:

```
pip3 install ephemetoot==3.0.0-beta.0
```

If you are upgrading from an `ephemetoot` version prior to v3.0.0 please see the [upgrading](./upgrade.md) instructions and note that you need to manually uninstall the old version first.

* [Installation](./install.md)
* [Options](./options.md)
* [Upgrading and uninstalling](./upgrade.md)
* [Contributing](./contributing.md)

## Prior work
The initial `ephemetoot` script was based on [this tweet-deleting script](https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f) by [@flesueur](https://github.com/flesueur)

`ephemetoot` relies heavily on the Mastodon.py package by [@halcy](https://github.com/halcy)

## Usage
You can use `ephemetoot` to delete [Mastodon](https://github.com/tootsuite/mastodon) toots that are older than a certain number of days (default is 365). Toots can optionally be saved from deletion if:
* they are pinned; or
* they include certain hashtags; or
* they have certain visibility; or
* they are individually listed to be kept

## Rate limits
As of Mastodon v2.7.2 the Mastodon API has a rate limit of 30 deletions per 30 minutes. `mastodon.py` automatically handles this. If you are running `ephemetoot` for the first time and/or have a lot of toots to delete, it may take a while as the script will pause when it hits a rate limit, until the required time has expired. You can use the `--pace` flag to slow down ephemetoot so that it never hits the limit - this is recommended on your first run. It will not speed up the process but will smooth it out.

Note that the rate limit is per access token, so using ephemetoot for multiple accounts on the same server shouldn't be a big problem, however one new user may delay action on subsequent accounts in the config file.

## ASCII / utf-8 errors
Prior to Python 3.7, running a Python script on some BSD and Linux systems may throw an error. This can be resolved by:
* setting a _locale_ that encodes utf-8, by using the environment setting `PYTHONIOENCODING=utf-8` when running the script, or 
* upgrading your Python version to 3.7 or higher. See [Issue 11](https://github.com/hughrun/ephemetoot/issues/11) for more information.

## Contributing
For all bugs, suggestions, pull requests or other contributions, please check the [contributing guide](./docs/contributing.md).

## License
This project and all contributions are [licensed](https://github.com/hughrun/ephemetoot/blob/master/LICENSE) under the GPL 3.0 or future version
