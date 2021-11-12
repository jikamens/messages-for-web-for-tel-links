#!/usr/bin/env python3

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

import os
import requests
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import subprocess
from subprocess import DEVNULL
import sys
import time

data_dir = os.path.expanduser('~/.messages-tel')


def get_setting(name):
    return(open(f'{data_dir}/{name}').read().strip())


def launch_messages(messages_app, debug_port):
    try:
        requests.get(f'http://127.0.0.1:{debug_port}/')
    except ConnectionError:
        subprocess.run(('gio', 'launch', messages_app), check=True,
                       stdout=DEVNULL, stderr=DEVNULL)
        for i in range(20):
            try:
                requests.get(f'http://127.0.0.1:{debug_port}/')
                return
            except ConnectionError:
                time.sleep(1)
        sys.exit('Failed to launch Messages app')


def find_element_with_timeout(driver, xpath, timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        try:
            return(driver.find_element_by_xpath(xpath))
        except NoSuchElementException:
            time.sleep(1)


def main():
    if len(sys.argv) < 2:
        sys.exit('No "tel:" URL specified on command line')
    url = sys.argv[1]
    if not url.startswith('tel:'):
        sys.exit(f'"{url}" does not look like a "tel:" URL')
    phone_number = url[4:]
    messages_app = get_setting('messages_app')
    debug_port = get_setting('debug_port')
    launch_messages(messages_app, debug_port)
    chrome_options = Options()
    chrome_options.add_experimental_option(
        'debuggerAddress', f'127.0.0.1:{debug_port}')
    driver = webdriver.Chrome(options=chrome_options)
    # This uniconifies the window if it's iconified
    driver.switch_to.window(driver.current_window_handle)
    find_element_with_timeout(driver, '//a[@href="/web/calls"]').click()
    # If we had to wait for the new call button, then that means the app was
    # just launched, so we need to wait a second more for it to finish
    # initializing or the call might not work.
    start = time.time()
    find_element_with_timeout(driver, '//a[@href="/web/calls/new"]').click()
    if time.time() - start > 0.5:
        time.sleep(1)
    number_field = find_element_with_timeout(
        driver, '//input[@placeholder="Type a name or phone number"]')
    number_field.send_keys(phone_number)
    number_field.send_keys(Keys.RETURN)


if __name__ == '__main__':
    main()
