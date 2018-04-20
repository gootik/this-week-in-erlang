#!/usr/bin/env python3

# This script will pull issues from the upstream "This Week in Erlang"
# and give them an initial formatting.

# Copyright (C) 2018 Mark Allen.
# Licensed under the MIT license
# https://opensource.org/licenses/MIT

import urllib.request
import json
import pprint

# TODO: Clean this up.


class TWIEFailure(Exception):
    """This week in Erlang exception type"""


class TWIEBadIssue(Exception):
    """Error while parsing an issue"""


GITHUB_API = "https://api.github.com"
UPSTREAM = "repos/gootik/this-week-in-erlang"

POST_HEADER_TEMPLATE = """
---
layout: post
title: "This Week In Erlang {}"
description: ""
date: {}
tags: [erlang, news]
comments: false
share: true
---
\r\n
"""

POST_INTRO_TEMPLATE = 'Welcome to another "This week in Erlang" newsletter.\r\n\r\n'
CATEGORY_TITLE_TEMPLATE = '### {}\r\n'
CATEGORY_ITEM_TEMPLATE = '- *{}* ([@{}](https://twitter/{})): {} - <{}>\r\n\r\n'
CATEGORY_ITEM_TEMPLATE_NO_AUTHOR = '{} - <{}>\r\n\r\n'

CATEGORY_TO_TITLE = {
    'article': 'Articles and Blog posts',
    'library update': 'Library Updates',
    'OTP': 'OTP Updates',
    'announcement': 'Announcements',
    'event': 'Events and Meetups',
    'employment': 'Employment',
    'misc': 'Other News'
}

TWEET_TEMPLATE = "This week in #Erlang ! Thanks to {}"


def make_get_request(resource):
    return urllib.request.Request("/".join([GITHUB_API, UPSTREAM, resource]))


def parse_issue(issue_json):
    body = issue_json['body']
    r = list(filter(len, body.split('\r\n')))

    return {
        'date': get_value_from_issue_list(r, "DATE", issue_json),
        'author_name': get_value_from_issue_list(r, "AUTHOR NAME", issue_json),
        'author_twitter': get_value_from_issue_list(r, "AUTHOR TWITTER", issue_json),
        'category': get_value_from_issue_list(r, "CATEGORY", issue_json),
        'description': get_value_from_issue_list(r, "DESCRIPTION", issue_json),
        'link': get_value_from_issue_list(r, "LINK", issue_json),
    }


def get_value_from_issue_list(l, section, issue_json):
    section_string = "### " + section

    index = -1
    for i, t in enumerate(l):
        if section_string in t:
            index = i
            break

    if (index + 1 >= len(l) or index == -1) and section not in ["AUTHOR NAME", "AUTHOR TWITTER"]:
        print(issue_json);
        raise TWIEBadIssue(section + " has no value in issue.")    

    if index + 1 < len(l):
        return l[index + 1]
    else:
        return ''


def create_post(date_string, items):
    dashed_date = date_string.replace('/', '-')
    out_file = open('../_posts/' + dashed_date + '.md', 'w+')

    out_file.write(POST_HEADER_TEMPLATE.format(date_string, dashed_date))
    out_file.write(POST_INTRO_TEMPLATE)

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
        if len(item_by_cat[cat]) == 0:
            continue

        out_file.write(CATEGORY_TITLE_TEMPLATE.format(CATEGORY_TO_TITLE[cat]))

        for item in item_by_cat[cat]:
            out_file.write(issue_item_to_md(item))

    out_file.close()


def issue_item_to_md(item):
    if item['author_name'] != '':
        return CATEGORY_ITEM_TEMPLATE.format(
            item['author_name'],
            item['author_twitter'],
            item['author_twitter'],
            item['description'],
            item['link'])
    else:
        return CATEGORY_ITEM_TEMPLATE_NO_AUTHOR.format(
                item['description'],
                item['link'])


def create_tweet(issues):
    authors = list(map(lambda x: '@' + x['author_twitter'], issues))

    return TWEET_TEMPLATE.format(' '.join(authors))


# get all issues list
req = urllib.request.urlopen(make_get_request("issues"))

if req.status != 200:
    raise TWIEFailure(req.info())
else:
    j = json.loads(req.read().decode())

    issues_by_date = {}

    for issue in j:
        try:
            parsed_issue = parse_issue(issue)

            date = parsed_issue['date']

            if date:
                if date not in issues_by_date:
                    issues_by_date[date] = []

                issues_by_date[date].append(parsed_issue)
        except TWIEBadIssue as error:
            print(error)

    for date in issues_by_date:
        create_post(date, issues_by_date[date])
        tweet = create_tweet(issues_by_date[date])
        print("Tweet for {} -- {}".format(date, tweet))
