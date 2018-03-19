#!/usr/bin/env python3

# This script will pull issues from the upstream "This Week in Erlang"
# and give them an initial formatting.

# Copyright (C) 2018 Mark Allen.
# Licensed under the MIT license
# https://opensource.org/licenses/MIT


# TODO: Clean this up.

class TWIEFailure(Exception):
    """This week in Erlang exception type"""

class TWIEBadIssue(Exception):
    """Error while parsing an issue"""

import urllib.request
import json
import pprint

GITHUB_API="https://api.github.com"
UPSTREAM="repos/gootik/this-week-in-erlang"

POST_HEADER = """
---
layout: post
title: "This Week In Erlang {}"
description: ""
date: {}
tags: [erlang, news]
comments: false
share: true
---
"""

POST_INTRO = """
Welcome to another “This week in Erlang” newsletter.
"""

CATEGORY_ITEM_TEMPLATE = "- *{}* ([@{}](https://twitter/{})): {} - <{}> \r\n\r\n"

CATEGORY_TO_TITLE = {
    'article': 'Articles and Blog posts',
    'library update': 'Library Updates',
    'OTP': 'OTP Updates',
    'announcement': 'Announcements',
    'event': 'Events and Meetups',
    'employment': 'Employment',
    'misc': 'Other News'
}

def make_get_request(resource):
    return urllib.request.Request("/".join([GITHUB_API, UPSTREAM,resource]))

def parse_issue(issue): 
    body = issue['body']
    r = list(filter(len, body.split('\r\n')))

    return {
        'date': get_value_from_issue_list(r, "DATE"),
        'author_name': get_value_from_issue_list(r, "AUTHOR NAME"),
        'author_twitter': get_value_from_issue_list(r, "AUTHOR TWITTER"),
        'category': get_value_from_issue_list(r, "CATEGORY"),
        'description': get_value_from_issue_list(r, "DESCRIPTION"),
        'link': get_value_from_issue_list(r, "LINK"),
    }

def get_value_from_issue_list(l, section):

    section_string = "### " + section

    index = -1;
    for i, t in enumerate(l):
        if section_string in t:
            index = i
            break;

    if index + 1 >= len(l) or index == -1:
        raise TWIEBadIssue(section + " has no value in issue.")    

    return l[index + 1]


def create_post(date, items):
    file = open('../_posts/' + date.replace('/', '-') + '.md', 'w+')

    file.write(POST_HEADER.format(date, date))
    file.write(POST_INTRO)

    item_by_cat = {
        'announcement': [],
        'article': [],
        'library update': [],
        'OTP': [],
        'misc': [],
        'employment': [],
        'event': [],
    }

    for item in items:
        if item['category'] in item_by_cat:
           item_by_cat[item['category']].append(item)
        else:
            item_by_cat['misc'].append(item)

    for cat in item_by_cat: 
        file.write('### {}\r\n'.format(CATEGORY_TO_TITLE[cat]))

        for item in item_by_cat[cat]:
            file.write(issue_item_to_md(item))

    file.close()

def issue_item_to_md(item):
    return CATEGORY_ITEM_TEMPLATE.format(
        item['author_name'], 
        item['author_twitter'], 
        item['author_twitter'], 
        item['description'], 
        item['link'])

# get all issues list
req = urllib.request.urlopen(make_get_request("issues"))

if req.status != 200:
    raise TWIEFailure(req.info())
else:
    j = json.loads(req.read().decode())

    issue_by_date = {}

    for issue in j:
        parsed_issue = parse_issue(issue)

        date = parsed_issue['date']

        if date:
            if date not in issue_by_date:
                issue_by_date[date] = []

            issue_by_date[date].append(parsed_issue)

    for date in issue_by_date:
        create_post(date, issue_by_date[date])

