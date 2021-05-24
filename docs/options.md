# Running the script

For a short description of all available options, run `ephemetoot --help` from the command line.

It is **strongly recommended** that you do a test run before using `ephemetoot` live. There is no "undo"!

## Create your config file (--init)

Before you can use `ephemetoot` you need a configuration file. You can create this yourself, but `--init` will walk you through the values you need and save it to `config.yaml` in the directory from which you run the command:

```shell
ephemetoot --init
```

More information about the config file can be found on the _[Installation](./install.md#configuration-file)_ page, and an [example file](https://github.com/hughrun/ephemetoot/blob/master/example-config.yaml) is available on GitHub.

## Run in test mode (--test)

To do a test-run without actually deleting anything, run the script with the `--test` flag:
```shell
ephemetoot --test
```

## Run in "live" mode

To call the script use the command `ephemetoot` without any other arguments:
```shell
ephemetoot
```

Depending on how many toots you have and how long you want to keep them, it may take a minute or two before you see any results.

## Specify the config location (--config)

By default ephemetoot expects there to be a config file called `config.yaml` in the directory from where you run the `ephemetoot` command. If you want to call it from elsewhere (e.g. when using `cron`), you need to specify where your config file is:

```shell
ephemetoot --config '~/directory/subdirectory/config.yaml'
```
## Manage timing

### Slow down deletes to match API limit (--pace)

With the `--pace` flag, delete actions are slowed so that the API limit is never reached, essentially borrowing the 'pace' method from the [`Mastodon.py`](https://mastodonpy.readthedocs.io/en/stable/index.html?highlight=pace#mastodon.Mastodon.__init__) module. This is **recommended for your first run**, as unless you have tooted fewer than 30 times you are guaranteed to hit the API limit for deletions the first time you run `ephemetoot`. If you do not toot very often on most days, it is probably more efficient to use the default behaviour for daily runs after the first time, but you can use `--pace` every time if you prefer.

### Increase the time between retry attempts when encountering errors (--retry-mins)

Use `--retry-mins` to increase the period between attempts to retry deletion after an error. The default value is one (1) minute, but you can make it anything you like. This is useful if your mastodon server is unreliable or frequently in "maintenance mode". `ephemetoot` will make four additional attempts if it encounters an error, so the following command, for example, would wait 20 minutes between each retry, allowing the script to continue if there is an outage of 79 minutes or fewer:

```shell
ephemetoot --retry-mins 20
```

## Do more

### Include datestamp with every action (--datestamp)

If you want to know exactly when each delete action occured, you can use the `--datestamp` flag to add a datestamp to the log output. This is useful when using `--pace` so you can see the rate you have been slowed down to.

### Include full error messages (--verbose)

Sometimes you might get an error and want to know more about what's triggering it. Use the `--verbose` flag to print the full error to the console, instead of just the friendly version.

## Do less

### Hide skipped items (--hide-skipped)

If you skip a lot of items (e.g. you skip direct messages) it may clutter your log file to list these every time you run the script. You can suppress them from the output by using the `--hide-skipped` flag.

### Hide everything (--quiet)

Use the `--quiet` or `-q` flag to suppress all logging except for the account name being checked and the number of toots deleted. Use the `-qq` flag to further suppress output for accounts with zero deleted toots. The `-qqq` flag will suppress all output. Exception messages will not be suppressed, other than `IndexError` when any account has no toots to check.

### Only archive deleted toots (--archive-deleted)

If you provide a value for `archive` in your config file, the default is that all toots will be archived in that location, regardless of whether or not it is being deleted. i.e. it will create a local archive of your entire toot history. If you run ephemetoot with the `--test` flag, this allows you to use create an archive without even deleting anything.

You can use the `--archive-deleted` flag to only archive deleted toots instead.

## Combining flag options

You can use several flags together:
```shell
ephemetoot --config 'directory/config.yaml' --test --hide-skipped
```
Use them in any order:
```shell
ephemetoot --pace  --retry-mins 5 --datestamp --config 'directory/config.yaml'
```

## Scheduling

Deleting old toots daily is the best approach to keeping your timeline clean and avoiding problems with the API rate limit.

### Linux and FreeBSD/Unix

To run automatically every day on a n*x server you could try using crontab:

  1. `crontab -e`
  2. enter a new line: `@daily /path/to/ephemetoot --config /path/to/ephemetoot/config.yaml`
  3. exit with `:qw` (Vi/Vim) or `Ctrl + x` (nano)

### MacOS (--schedule)

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
---
* [Home](index.md)
* [Installation](install.md)
* [Upgrading and uninstalling](upgrade.md)
* [Contributing](contributing.md)
