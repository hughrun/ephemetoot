# 🥳 ==> 🧼 ==> 😇
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)  

**ephemetoot** is a Python command line tool for deleting old toots.

**NOTE:** to install ephemetoot from pypi currently you must pin the beta version:

```
pip install ephemetoot=3.0.0-beta.0
```

## Documentation
* [Installation](./docs/install.md)
* [Options](./docs/options.md)
* [Upgrading and uninstalling](./docs/upgrade.md)

## Prior work
The initial `ephemetoot` script was based on [this tweet-deleting script](https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f) by [@flesueur](https://github.com/flesueur)

`ephemetoot` relies heavily on the Mastodon.py package by [@halcy](https://github.com/halcy)

## Usage
You can use `ephemetoot` to delete [Mastodon](https://github.com/tootsuite/mastodon) toots that are older than a certain number of days (default is 365). Toots can optionally be saved from deletion if:
* they are pinned; or
* they include certain hashtags; or
* they have certain visibility; or
* they are individually listed to be kept

## Contributing
For all bugs, suggestions, pull requests or other contributions, please check the [contributing guide](./docs/contributing.md).

## License
This project and all contributions are [licensed](./LICENSE) under the GPL 3.0 or future version
