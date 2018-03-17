#!/usr/bin/env python3

# This script will pull issues from the upstream "This Week in Erlang"
# and give them an initial formatting.

# Copyright (C) 2018 Mark Allen.
# Licensed under the MIT license
# https://opensource.org/licenses/MIT

class TWIEFailure(Exception):
    """This week in Erlang exception type"""

import urllib.request
import json
import pprint

GITHUB_API="https://api.github.com"
UPSTREAM="repos/gootik/this-week-in-erlang"

def make_get_request(resource):
    return urllib.request.Request("/".join([GITHUB_API, UPSTREAM,resource]))

# get all issues list
req = urllib.request.urlopen(make_get_request("issues"))

if req.status != 200:
    raise TWIEFailure(req.info())
else:
    j = json.loads(req.read().decode())
    for issue in j:
        num = issue['number']
        url = issue['comments_url']

        print("Fetching comments for issue {}".format(num))

        req0 = urllib.request.urlopen(url)
        j0 = json.loads(req0.read().decode())
        i = 1
        for comment in j0:
            print("Comment {} on {} by {}: {}".format(i, comment['updated_at'], comment['user']['login'], comment['body']))
            i = i + 1


