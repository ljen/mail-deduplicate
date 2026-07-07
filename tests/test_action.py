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
from unittest.mock import MagicMock, patch

from mail_deduplicate.action import Action, move_mails
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


def test_move_mails():
    """Test move_mails action."""
    dedup = MagicMock()
    dedup.conf = {"export": "/path/to/export", "dry_run": False}
    dedup.stats = {Stat.MAIL_MOVED: 0}

    source_box = MagicMock()
    dedup.sources = {"/path/to/source": source_box}

    mail1 = MagicMock()
    mail1.source_path = "/path/to/source"
    mail1.mail_id = "id1"

    mail2 = MagicMock()
    mail2.source_path = "/path/to/source"
    mail2.mail_id = "id2"

    mails = [mail1, mail2]

    with patch("mail_deduplicate.action.export_box") as mock_export_box:
        box_mock = MagicMock()
        mock_export_box.return_value.__enter__.return_value = box_mock

        move_mails(dedup, mails)

        assert dedup.stats[Stat.MAIL_MOVED] == 2
        assert box_mock.add.call_count == 2
        box_mock.add.assert_any_call(mail1)
        box_mock.add.assert_any_call(mail2)

        source_box.remove.assert_any_call("id1")
        source_box.remove.assert_any_call("id2")


def test_move_mails_dry_run():
    """Test move_mails action in dry-run mode."""
    dedup = MagicMock()
    dedup.conf = {"export": "/path/to/export", "dry_run": True}
    dedup.stats = {Stat.MAIL_MOVED: 0}

    source_box = MagicMock()
    dedup.sources = {"/path/to/source": source_box}

    mail1 = MagicMock()
    mail1.source_path = "/path/to/source"
    mail1.mail_id = "id1"

    mail2 = MagicMock()
    mail2.source_path = "/path/to/source"
    mail2.mail_id = "id2"

    mails = [mail1, mail2]

    with patch("mail_deduplicate.action.export_box") as mock_export_box:
        box_mock = MagicMock()
        mock_export_box.return_value.__enter__.return_value = box_mock

        move_mails(dedup, mails)

        assert dedup.stats[Stat.MAIL_MOVED] == 2
        assert box_mock.add.call_count == 0
        assert source_box.remove.call_count == 0
