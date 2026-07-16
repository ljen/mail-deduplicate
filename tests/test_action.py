# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from __future__ import annotations

from string import ascii_lowercase
from unittest.mock import MagicMock

from mail_deduplicate.action import Action, delete_mails
from mail_deduplicate.deduplicate import Stat


def test_action_definitions():
    """Test duplicate action definitions."""
    for action in Action:
        assert isinstance(action.value, str)
        assert set(action.value).issubset(ascii_lowercase + "-")
        assert str(action) == action.value
        assert action.name.lower().replace("_", "-") == action.value

        action_func = action.action_function
        assert action_func is not None
        assert callable(action_func)
        assert action_func.__name__ == action.name.lower()


def test_delete_mails_execute():
    """Test delete_mails action correctly deletes mails in-place."""
    dedup = MagicMock()
    dedup.conf = {"dry_run": False}
    dedup.stats = {Stat.MAIL_DELETED: 0}

    mock_source = MagicMock()
    dedup.sources = {"/path/to/box": mock_source}

    mail1 = MagicMock()
    mail1.source_path = "/path/to/box"
    mail1.mail_id = "1"

    mail2 = MagicMock()
    mail2.source_path = "/path/to/box"
    mail2.mail_id = "2"

    delete_mails(dedup, [mail1, mail2])

    assert dedup.stats[Stat.MAIL_DELETED] == 2
    mock_source.remove.assert_any_call("1")
    mock_source.remove.assert_any_call("2")
    assert mock_source.remove.call_count == 2


def test_delete_mails_dry_run():
    """Test delete_mails action correctly skips deleting mails in-place on dry run."""
    dedup = MagicMock()
    dedup.conf = {"dry_run": True}
    dedup.stats = {Stat.MAIL_DELETED: 0}

    mock_source = MagicMock()
    dedup.sources = {"/path/to/box": mock_source}

    mail1 = MagicMock()
    mail1.source_path = "/path/to/box"
    mail1.mail_id = "1"

    mail2 = MagicMock()
    mail2.source_path = "/path/to/box"
    mail2.mail_id = "2"

    delete_mails(dedup, [mail1, mail2])

    assert dedup.stats[Stat.MAIL_DELETED] == 2
    mock_source.remove.assert_not_called()
