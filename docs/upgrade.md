# Upgrade or uninstall

## Upgrading

### Note for users upgrading to Version 3

To upgrade from an earlier version to Version 3.x you will need to remove your existing install.

1. save a copy of your `config.yaml` file somewhere safe
2. run `pip3 uninstall ephemetoot`
3. run `pip3 install ephemetoot`
4. check your config file is in the current directory
5. check everything is working with `ephemetoot --test` or `ephemetoot --version`

### Upgrading with pypi
To upgrade to a new version, the easiest way is to use pip to download the latest version from pypi (remembering that for your machine you may need to substitute `pip` for `pip3`):

```shell
pip3 install --upgrade ephemetoot
```

### Upgrading with git
To upgrade to a new version using git, run the following from inside the `ephemetoot` directory:

```shell
git fetch --tags
git checkout [latest-tagname]
pip3 install .
```

### Upgrading with a ZIP file
To upgrade without using git or pypi:

* put your config file somewhere safe
* download and unzip the zip file into your `ephemetoot` directory over the top of your existing installation
* move your config file back in to the ephemetoot directory
* run `pip3 install .` from within the directory

## Uninstalling

Uninstall using pip:
```shell
pip3 uninstall ephemetoot
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