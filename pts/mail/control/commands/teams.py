# Copyright 2013 The Debian Package Tracking System Developers
# See the COPYRIGHT file at the top-level directory of this distribution and
# at http://deb.li/ptsauthors
#
# This file is part of the Package Tracking System. It is subject to the
# license terms in the LICENSE file found in the top-level directory of
# this distribution and at http://deb.li/ptslicense. No part of the Package
# Tracking System, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE file.
"""
Implements all commands which deal with PTS teams.
"""
from __future__ import unicode_literals

from pts.mail.control.commands.base import Command
from pts.mail.control.commands.confirmation import needs_confirmation

from pts.core.models import Team
from pts.core.models import EmailUser
from pts.core.utils import get_or_none


@needs_confirmation
class JoinTeam(Command):
    """
    Command which lets users join an existing public team.
    """
    META = {
        'description': """join-team <team-slug> [<email>]
  Adds <email> to team with the slug given by <team-slug>. If
  <email> is not given, it adds the From address email to the team.
  If the team is not public or it does not exist, a warning is
  returned.""",
        'name': 'join-team',
    }
    REGEX_LIST = (
        r'\s+(?P<team_slug>\S+)(?:\s+(?P<email>\S+))?$',
    )

    def __init__(self, team_slug, email):
        super(JoinTeam, self).__init__()
        self.user_email = email
        self.team_slug = team_slug

    def get_team_and_user(self):
        team = get_or_none(Team, slug=self.team_slug)
        if not team:
            self.error('Team with the slug "{}" does not exist.'.format(
                self.team_slug))
            return
        if not team.public:
            self.error(
                "The given team is not public. "
                "Please contact {} if you wish to join".format(
                    team.owner.main_email))
            return

        email_user, _ = EmailUser.objects.get_or_create(email=self.user_email)
        if email_user in team.members.all():
            self.warn("You are already a member of the team.")
            return

        return team, email_user

    def pre_confirm(self):
        packed = self.get_team_and_user()
        if packed is None:
            return False

        self.reply('A confirmation mail has been sent to ' + self.user_email)
        return True

    def get_command_text(self):
        return super(JoinTeam, self).get_command_text(
            self.team_slug, self.user_email)

    def handle(self):
        packed = self.get_team_and_user()
        if packed is None:
            return
        team, email_user = packed
        team.add_members([email_user])
        self.reply('You have successfully joined the team "{}"'.format(team))
