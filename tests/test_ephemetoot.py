import datetime
from datetime import timezone
from dateutil.tz import tzutc
import json
import os
import subprocess
import sys

import pytest
import requests

from ephemetoot import ephemetoot


########################
#         MOCKS        #
########################

toot_dict = {
    "id": 104136090490756999,
    "created_at": datetime.datetime(2020, 5, 9, 2, 17, 18, 598000, tzinfo=tzutc()),
    "in_reply_to_id": None,
    "in_reply_to_account_id": None,
    "sensitive": False,
    "spoiler_text": "",
    "visibility": "public",
    "language": "en",
    "uri": "https://example.social/users/testbot/statuses/104136090490756503",
    "url": "https://example.social/@testbot/104136090490756503",
    "replies_count": 0,
    "reblogs_count": 0,
    "favourites_count": 0,
    "favourited": False,
    "reblogged": False,
    "muted": False,
    "bookmarked": False,
    "pinned": True,
    "content": "<p>hello I am testing</p>",
    "reblog": None,
    "application": None,
    "account": {
        "id": 16186,
        "username": "testbot",
        "acct": "testbot",
        "display_name": "ephemtoot Testing Bot",
        "locked": True,
        "bot": True,
        "discoverable": False,
        "group": False,
        "created_at": datetime.datetime(
            2018, 11, 16, 23, 15, 15, 718000, tzinfo=tzutc()
        ),
        "note": "<p>Liable to explode at any time, handle with care.</p>",
        "url": "https://example.social/@testbot",
        "avatar": "https://example.social/system/accounts/avatars/000/016/186/original/66d11c4191332e7a.png?1542410869",
        "avatar_static": "https://example.social/system/accounts/avatars/000/016/186/original/66d11c4191332e7a.png?1542410869",
        "header": "https://example.social/headers/original/header.png",
        "header_static": "https://example.social/headers/original/header.png",
        "followers_count": 100,
        "following_count": 10,
        "statuses_count": 99,
        "last_status_at": datetime.datetime(2020, 8, 17, 0, 0),
        "emojis": [],
        "fields": [
            {"name": "Fully", "value": "Automated", "verified_at": None},
            {"name": "Luxury", "value": "Communism", "verified_at": None},
        ],
    },
    "media_attachments": [
      {
        "id": 123456789987654321,
        "type": "image",
        "url": "https://hugh.run/success/accomplished.jpg"
      }
    ],
    "mentions": [],
    "tags": [],
    "emojis": [],
    "card": None,
    "poll": None,
}

# Turn dict into object needed by mastodon.py
# Use this in tests after making any changes
# you need to your dict object
# NOTE: ensure values in the dict object are what you need:
# it can be mutated by any test before your test runs

def dict2obj(d):
    # checking whether object d is a
    # instance of class list
    if isinstance(d, list):
        d = [dict2obj(x) for x in d]

    # if d is not a instance of dict then
    # directly object is returned
    if not isinstance(d, dict):
        return d

    # declaring a class
    class C:
        pass

    # constructor of the class passed to obj
    obj = C()

    for k in d:
        obj.__dict__[k] = dict2obj(d[k])

    return obj


# here is our toot object - use this in tests
toot = dict2obj(toot_dict)

# config file after being parsed by yaml.safe_load
config_file = {
    "access_token": "abcd_1234",
    "username": "alice",
    "base_url": "test.social",
    "hashtags_to_keep": ["ephemetoot"],
    "days_to_keep": 14,
    "keep_pinned": True,
    "toots_to_keep": [103996285277439262, 103976473612749097, 103877521458738491],
    "visibility_to_keep": [],
    "archive": "archive",
    "archive_media": False
}

# mock GitHub API call for the version number
class MockGitHub:
    @staticmethod
    def json():
        return {"tag_name": "vLATEST_VERSION"}


# mock Mastodon
class Mocktodon:
    def __init__(self):
        return None

    def status_delete(self, t=toot):
        return None

    def status_unreblog(self, t=toot):
        return None

    def ratelimit_remaining(self):
        return 100

    def account_statuses(self, user_id=None, limit=None, max_id=None):
        # create 10 statuses
        # the first 2 will be checked in the first batch (in production it would be 40)
        user_toots = []

        def make_toot(i=1):
            if i < 11:
                keys = ("id", "created_at", "reblog", "tags", "visibility")
                vals = (
                    i,
                    datetime.datetime(2018, 11, i, 23, 15, 15, 718000, tzinfo=tzutc()),
                    False,
                    [],
                    "public",
                )
                user_toot = dict(zip(keys, vals))
                user_toots.append(user_toot)
                total = i + 1
                make_toot(total)

        user_toots.sort(reverse=True)
        make_toot(1)  # make the batch of toots
        # ignore user_id
        # filter for toots with id smaller than max_id
        this_batch = []
        # use dict_to_obj to make a toot for each toot in the obj then a list from that
        this_batch = [dict2obj(t) for t in user_toots if t["id"] > max_id][:limit]
        return this_batch


# mock argparse objects (options)
class Namespace:
    def __init__(
        self,
        archive_deleted=False,
        datestamp=False,
        hide_skipped=False,
        retry_mins=1,
        schedule=False,
        test=False,
        time=False,
        quiet=False,
    ):
        self.archive_deleted = archive_deleted
        self.datestamp = datestamp
        self.schedule = schedule
        self.time = time
        self.test = test
        self.hide_skipped = hide_skipped
        self.quiet = quiet
        self.retry_mins = retry_mins


@pytest.fixture
def mock_github_response(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockGitHub()

    monkeypatch.setattr(requests, "get", mock_get)


########################
#         TESTS        #
########################

# Tests should be listed in alphabetical order
# Remember that a previous test may have mutated
# one of the values above: set all values you are using


def test_archive_toot(tmpdir):
    p = tmpdir.mkdir("archive")
    config_file["archive"] = str(p)  # make archive directory a temp test dir

    ephemetoot.archive_toot(config_file, toot)

    file_exists = os.path.exists(p + "/104136090490756999.json")
    assert file_exists

def test_archive_toot_media(tmpdir):
    p = tmpdir.mkdir("archive")
    config_file["archive"] = str(p)  # make archive directory a temp test dir
    config_file["archive_media"] = True
    ephemetoot.archive_toot_media(p, toot.media_attachments[0].url)
    image_exists = os.path.exists(p + "/hugh.run/success/accomplished.jpg")
    config_file["archive_media"] = False
    assert image_exists

def test_check_batch(capfd, monkeypatch):
    config = config_file
    options = Namespace(archive_deleted=False)
    mastodon = Mocktodon()
    user_id = "test_user_id"
    # limit to 2 so check_batch calls itself for the last 8 toots
    timeline = mastodon.account_statuses(user_id=user_id, limit=2, max_id=0)
    # monkeypatch process_toot to add 1 to deleted_count and return
    # this simulates what would happen if the toot was being deleted
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.process_toot",
        lambda config, options, mastodon, toot, deleted_count: deleted_count + 1,
    )
    # run check_batch
    ephemetoot.check_batch(config, options, mastodon, user_id, timeline, 0)
    # deleted_count should be 10
    output = capfd.readouterr().out.split("\n")
    assert output[0] == "Removed 10 toots for alice@test.social."

def test_check_batch_quiet(capfd, monkeypatch):
    config = config_file
    options = Namespace(archive_deleted=False, quiet=1)
    mastodon = Mocktodon()
    user_id = "test_user_id"
    timeline = mastodon.account_statuses(user_id=user_id, limit=2, max_id=0)
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.process_toot",
        lambda config, options, mastodon, toot, deleted_count: deleted_count + 1,
    )
    ephemetoot.check_batch(config, options, mastodon, user_id, timeline, 0)
    # deleted_count should be 10
    output = capfd.readouterr().out.split("\n")
    assert output[0] == "Removed 10 toots for alice@test.social."

def test_check_batch_quiet_no_toots(capfd, monkeypatch):
    config = config_file
    options = Namespace(archive_deleted=False, quiet=2)
    mastodon = Mocktodon()
    user_id = "test_user_id"
    # max_id is the last toot in our batch so this returns no toots
    timeline = mastodon.account_statuses(user_id=user_id, limit=2, max_id=10)
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.process_toot",
        lambda config, options, mastodon, toot, deleted_count: deleted_count + 1,
    )
    # run check_batch
    ephemetoot.check_batch(config, options, mastodon, user_id, timeline, 0)
    # deleted_count should be 0 but with quiet=2 there should be not output
    output = capfd.readouterr().out
    assert output == ""

def test_check_batch_qq(capfd, monkeypatch):
    config = config_file
    options = Namespace(archive_deleted=False, quiet=2)
    mastodon = Mocktodon()
    user_id = "test_user_id"
    timeline = mastodon.account_statuses(user_id=user_id, limit=2, max_id=0)
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.process_toot",
        lambda config, options, mastodon, toot, deleted_count: deleted_count + 1,
    )
    ephemetoot.check_batch(config, options, mastodon, user_id, timeline, 0)
    # deleted_count should be 10 and message printed since there was a delete
    output = capfd.readouterr().out.split("\n")
    assert output[0] == "Removed 10 toots for alice@test.social."

def test_check_batch_qq_no_deletes(capfd, monkeypatch):
    config = config_file
    options = Namespace(archive_deleted=False, quiet=2)
    mastodon = Mocktodon()
    user_id = "quiet_user_id"
    timeline = mastodon.account_statuses(user_id=user_id, limit=2, max_id=0)
    # simulate no deletes occuring
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.process_toot",
        lambda config, options, mastodon, toot, deleted_count: 0,
    )
    # run check_batch
    ephemetoot.check_batch(config, options, mastodon, user_id, timeline, 0)
    # deleted_count should be 0 with no message since quiet=2
    output = capfd.readouterr().out
    assert output == ""

def test_check_batch_qqq(capfd, monkeypatch):
    config = config_file
    options = Namespace(archive_deleted=False, quiet=3)
    mastodon = Mocktodon()
    user_id = "test_user_id"
    timeline = mastodon.account_statuses(user_id=user_id, limit=2, max_id=0)
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.process_toot",
        lambda config, options, mastodon, toot, deleted_count: deleted_count + 1,
    )
    # run check_batch
    ephemetoot.check_batch(config, options, mastodon, user_id, timeline, 0)
    # deleted_count should be 10 and no message should be printed since quiet=3
    output = capfd.readouterr().out
    assert output == ""

def test_console_print(capfd):
    ephemetoot.console_print(
        "test123", Namespace(test=False, hide_skipped=False, quiet=False), False
    )
    assert capfd.readouterr().out == "test123\n"


def test_console_print_quiet():
    result = ephemetoot.console_print(
        "test123", Namespace(test=False, hide_skipped=False, quiet=True), False
    )
    assert result == None


def test_console_print_skip():
    result = ephemetoot.console_print(
        "test123", Namespace(test=False, hide_skipped=True, quiet=False), True
    )
    assert result == None


def test_datestamp_now():
    datestamp = ephemetoot.datestamp_now()
    date_object = datetime.datetime.strptime(datestamp, "%a %d %b %Y %H:%M:%S %z")
    # use timetuple() to exclude differences in milliseconds
    assert datetime.datetime.now(timezone.utc).timetuple() == date_object.timetuple()


def test_init(monkeypatch, tmpdir):

    # monkeypatch current directory
    current_dir = tmpdir.mkdir("current_dir")  # temporary directory for testing
    monkeypatch.chdir(current_dir)

    # monkeypatch input ...outputs
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.compulsory_input", lambda a, b, c: "compulsory"
    )
    monkeypatch.setattr("ephemetoot.ephemetoot.digit_input", lambda a, b, c: "14")
    monkeypatch.setattr("ephemetoot.ephemetoot.yes_no_input", lambda a, b: "false")
    monkeypatch.setattr(
        "ephemetoot.ephemetoot.optional_input", lambda a, b, c: "optional"
    )

    # run init
    ephemetoot.init()
    assert os.path.exists(os.path.join(current_dir, "config.yaml"))


def test_init_archive_path(tmpdir):

    good_path = tmpdir.mkdir("archive_dir")  # temporary directory for testing
    wrong = ephemetoot.sanitise_input(
        os.path.join(good_path, "/bad/path/"), "Archive path", None
    )
    ok = ephemetoot.sanitise_input(good_path, "Archive path", None)

    assert ok == "ok"
    assert wrong == "That directory does not exist, please try again"


def test_init_sanitise_id_list():
    tags = ("\033[96m", "\033[2m", "\033[0m")
    wrong = ephemetoot.sanitise_input(
        "987654321, toot_id_number", "Toots to keep", tags
    )
    also_wrong = ephemetoot.sanitise_input("toot_id_number", "Toots to keep", tags)
    ok = ephemetoot.sanitise_input("1234598745, 999933335555", "Toots to keep", tags)
    also_ok = ephemetoot.sanitise_input("1234598745", "Toots to keep", tags)

    assert wrong == "Toot IDs must be numeric and separated with commas"
    assert also_wrong == "Toot IDs must be numeric and separated with commas"
    assert ok == "ok"
    assert also_ok == "ok"


def test_init_sanitise_tag_list():
    tags = ("\033[96m", "\033[2m", "\033[0m")
    wrong = ephemetoot.sanitise_input("#tag, another_tag", "Hashtags to keep", tags)
    also_wrong = ephemetoot.sanitise_input("tag, another tag", "Hashtags to keep", tags)
    still_wrong = ephemetoot.sanitise_input("tag, 12345", "Hashtags to keep", tags)
    ok = ephemetoot.sanitise_input("tag123, another_TAG", "Hashtags to keep", tags)
    also_ok = ephemetoot.sanitise_input("single_tag", "Hashtags to keep", tags)

    error = (
        "Hashtags must not include '#' and must match rules at "
        + tags[0]
        + "https://docs.joinmastodon.org/user/posting/#hashtags"
        + tags[2]
    )

    assert ok == "ok"
    assert also_ok == "ok"
    assert wrong == error
    assert also_wrong == error
    assert still_wrong == error


def test_init_sanitise_url():
    tags = ("\033[96m", "\033[2m", "\033[0m")
    wrong = ephemetoot.sanitise_input("http://example.social", "Base URL", tags)
    ok = ephemetoot.sanitise_input("example.social", "Base URL", tags)

    assert (
        wrong
        == "Provide full domain without protocol prefix (e.g. \033[2mexample.social\033[0m, not \033[2mhttp://example.social\033[0m)"
    )
    assert ok == "ok"


def test_init_sanitise_username():
    tags = ("\033[96m", "\033[2m", "\033[0m")
    wrong = ephemetoot.sanitise_input("@alice", "Username", tags)
    ok = ephemetoot.sanitise_input("alice", "Username", tags)

    assert wrong == "Do not include '@' in username, please try again"
    assert ok == "ok"


def test_init_sanitise_visibility_list():
    tags = ("\033[96m", "\033[2m", "\033[0m")
    wrong = ephemetoot.sanitise_input("nonexistent", "Visibility to keep", tags)
    also_wrong = ephemetoot.sanitise_input("direct public", "Visibility to keep", tags)
    ok = ephemetoot.sanitise_input("direct", "Visibility to keep", tags)
    also_ok = ephemetoot.sanitise_input("direct, public", "Visibility to keep", tags)

    error = (
        "Valid values are one or more of 'public', 'unlisted', 'private' or 'direct'"
    )
    assert ok == "ok"
    assert also_ok == "ok"
    assert wrong == error
    assert also_wrong == error


def test_jsondefault():
    d = ephemetoot.jsondefault(toot.created_at)
    assert d == "2020-05-09T02:17:18.598000+00:00"


def test_process_toot(capfd, tmpdir, monkeypatch):
    # config uses config_listed at top of this tests file
    p = tmpdir.mkdir("archive")  # use temporary test directory
    config_file["archive"] = str(p)
    config_file["keep_pinned"] = False
    config_file["toots_to_keep"] = []
    config_file["visibility_to_keep"] = []
    options = Namespace(archive_deleted=False)
    mastodon = Mocktodon()
    toot_dict["pinned"] = False
    toot_dict["visibility"] = "public"
    toot_dict["reblog"] = False
    toot = dict2obj(toot_dict)
    ephemetoot.process_toot(config_file, options, mastodon, toot, 0)
    assert (
        capfd.readouterr().out
        == "❌ deleting toot 104136090490756999 tooted 09 May 2020\n"
    )


def test_process_toot_pinned(capfd, tmpdir):
    # config uses config_listed at top of this tests file
    p = tmpdir.mkdir("archive")  # use temporary test directory
    config_file["archive"] = str(p)
    config_file["keep_pinned"] = True
    options = Namespace(archive_deleted=False)
    mastodon = Mocktodon()
    toot_dict["pinned"] = True
    toot = dict2obj(toot_dict)
    ephemetoot.process_toot(config_file, options, mastodon, toot, 0)
    assert capfd.readouterr().out == "📌 skipping pinned toot - 104136090490756999\n"


def test_process_toot_saved(capfd, tmpdir):
    # config uses config_listed at top of this tests file
    p = tmpdir.mkdir("archive")  # use temporary test directory
    config_file["archive"] = str(p)
    config_file["keep_pinned"] = False
    config_file["toots_to_keep"].append(104136090490756999)
    options = Namespace(archive_deleted=False)
    mastodon = Mocktodon()
    toot_dict["pinned"] = False
    toot = dict2obj(toot_dict)
    ephemetoot.process_toot(config_file, options, mastodon, toot, 0)
    assert capfd.readouterr().out == "💾 skipping saved toot - 104136090490756999\n"


def test_process_toot_visibility(capfd, tmpdir):
    # config uses config_listed at top of this tests file
    p = tmpdir.mkdir("archive")  # use temporary test directory
    config_file["archive"] = str(p)
    config_file["keep_pinned"] = False  # is true above so make false
    config_file["toots_to_keep"].remove(104136090490756999)  # don't keep this toot
    config_file["visibility_to_keep"].append("testing")
    options = Namespace(archive_deleted=False)
    mastodon = Mocktodon()
    toot_dict["pinned"] = False  # is true above so make false
    toot_dict["visibility"] = "testing"
    toot = dict2obj(toot_dict)
    ephemetoot.process_toot(config_file, options, mastodon, toot, 0)
    assert capfd.readouterr().out == "👀 skipping testing toot - 104136090490756999\n"


def test_process_toot_hashtag(capfd, tmpdir, monkeypatch):
    # config uses config_listed at top of this tests file
    p = tmpdir.mkdir("archive")  # use temporary test directory
    config_file["archive"] = str(p)
    config_file["keep_pinned"] = False
    config_file["toots_to_keep"] = []
    config_file["visibility_to_keep"] = []
    options = Namespace(archive_deleted=False)
    mastodon = Mocktodon()
    toot_dict["pinned"] = False
    toot_dict["visibility"] = "public"
    toot_dict["reblog"] = True
    toot = dict2obj(toot_dict)

    ephemetoot.process_toot(config_file, options, mastodon, toot, 0)
    assert (
        capfd.readouterr().out
        == "👎 unboosting toot 104136090490756999 boosted 09 May 2020\n"
    )


def test_retry_on_error():
    # Namespace object constructed from top of tests (representing options)
    # toot comes from variable at top of test
    mastodon = Mocktodon()
    toot = dict2obj(toot_dict)
    retry = ephemetoot.retry_on_error(Namespace(retry_mins=True), mastodon, toot, 5)
    assert retry == None  # should not return an error


def test_retry_on_error_max_tries():
    # Namespace object constructed from top of tests (representing options)
    # toot and mastodon come from objects at top of test
    with pytest.raises(TimeoutError):
        mastodon = Mocktodon()
        toot = dict2obj(toot_dict)
        retry = ephemetoot.retry_on_error(Namespace(retry_mins=True), mastodon, toot, 7)


def test_schedule(monkeypatch, tmpdir):

    home = tmpdir.mkdir("current_dir")  # temporary directory for testing
    launch = tmpdir.mkdir("TestAgents")  # temporary directory for testing

    # monkeypatch directories and suppress the plist loading process
    # NOTE: it may be possible to test the plist loading process
    # but I can't work out how to do it universally / consistently

    def mock_current_dir():
        return str(home)

    def mock_home_dir_expansion(arg):
        return str(launch)

    def suppress_subprocess(args, stdout=None, stderr=None, shell=None):
        return None

    monkeypatch.setattr(os, "getcwd", mock_current_dir)
    monkeypatch.setattr(os.path, "expanduser", mock_home_dir_expansion)
    monkeypatch.setattr(subprocess, "run", suppress_subprocess)

    # now we run the function we're testing
    ephemetoot.schedule(Namespace(schedule=".", time=None))

    # assert the plist file was created
    plist_file = os.path.join(launch, "ephemetoot.scheduler.plist")
    assert os.path.lexists(plist_file)

    # check that correct values were modified in the file
    f = open(plist_file, "r")
    plist = f.readlines()
    assert plist[7] == "  <string>" + str(home) + "</string>\n"
    assert plist[7] == "  <string>" + str(home) + "</string>\n"
    assert plist[10] == "    <string>" + sys.argv[0] + "</string>\n"
    assert plist[12] == "    <string>" + str(home) + "/config.yaml</string>\n"
    assert plist[15] == "  <string>" + str(home) + "/ephemetoot.log</string>\n"
    assert plist[17] == "  <string>" + str(home) + "/ephemetoot.error.log</string>\n"


def test_schedule_with_time(monkeypatch, tmpdir):

    home = tmpdir.mkdir("current_dir")  # temporary directory for testing
    launch = tmpdir.mkdir("TestAgents")  # temporary directory for testing

    # monkeypatch directories and suppress the plist loading process
    # NOTE: it may be possible to test the plist loading process
    # but I can't work out how to do it universally / consistently

    def mock_current_dir():
        return str(home)

    def mock_home_dir_expansion(arg):
        return str(launch)

    def suppress_subprocess(args, stdout=None, stderr=None, shell=None):
        return None

    monkeypatch.setattr(os, "getcwd", mock_current_dir)
    monkeypatch.setattr(os.path, "expanduser", mock_home_dir_expansion)
    monkeypatch.setattr(subprocess, "run", suppress_subprocess)

    # now we run the function we're testing
    ephemetoot.schedule(Namespace(schedule=".", time=["10", "30"]))

    # assert the plist file was created
    plist_file = os.path.join(launch, "ephemetoot.scheduler.plist")
    assert os.path.lexists(plist_file)

    # assert that correct values were modified in the file
    f = open(plist_file, "r")
    plist = f.readlines()

    assert plist[21] == "    <integer>10</integer>\n"
    assert plist[23] == "    <integer>30</integer>\n"


def test_tooted_date():
    string = ephemetoot.tooted_date(toot)
    created = datetime.datetime(2020, 5, 9, 2, 17, 18, 598000, tzinfo=timezone.utc)
    test_string = created.strftime("%d %b %Y")

    assert string == test_string


def test_version(mock_github_response, capfd):
    ephemetoot.version("TEST_VERSION")
    output = capfd.readouterr().out
    msg = """
ephemetoot ==> 🥳 ==> 🧼 ==> 😇
-------------------------------
You are using release: \033[92mvTEST_VERSION\033[0m
The latest release is: \033[92mvLATEST_VERSION\033[0m
To upgrade to the most recent version run \033[92mpip install --upgrade ephemetoot\033[0m\n"""

    assert output == msg
