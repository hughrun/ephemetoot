# Upgrade or uninstall

## Upgrading

### Upgrading with pypi
To upgrade to a new version, the easiest way is to use pip to download the latest version from pypi (remembering that for your machine you may need to substitute `pip3` for `pip`):

```shell
pip install --upgrade ephemetoot
```

### Upgrading with git
To upgrade to a new version using git, run the following from inside the `ephemetoot` directory:

```shell
git fetch --tags
git checkout [latest-tagname]
pip install .
```

### Upgrading with a ZIP file
To upgrade without using git or pypi:

* put your config file somewhere safe
* download and unzip the zip file into your `ephemetoot` directory over the top of your existing installation
* move your config file back in to the ephemetoot directory
* run `pip install .` from within the directory

## Uninstalling

Uninstall using pip:
```shell
pip uninstall ephemetoot
```

If you scheduled a `launchd` job on MacOS using `--schedule`, you will also need to unload and remove the scheduling file:
```shell
launchctl unload ~/Library/LaunchAgents/ephemetoot.scheduler.plist
rm ~/Library/LaunchAgents/ephemetoot.scheduler.plist
```
---
* [Home](/)
* [Installation](./install.md)
* [Options](./options.md)
* [Contributing](./contributing.md)