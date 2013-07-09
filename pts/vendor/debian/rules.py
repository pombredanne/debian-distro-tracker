# Copyright 2013 The Debian Package Tracking System Developers
# See the COPYRIGHT file at the top-level directory of this distribution and
# at http://deb.li/ptsauthors
#
# This file is part of the Package Tracking System. It is subject to the
# license terms in the LICENSE file found in the top-level directory of
# this distribution and at http://deb.li/ptslicense. No part of the Package
# Tracking System, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE file.

from __future__ import unicode_literals
import re
import requests
from pts.core.utils import get_decoded_message_payload
from pts.vendor.common import PluginProcessingError


def get_keyword(local_part, msg):
    re_accepted_installed = re.compile('^Accepted|INSTALLED|ACCEPTED')
    re_comments_regarding = re.compile(r'^Comments regarding .*\.changes$')

    body = _get_message_body(msg)
    xloop = msg.get_all('X-Loop', ())
    subject = msg.get('Subject', '')
    xdak = msg.get_all('X-DAK', '')
    debian_pr_message = msg.get('X-Debian-PR-Message', '')

    owner_match = 'owner@bugs.debian.org' in xloop

    if owner_match and debian_pr_message.startswith('transcript'):
        return 'bts-control'
    elif owner_match and debian_pr_message:
        return 'bts'
    elif xdak and re_accepted_installed.match(subject):
        if re.search(r'\.dsc\s*$', body, flags=re.MULTILINE):
            return 'upload-source'
        else:
            return 'upload-binary'
    elif xdak or re_comments_regarding.match(subject):
        return 'archive'


def add_new_headers(received_message, package_name, keyword):
    new_headers = [
        ('X-Debian-Package', package_name),
        ('X-Debian', 'PTS'),
    ]
    return new_headers


def approve_default_message(msg):
    return 'X-Bugzilla-Product' in msg


def _get_message_body(msg):
    """
    Returns the message body, joining together all parts into one string.
    """
    return '\n'.join(get_decoded_message_payload(part)
                     for part in msg.walk() if not part.is_multipart())


def get_pseudo_package_list():
    PSEUDO_PACKAGE_LIST_URL = (
        'http://bugs.debian.org/pseudo-packages.maintainers'
    )
    response = requests.get(PSEUDO_PACKAGE_LIST_URL)

    if response.status_code != 200:
        raise PluginProcessingError()
    return [
        line.split(None, 1)[0]
        for line in response.text.splitlines()
    ]


def get_package_information_site_url(package_name,
                                     source_package=False,
                                     repository_name=None):
    """
    Should return a URL to a package information Web page for the given package
    and repository. The repository parameter is optional.

    If no URL exists, returns None
    """
    BASE_URL = 'http://packages.debian.org/'
    SOURCE_PACKAGE_URL_TEMPLATES = {
        'repository': BASE_URL + 'source/{repo}/{package}',
        'no-repository': BASE_URL + 'src:{package}',
    }
    BINARY_PACKAGE_URL_TEMPLATES = {
        'repository': BASE_URL + '{repo}/{package}',
        'no-repository': BASE_URL + '{package}',
    }

    params = {'package': package_name}
    if repository_name:
        url_type = 'repository'
        params['repo'] = repository_name
    else:
        url_type = 'no-repository'

    if source_package:
        template = SOURCE_PACKAGE_URL_TEMPLATES[url_type]
    else:
        template = BINARY_PACKAGE_URL_TEMPLATES[url_type]

    return template.format(**params)
