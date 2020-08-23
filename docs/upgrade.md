# Upgrade or uninstall

## Upgrading

### Upgrading with git
To upgrade to a new version using git, run the following from inside the `ephemetoot` directory:

```shell
git fetch --tags
git checkout [tagname]
pip install .
```

### Upgrading with a ZIP file
To upgrade without using git:

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

* [Installation](./install.md)
* [Options](./options.md)