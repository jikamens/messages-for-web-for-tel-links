#!/bin/bash

# Copyright (C) 2021 Jonathan Kamens.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see
# <https://www.gnu.org/licenses/>.

set -e

pkill -f -- --user-data-dir=$HOME/.messages-tel || true
if [ "$(uname)" = "Darwin" ]; then
    rm -rf ~/Applications/Messages-Tel.app
else
    rm -f ~/.local/share/applications/chrome-*-messages-tel.desktop
    rm -f ~/.local/share/applications/messages-tel.desktop
fi

rm -rf ~/.messages-tel

echo "Uninstalled."
