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
import platform
import requests
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import signal
import subprocess
from subprocess import DEVNULL
import sys
import time

data_dir = os.path.expanduser('~/.messages-tel')
sys.stdout = open(f'{data_dir}/dialer.out', 'w', buffering=1)
sys.stderr = sys.stdout


def get_setting(name):
    return(open(f'{data_dir}/{name}').read().strip())


def macos_launch_messages(messages_app):
    subprocess.run(f'{messages_app} &', shell=True, check=True,
                   stdout=DEVNULL, stderr=DEVNULL)


def linux_launch_messages(messages_app):
    subprocess.run(('gio', 'launch', messages_app), check=True,
                   stdout=DEVNULL, stderr=DEVNULL)


def launch_messages(messages_app):
    if platform.system() == 'Darwin':
        macos_launch_messages(messages_app)
    else:
        linux_launch_messages(messages_app)


def get_driver(messages_app, debug_port):
    relaunched = [False]

    try:
        requests.get(f'http://127.0.0.1:{debug_port}/')
    except ConnectionError:
        print('Debug port inaccessible, launching Messages')
        relaunched[0] = True
        launch_messages(messages_app)
        for i in range(20):
            try:
                requests.get(f'http://127.0.0.1:{debug_port}/')
                break
            except ConnectionError:
                time.sleep(1)
        else:
            sys.exit('Failed to launch Messages app')

    def handler(signum, frame):
        print('Selenium connection timed out, trying to relaunch Messages')
        relaunched[0] = True
        launch_messages(messages_app)

    chrome_options = Options()
    chrome_options.add_experimental_option(
        'debuggerAddress', f'127.0.0.1:{debug_port}')
    # If we can't connect after 3 seconds, probably Chrome is running in the
    # background (which is why we were able to connect to the debug port) but
    # there's no open Messages window.
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(3)
    driver = webdriver.Chrome(options=chrome_options)
    signal.alarm(0)
    return driver, relaunched


def find_element_with_timeout(driver, xpath, timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        try:
            elt = driver.find_element_by_xpath(xpath)
            elt.click()
            return(elt)
        except (NoSuchElementException, ElementNotInteractableException):
            time.sleep(1)


def do_business_once(driver, phone_number):
    elt = find_element_with_timeout(driver, '//a[@href="/web/calls"]')
    if not elt:
        print('No Calls button')
        return False
    print('Found Calls button')
    # If we had to wait for the new call button, then that means the app was
    # just launched, so we need to wait a second more for it to finish
    # initializing or the call might not work.
    start = time.time()
    elt = find_element_with_timeout(driver, '//a[@href="/web/calls/new"]')
    if not elt:
        print('No new call button')
        return False
    print('Found new call button')
    if time.time() - start > 0.5:
        time.sleep(1)
        print('Paused after clicking new call button')
    number_field = find_element_with_timeout(
        driver, '//input[@placeholder="Type a name or phone number"]')
    if not number_field:
        print('No number field')
        return False
    print('Found number field')
    number_field.send_keys(phone_number)
    number_field.send_keys(Keys.RETURN)
    print('Sent phone number')
    return True


def do_business(driver, phone_number, attempts=5):
    for i in range(attempts):
        print('Trying to place call')
        if do_business_once(driver, phone_number):
            return
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
    driver, relaunched = get_driver(messages_app, debug_port)
    print('Got driver')
    # This uniconifies the window if it's iconified
    driver.switch_to.window(driver.current_window_handle)
    print('Switched to window')
    do_business(driver, phone_number)


if __name__ == '__main__':
    main()
