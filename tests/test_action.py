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

from mail_deduplicate.action import Action, copy_mails
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


def test_copy_mails():
    """Test copy_mails action behavior."""
    dedup = MagicMock()
    dedup.conf = {"export": "mock_export", "dry_run": False}
    dedup.stats = {Stat.MAIL_COPIED: 0}

    mail1 = MagicMock()
    mail2 = MagicMock()
    mails = [mail1, mail2]

    with patch("mail_deduplicate.action.export_box") as mock_export_box:
        mock_box = MagicMock()
        mock_export_box.return_value.__enter__.return_value = mock_box

        copy_mails(dedup, mails)

        assert mock_box.add.call_count == 2
        mock_box.add.assert_any_call(mail1)
        mock_box.add.assert_any_call(mail2)
        assert dedup.stats[Stat.MAIL_COPIED] == 2


def test_copy_mails_dry_run():
    """Test copy_mails action behavior during a dry run."""
    dedup = MagicMock()
    dedup.conf = {"export": "mock_export", "dry_run": True}
    dedup.stats = {Stat.MAIL_COPIED: 0}

    mail1 = MagicMock()
    mails = [mail1]

    with patch("mail_deduplicate.action.export_box") as mock_export_box:
        mock_box = MagicMock()
        mock_export_box.return_value.__enter__.return_value = mock_box

        copy_mails(dedup, mails)

        # In dry run, box.add shouldn't be called
        mock_box.add.assert_not_called()
        assert dedup.stats[Stat.MAIL_COPIED] == 1
