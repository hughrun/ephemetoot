# Introduction

Thanks for using `ephemetoot`, and for considering contributing to it! Some of the best features have come from suggestions and code contributed by people like you.

You can contribute in many ways - improving the documentation, reporting bugs, suggesting new features, helping test new code, or even writing some code yourself. Following these guidelines will make the process smoother and easier for you and for maintainers and other contributors. That means everyone is happier and improvements get made faster 💫

# Expectations

## Adhere to the Code of Conduct 🤗
All contributors must adhere to the [Code of Conduct](./CODE_OF_CONDUCT.md) for this project. If you do not wish to follow this Code of Conduct, feel free to direct your energies towards a different project.

## Do not log security problems as public issues
If you have identified a security flaw in **ephemetoot**, please email `ephemetoot AT ausglam DOT space` to discuss this confidentially.

## Check existing issues 🧐
Your bug or enhancement might already be listed in the [issues](./issues). It's a good idea to check existing issues before you log your own. If you like someone else's enhancement suggestion, please "upvote" it with a 👍 reaction. If you have also experienced the same bug as someone else, you can add any useful additional context to the existing issue.

## Always log an issue 📝
If you would like to contribute code or documentation changes that do not already have an issue listed, you should always [log an issue](./issues) first. Please **do not add pull requests without prior discussion**. Whilst pull requests are very welcome and encouraged, if you don't log an issue for discussion first, you may end up wasting your time if someone else is already working on the same feature, or maintainers decide it isn't a good fit. This also allows for your proposed feature to be scoped before you get too deep in the weeds coding it.

Regardless of whether is is a bug report, feature request or code proposal, provide as much detail as possible in your issue, and give it a clear name. 

## One issue per bug or suggestion ☝️
Each issue should refer to a single bug or enhancement. Don't include multiple suggestions, or a mix of bug report and enhancement proposal, in a single issue. Multiple items in the one issue ticket will make it confusing to know when to close an issue, and means that maintainers will probably have to create new issues so that each task can be tracked properly. It also makes it hard to maintain a clear discussion thread in the issue if there are multiple things being discussed. 

## Issue and commit naming conventions ✏️

**Issues** should have clear names that describe the problem or the proposed enhancement. Past examples of good issue titles are:

- "Ephemetoot may die when encountering utf8 encoded toots" ([bug](https://github.com/hughrun/ephemetoot/issues/11))
- "Optionally include datetime stamp with every action" ([enhancement](https://github.com/hughrun/ephemetoot/issues/23))

**Commit messages** should start with an [imperative verb](https://www.grammarly.com/blog/imperative-verbs/). Simple commits such as documentation fixes may only need a brief sentence. Something bigger like an enhancement should usually have a commit heading briefly describing the outcome of the commit, with a longer explanation underneath. Past examples of good commit titles are:

- "handle IndexError when there are no toots in the timeline" ([bugfix](https://github.com/hughrun/ephemetoot/commit/92643271d53e00089a10bacd1795cfd50e030413))
- "add support for archiving toots into JSON files" ([new feature](https://github.com/hughrun/ephemetoot/commit/c0d680258ff0fe141fbabcf14a60eee8994e8d18))

## Closing issues in pull requests 🏁

When your pull request resolves an issue, you can optionally use [one of the magic words](https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword) to automatically close the issue. An example of a longer commit messages that does this is [`Add --version flag`](https://github.com/hughrun/ephemetoot/commit/a1db933bbd6c03e633975463801e6c94f7b9e9fa). The pull request template includes wording for this so you just need to add the issue number.

## Use 'black' code formatting standards 🖤

We use [black](https://pypi.org/project/black/) to maintain code formatting consistency. Thanks to [@MarkEEaton](https://github.com/MarkEEaton) for the suggestion. You should generally run `black .` in the main **ephemetoot** directory before making a pull request, or alternatively check that your code is formatted to the `black` standards. Maintainer [@hughrun](https://github.com/hughrun) often forgets to run `black` so logging an issue about code formatting is completely legitimate 😀

## prefer configuration over flags ⚙️
When adding a new feature, you should probably use a new, _optional_ value in the configuration file, rather than a new command line flag. As a general rule of thumb, use a flag when your change will affect the _output_, and a config value when it will affect the _actions_. 

For example, we use a configuration file boolean value for `keep_pinned` because that affects the _actions_ - if it is set to "true" then pinned toots are not deleted, and if set to "false", pinned toots _are_ deleted. On the other hand we use the `--datestamp` flag to print a datestamp against each action as it is logged. This doesn't change the action, merely the output to the screen or log file.

There are some exceptions to this general rule (`--test` prevents any real actions, for example), but the exceptions should be rare and reasonably obvious.

# Your first contribution
First time contributors are warmly encouraged! If you have never contributed to a project on GitHub or another public code repository, the **ephemetoot** maintainers can help you through the process.

## Terminology 📙
You can contribute in many ways - even pointing out where the documentation is unclear will be a real help to future users. Already confused by some of the terms here? Check out [First Timers Only](https://www.firsttimersonly.com) for some tips.

## Pull Requests 🤯
"Pull Requests" can be confusing. You can learn how the process works from this free series [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github).

This is a pretty small project so there usually won't be a lot of issues waiting for someone to work on, but keep an eye out for anything tagged `good first issue` - these are especially for you!

# Help

You can get in touch with Hugh at [@hugh@ausglam.space](https://ausglam.space/@hugh) if you need help contributing or want to discuss something about **ephemetoot**.