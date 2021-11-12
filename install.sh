#!/usr/bin/env bash

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

install_dir=~/.messages-tel

get_setting() {
    local name="$1"; shift
    if [ -f "$install_dir/$name" ]; then
        cat "$install_dir/$name"
    fi
}

save_setting() {
    local name="$1"; shift
    local value="$1"; shift
    echo "$value" >| "$install_dir/$name"
}

check_python3() {
    if ! python3 -V &>/dev/null; then
        echo "python3 does not appear to be installed and working" 1>&2
        exit 1
    fi
}

check_selenium() {
    if ! python3 -c 'import selenium' 2>/dev/null; then
        echo "The selenium python3 module isn't installed and working" 1>&2
        exit 1
    fi
}
    
get_debug_port() {
    local debug_port="$(get_setting debug_port)"
    if [ -n "$debug_port" ]; then
        echo "$debug_port"
        return
    fi
    # We pick a random port number for security reasons
    while debug_port="$(python3 -c 'import random; print(random.randrange(1025, 65535));')"; do
        if ! netstat -t -n -a | grep LISTEN | grep "$debug_port"; then
            echo "$debug_port"
            return
        fi
    done
}

set_up_chrome() {
    local debug_port="$1"; shift
    local response

    pkill -f -- --user-data-dir=$install_dir/chrome || true

    echo ""
    echo "A Chrome window is about to open. Please select or sign into the"
    echo "Google account associated with your Fi phone number, then Messages"
    echo "for Web should appear. If it doesn't, then something is wrong that"
    echo "this installer doesn't know how to deal with."

    mkdir -p "$install_dir/chrome"
    touch "$install_dir/chrome/First Run"
    google-chrome \
        --no-default-browser-check \
        --user-data-dir=$install_dir/chrome \
        --profile-directory=messages-tel \
        --remote-debugging-port="$debug_port" \
        https://messages.google.com/web/signin &>/dev/null &

    echo ""
    echo -n "Hit Return when Messages for Web is running in the window: "
    read response

    echo ""
    echo "Click the lock on the left side of the URL bar and select 'Site "
    echo "settings'. Make sure that 'Microphone' and 'Notifications' are set "
    echo "to 'Allow'. Close that tab and then click the 'Reload' button if it"
    echo "appears at the top of the Messages tab."
    echo ""
    echo -n "Hit Return when finished: "
    read response

    echo ""
    echo "Near the right side of the URL bar you should see an icon that looks"
    echo "like a computer monitor with a down-pointing arrow on it. Click that"
    echo "icon, then click the 'Install' button in the pop-up that appears."
    echo ""
    echo "NOTE: If you instead see a square with an arrow on it pointing up"
    echo "and to the right, then you've already installed the Messages app,"
    echo "so close the browser window and skip the next step."
    echo ""
    echo -n "Hit Return when finished: "
    read response

    rm -f ~/Desktop/chrome-*messages-tel.desktop

    echo ""
    echo "The Messages app should have just moved into a separate window,"
    echo "and the browser window it was previously in should now have a"
    echo "single empty tab. Close both of them."
    echo ""
    echo -n "Hit Return when finished: "
    read response
}

get_messages_app() {
    local messages_app="$(echo ~/.local/share/applications/chrome-*-messages-tel.desktop)"
    if [ ! -f "$messages_app" ]; then
        echo "Could not find Messages desktop app" 1>&2
        exit 1
    fi
    echo "$messages_app"
}

configure_debug_port() {
    local messages_app="$1"; shift
    local debug_port="$1"; shift
    local cmd="$(sed -n -e 's/^Exec=//p' "$messages_app")"
    local rdp_arg="--remote-debugging-port=$debug_port "
    if expr "$cmd" : ".*$rdp_arg" >/dev/null; then
        return
    fi
    local old_port=$(echo "$cmd" |
                     sed -n -e 's/.*--remote-debugging-port=\([0-9]*\).*/\1/p')
    if [ -n "$old_port" ]; then
        echo "Changing Selenium port from $old_port to $debug_port" 1>&2
        cmd="$(echo "$cmd" |
               sed 's/\(--remote-debugging-port=\)[0-9]*/\1'$debug_port'/')"
        return
    fi
    local newcmd="$(echo "$cmd" |
                    sed 's/-chrome /-chrome --remote-debugging-port='$debug_port' /')"
    if [ "$cmd" = "$newcmd" ]; then
        echo "Internal error, failed to add Selenium port to app command" 1>&2
        exit 1
    fi
    sed -i -e 's|^Exec=.*|Exec='"$newcmd"'|' "$messages_app"
}

install_scripts() {
    sd="$(dirname "$0")"
    cp "$sd/dialer.py" "$install_dir"
    cp "$sd/install.sh" "$install_dir"
    cp "$sd/uninstall.sh" "$install_dir"
    chmod +x "$install_dir"/*.py "$install_dir"/*.sh
}

install_dialer_app() {
    td=/tmp/messages-tel.$$
    tf=$td/messages-tel.desktop
    mkdir $td
    cat > $tf <<EOF
[Desktop Entry]
Encoding=UTF-8
Name=Messages for tel: links dialer
Version=1.0
Type=Application
NoDisplay=true
Exec="$HOME/.messages-tel/dialer.py" %u
Terminal=false
MimeType=x-scheme-handler/tel
EOF
   desktop-file-install --dir=$HOME/.local/share/applications $tf
   rm -rf $td
   gio mime x-scheme-handler/tel messages-tel.desktop
}

main() {
    local response debug_port messages_app
    if [ -d "$install_dir" ]; then
        echo "It appears you've already at least partially installed this." 1>&2
        echo "Hit Return to overwrite your previous installation," 1>&2
        echo -n "or Ctrl-C to abort: "
        read response
    fi
    mkdir -p "$install_dir"
    check_python3
    check_selenium
    debug_port=$(get_debug_port)
    save_setting debug_port "$debug_port"
    set_up_chrome "$debug_port"
    messages_app=$(get_messages_app)
    save_setting messages_app "$messages_app"
    configure_debug_port "$messages_app" "$debug_port"
    install_scripts
    install_dialer_app
    echo -n "Enter a telephone number to test the installation: "
    read response
    xdg-open "tel:response"
    echo "If Messages successfully dialed the number, then you're all set!"
}

main
