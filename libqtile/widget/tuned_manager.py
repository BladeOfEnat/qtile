# Copyright (c) 2025 Emma Nora Theuer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from libqtile import bar
from libqtile.widget import base

import subprocess
import re
from os import system

class TunedManager(base._TextBox):
    """
    A widget to interact with the Tuned power management daemon.
    It always displays the name of the currently active profile.

    The user can define a list of profiles to be used, 3 default
    profiles exist. These 3 are the default profiles on RHEL and
    Fedora Linux.

    A left click on the widget will go to the next layout in the
    list, a right click will go to the previous one.  If the end
    of the list is reached, it cycles back to the beginning.
    Scrolling can also be used to cycle through the list, though
    keep in mind that switching the profile takes a while and so
    scrolling through the list quickly is not feasible.
    """
    orientations = base.ORIENTATION_HORIZONTAL

    defaults = [
        ("modes", ["powersave", "balanced-battery", "throughput-performance"], "The modes to cycle through")
    ]

    def __init__(self, **config):
        base._TextBox.__init__(self, "", **config)
        self.add_defaults(TunedManager.defaults)
        self.length_type = bar.CALCULATED
        self.current_mode = self.find_mode()

        self.add_callbacks({
            'Button1': self.next_mode, # Left Click
            'Button3': self.previous_mode, # Right Click
            'Button4': self.next_mode, # Scroll up
            'Button5': self.previous_mode # Scroll down
        })

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.text = TunedManager.find_mode(self)

    def find_mode(self):
        result = subprocess.run("tuned-adm active", shell=True, capture_output=True, text=True)
        output = result.stdout
        regex = re.compile(r"Current active profile:\s+(\S+)")
        return regex.findall(output)[0]

    def update_bar(self):
        self.current_mode = self.find_mode()
        self.text = self.current_mode
        self.bar.draw()

    def execute_command(self, index: int):
        argument = self.modes[index] # pyright: ignore
        # NOTE: For some reason, this does not work through subprocesses. It does work with os though. TODO: Fix.
        result = system(f"tuned-adm profile {argument}")
        if result == 0:
            self.update_bar()
        else:
            self.text = "Error setting mode"
            self.bar.draw()

    def next_mode(self):
        next_index: int = (self.modes.index(self.current_mode) + 1) % len(self.modes) # pyright: ignore
        self.execute_command(next_index)

    def previous_mode(self):
        prev_index: int = (self.modes.index(self.current_mode) - 1) % len(self.modes) # pyright: ignore
        self.execute_command(prev_index)
