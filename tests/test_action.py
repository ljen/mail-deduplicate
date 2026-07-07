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
from unittest.mock import MagicMock, Mock

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


def test_delete_mails_dry_run():
    """Test delete_mails with dry_run=True."""
    dedup = MagicMock()
    dedup.stats = {Stat.MAIL_DELETED: 0}
    dedup.conf = {"dry_run": True}

    mail1 = Mock()
    mail1.source_path = "path/to/source1"
    mail1.mail_id = "id1"

    mail2 = Mock()
    mail2.source_path = "path/to/source2"
    mail2.mail_id = "id2"

    source_mock = MagicMock()
    dedup.sources = {"path/to/source1": source_mock, "path/to/source2": source_mock}

    delete_mails(dedup, [mail1, mail2])

    assert dedup.stats[Stat.MAIL_DELETED] == 2
    source_mock.remove.assert_not_called()


def test_delete_mails():
    """Test delete_mails with dry_run=False."""
    dedup = MagicMock()
    dedup.stats = {Stat.MAIL_DELETED: 0}
    dedup.conf = {"dry_run": False}

    mail1 = Mock()
    mail1.source_path = "path/to/source1"
    mail1.mail_id = "id1"

    mail2 = Mock()
    mail2.source_path = "path/to/source2"
    mail2.mail_id = "id2"

    source_mock1 = MagicMock()
    source_mock2 = MagicMock()
    dedup.sources = {"path/to/source1": source_mock1, "path/to/source2": source_mock2}

    delete_mails(dedup, [mail1, mail2])

    assert dedup.stats[Stat.MAIL_DELETED] == 2
    source_mock1.remove.assert_called_once_with("id1")
    source_mock2.remove.assert_called_once_with("id2")
