# coding: latin-1
# Copyright (c) 2014 Dirk Baechle.
# www: https://bitbucket.org/dirkbaechle/pysketch
# mail: dl9obn AT darc.de
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

#
# Default values
#
canvas_width = 300
canvas_height = 300
pen_size = 3
erase_factor = 8
black_pen = True
draw_lines = True
version = '1.1'


def banner():
    """ Return a small banner message.
    """
    
    return "pysketch %s, https://bitbucket.org/dirkbaechle/pysketch" % version

#
# In this main package "pysketch", you can find the single subfolders for
# each supported GUI binding. The single GUI packages have to support
# the following interface:
#
#    package.exists()   : returns 'True' if all required modules can be imported,
#                         signalling that this binding is available
#    package.name()     : returns the unique name, that is used to reference this
#                         module throughout "pysketch"
#    package.run_main() : starts the main application for this binding type and
#                         runs it
#
# Each GUI module should try to mimic the following basic behaviour, as closely
# as possible:
#
# - The main window opens, such that the drawing area has the specified width/height.
# - There is no menu bar.
# - The window can get resized larger, but not smaller than the size specified by
#   the user or the default settings, respectively.
# - On a resize, the buttons in the bottom row always keep their minimum height.
# - The buttons fill/expand in the horizontal direction, a small padding between the single
#   buttons is allowed (e.g. 3px).
#
