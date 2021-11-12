Using Google Fi Messages for Web for "tel:" links in Chrome on Linux
====================================================================

Introduction
------------

This directory contains the files you need to make any "tel:" link you
click on in Google Chrome in GNOME on Linux cause the number to be
dialed in the Google Fi Messages for Web app, along with instructions
for how to set it up.

It's rather bewildering that Google doesn't provide a way to do this
automatically. Maybe there actually is a way to do it that I haven't
found. If so, please let me know! There is nothing I would like more
than for everything in this directory to be obsoleted by something
supported by the vendor.

Overall strategy
----------------

The strategy used here is:

* Set up the Messages for Web app in a separate Chrome instance,
  configured to launch with a remote debugging port opened so Selenium
  can connect to it.

* Implement a Python Selenium script which knows how to launch
  Messages for Web if it isn't already running, connect to it over the
  remote debugging port, and make it dial a phone number.

* Install a GNOME desktop file which knows how to launch that script
  and knows that it is associated with the "x-scheme-handler/tel" MIME
  type, i.e., "tel:" links.

* Configure GNOME to use that desktop file by default for "tel:"
  links.

With all this in place, when you click on a "tel:" link in the browser
and then select "xdg-open" when prompted for how to open the link, the
call will be dialed in Messages. It will actually work with anything,
not just Chrome, that uses GNOME's built-in type system to open "tel:"
links.

Prerequisites
-------------

You need to have Google Fi and Chrome.

You need to have python3 and the python selenium modules installed.
On Ubuntu, `sudo apt install -y python3-selenium` will do the needful.

Notes and caveats
-----------------

The installer sets up the Messages app to run in a separate Chrome
instance for security reasons. If we instead configured the user's
regular Chrome with a remote debugging port enabled, then all of the
user's browser windows and tabs would be fully accessible to Selenium,
which wouldn't be great.

CAUTION: Even with things implemented as described here, anyone who
can log into your computer will be able to read content from the
Messages app while it's running. If you're unwise and not running a
local firewall, anyone on your local network will as well. If you're
not running a firewall _and_ you install this on a computer with a
public IP address, it's possible that anyone on the internet will be
able to read content from your Messages app! Be sensible.

The Selenium script is rather sensitive to the page structure of the
Messages app. If Google changes the page structure and breaks the
script, I'll eventually get around to fixing it, but if you notice it
before I do, let me know!

Personally, when I have everything set up as described above and I
click on a "tel:" link, Google asks whether I want to use my phone or
xdg-open to open the link. I wish I could figure out how to make it
stop prompting and always use xdg-open. If you know, let me know!

How to install
--------------

### Setting up the chrome profile and the Messages app

1. Clone this repository to a local directory.

2. Run `./install.sh` and follow its prompts and instructions.

How to uninstall
----------------

Run `~/.messages-tel/uninstall.sh`.

Credits
-------

Written by Jonathan Kamens &lt;<jik@kamens.us>&gt;.

To-Do List
----------

(Pull requests happily accepted!)

Is there already a way to do this that is supported by Google? If so,
let's just get rid of this whole project and use that instead!

Is there a way to force Chrome to always use `xdg-open` rather than
prompting the user for whether to use `xdg-open` or send the call to a
phone?

It should be feasible to make this work on macOS and Windows, too.

This method is probably relatively easily extensible to other web apps
that know how to make phone calls but do not provide an integration
with "tel:" links in the browser.

Copyright
---------

Copyright (C) 2021 Jonathan Kamens.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
