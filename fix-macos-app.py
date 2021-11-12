#!/usr/bin/env python3

import os
import subprocess
import sys


def add_tel_links_block(plist_contents):
    # Insert code at top of dictionary indicating that we can handle tel:
    # links, if it's not already there.
    if 'CFBundleURLSchemes' in plist_contents:
        return(plist_contents)
    tel_links_block = """
        <key>CFBundleURLTypes</key>
        <array>
                <dict>
                        <key>CFBundleTypeRole</key>
                        <string>Viewer</string>
                        <key>CFBundleURLName</key>
                        <string></string>
                        <key>CFBundleURLSchemes</key>
                        <array>
                                <string>tel</string>
                        </array>
                </dict>
        </array>
"""
    splitter = '<dict>'
    before, after = plist_contents.split(splitter, 1)
    plist_contents = before + splitter + tel_links_block + after
    return(plist_contents)


def add_bundle_identifier(plist_contents):
    if 'CFBundleIdentifier' in plist_contents:
        return(plist_contents)
    identifier_block = """
        <key>CFBundleIdentifier</key>
        <string>com.jonathankamens.messagestel</string>
"""
    splitter = '<string>Messages-Tel</string>'
    before, after = plist_contents.split(splitter, 1)
    plist_contents = before + splitter + identifier_block + after
    return(plist_contents)


def main():
    app_path = sys.argv[1]
    plist_path = f'{app_path}/Contents/Info.plist'
    plist_contents = open(plist_path).read()
    plist_contents = add_tel_links_block(plist_contents)
    plist_contents = add_bundle_identifier(plist_contents)
    open(f'{plist_path}.new', 'w').write(plist_contents)
    os.rename(f'{plist_path}.new', plist_path)
    subprocess.run(('codesign', '--force', '--deep', '--sign', '-', app_path),
                   check=True)


if __name__ == '__main__':
    main()
