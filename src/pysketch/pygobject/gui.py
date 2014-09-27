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

import math
import cairo
from gi.repository import Gtk, Gdk

import pysketch

#
# Roughly based on the drawingarea.py example from the pygobject demo
#

# Offsets for drawing
rect_left = pysketch.pen_size / 2
erase_left = rect_left * pysketch.erase_factor
erase_width = pysketch.pen_size * pysketch.erase_factor

fgcolor = (0, 0, 0)
bgcolor = (1.0, 1.0, 1.0)
if not pysketch.black_pen:
    fgcolor = (1.0, 1.0, 1.0)
    bgcolor = (0, 0, 0)


class PygobjectApp:

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title('pysketch %s' % pysketch.version)
        self.window.set_default_size(pysketch.canvas_width, pysketch.canvas_height)
        self.window.connect('destroy', lambda x: Gtk.main_quit())
        self.width = pysketch.canvas_width
        self.height = pysketch.canvas_height

        # Storing the last mouse position
        self.lastx = None
        self.lasty = None

        tbox = Gtk.Table(2, 1, False)
        self.window.add(tbox)

        # Create the drawing area
        self.surface = None
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(pysketch.canvas_width,
                                           pysketch.canvas_height)

        tbox.attach(self.drawing_area, 0, 1, 0, 1,
                    Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                    Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND)

        # Signals used to handle backing pixmap
        self.drawing_area.connect("draw", self.draw_event)
        self.drawing_area.connect("configure-event", self.configure_event)

        # Event signals
        self.drawing_area.connect("motion-notify-event", self.motion_notify_event)
        self.drawing_area.connect("button-press-event", self.button_press_event)
        self.drawing_area.connect("button-release-event", self.button_release_event)

        self.drawing_area.set_events(self.drawing_area.get_events()
                                     | Gdk.EventMask.LEAVE_NOTIFY_MASK
                                     | Gdk.EventMask.BUTTON_PRESS_MASK
                                     | Gdk.EventMask.BUTTON_RELEASE_MASK
                                     | Gdk.EventMask.POINTER_MOTION_MASK
                                     | Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        # .. some buttons
        hbox = Gtk.HBox(True, 3)
        sbutton = Gtk.Button("Save")

        hbox.pack_start(sbutton, True, True, 0)
        sbutton.connect("clicked", self.save_image)

        nbutton = Gtk.Button("New")
        hbox.pack_start(nbutton, True, True, 0)
        nbutton.connect("clicked", self.new_image)

        tbox.attach(hbox, 0, 1, 1, 2,
                    Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                    Gtk.AttachOptions.FILL)

        self.window.show_all()

    def draw_event(self, da, cairo_ctx):
        cairo_ctx.set_source_surface(self.surface, 0, 0)
        cairo_ctx.paint()

        return False

    def cairo_line(self, cr,
                   lastx, lasty, x, y,
                   color, width):
        """ Draws a line with the given cairo context.
        """
        
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        cr.set_line_width(width)
        cr.set_source_rgb(*color)
        cr.move_to(lastx, lasty)
        cr.line_to(x, y)
        cr.stroke()

    def cairo_circle(self, cr, x, y, color, width):
        """ Draws a filled circle with the given cairo context.
        """
        
        cr.set_line_width(0.1)
        cr.set_source_rgb(*color)
        cr.arc(x, y, width/2.0, 0, 2 * math.pi)
        cr.stroke_preserve()
        cr.fill()

    def draw_point(self, widget, x, y, rectshape=True):
        """ Draw a point (=square/circle) on the screen.
        """
        
        update_rect = Gdk.Rectangle()
        update_rect.x = x - rect_left
        update_rect.y = y - rect_left
        update_rect.width = pysketch.pen_size
        update_rect.height = pysketch.pen_size

        # paint to the surface where we store our state
        cairo_ctx = cairo.Context(self.surface)
        if rectshape:
            cairo_ctx.set_source_rgb(*fgcolor)
            Gdk.cairo_rectangle(cairo_ctx, update_rect)
            cairo_ctx.fill()
        else:
            self.cairo_circle(cairo_ctx, x, y, fgcolor, pysketch.pen_size)

        widget.get_window().invalidate_rect(update_rect, False)

    def draw_brush(self, widget, x, y, rectshape=True):
        """ Draw a line or point on the screen.
        """
        
        if not pysketch.draw_lines:
            self.draw_point(widget, x, y)
        else:
            if self.lastx is not None:
                if self.lastx != x or self.lasty != y:
                    cairo_ctx = cairo.Context(self.surface)
                    self.cairo_line(cairo_ctx,
                                    self.lastx, self.lasty, x, y,
                                    fgcolor, pysketch.pen_size)
                    updx = min(self.lastx, x)
                    updy = min(self.lasty, y)
                    update_rect = Gdk.Rectangle()
                    update_rect.x = updx-pysketch.pen_size
                    update_rect.y = updy-pysketch.pen_size
                    update_rect.width = abs(x-self.lastx)+2*pysketch.pen_size
                    update_rect.height = abs(y-self.lasty)+2*pysketch.pen_size
                    widget.get_window().invalidate_rect(update_rect, False)
            else:
                self.draw_point(widget, x, y, False)

            # store the current position
            self.lastx = x
            self.lasty = y

    def erase_point(self, widget, x, y, rectshape=True):
        """ Erase a point (=square/circle) on the screen.
        """
        
        update_rect = Gdk.Rectangle()
        update_rect.x = x - erase_left
        update_rect.y = y - erase_left
        update_rect.width = erase_width
        update_rect.height = erase_width

        # paint to the surface where we store our state
        cairo_ctx = cairo.Context(self.surface)
        if rectshape:
            cairo_ctx.set_source_rgb(*bgcolor)
            Gdk.cairo_rectangle(cairo_ctx, update_rect)
            cairo_ctx.fill()
        else:
            self.cairo_circle(cairo_ctx, x, y, bgcolor, erase_width)

        widget.get_window().invalidate_rect(update_rect, False)

    def erase_brush(self, widget, x, y, rectshape=True):
        """ Erase a line or point on the screen.
        """
        
        if not pysketch.draw_lines:
            self.erase_point(widget, x, y)
        else:
            if self.lastx is not None:
                if self.lastx != x or self.lasty != y:
                    cairo_ctx = cairo.Context(self.surface)
                    self.cairo_line(cairo_ctx,
                                    self.lastx, self.lasty, x, y,
                                    bgcolor, erase_width)
                    updx = min(self.lastx, x)
                    updy = min(self.lasty, y)
                    update_rect = Gdk.Rectangle()
                    update_rect.x = updx-erase_width
                    update_rect.y = updy-erase_width
                    update_rect.width = abs(x-self.lastx)+2*erase_width
                    update_rect.height = abs(y-self.lasty)+2*erase_width
                    widget.get_window().invalidate_rect(update_rect, False)
            else:
                self.erase_point(widget, x, y, False)

            # store the current position
            self.lastx = x
            self.lasty = y

    def configure_event(self, da, event):
        """ Windows resize -> create a new Surface of the appropriate size.
        """

        allocation = da.get_allocation()
        # Create new surface
        tmp_surface = da.get_window().create_similar_surface(cairo.CONTENT_COLOR,
                                                             allocation.width,
                                                             allocation.height)
        # Clear surface background
        cairo_ctx = cairo.Context(tmp_surface)
        cairo_ctx.set_source_rgb(*bgcolor)
        cairo_ctx.paint()
        if self.surface is not None:
            # Copy over old image
            cairo_ctx.set_source_surface(self.surface, 0, 0)
            cairo_ctx.paint()

        # Keep reference to surface
        self.width = allocation.width
        self.height = allocation.height
        self.surface = tmp_surface

        return True

    def motion_notify_event(self, da, event):
        """ React to a motion event.
        """

        if self.surface is None:  # paranoia check, in case we haven't gotten a configure event
            return False

        # This call is very important; it requests the next motion event.
        # If you don't call gdk_window_get_pointer() you'll only get
        # a single motion event. The reason is that we specified
        # GDK_POINTER_MOTION_HINT_MASK to gtk_widget_set_events().
        # If we hadn't specified that, we could just use event->x, event->y
        # as the pointer location. But we'd also get deluged in events.
        # By requesting the next event as we handle the current one,
        # we avoid getting a huge number of events faster than we
        # can cope.

        (window, x, y, state) = event.window.get_pointer()

        if state & Gdk.ModifierType.BUTTON1_MASK:
            self.draw_brush(da, x, y)
        elif state & Gdk.ModifierType.BUTTON3_MASK:
            self.erase_brush(da, x, y)

        return True

    def button_press_event(self, da, event):
        """ React to a button press event.
        """

        if self.surface is None:  # paranoia check, in case we haven't gotten a configure event
            return False

        if event.button == 1:
            self.draw_brush(da, event.x, event.y)
        elif event.button == 3:
            self.erase_brush(da, event.x, event.y)

        return True

    def button_release_event(self, da, event):
        """ React to a button release event.
        """
        
        self.lastx = None
        self.lasty = None

        return True

    def save_image(self, widget):
        """ Save the current sketch as PNG image file.
        """

        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_do_overwrite_confirmation(True)

        filter_text = Gtk.FileFilter()
        filter_text.set_name("PNG files")
        filter_text.add_mime_type("image/png")
        filter_text.add_pattern("*.png")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            fname = dialog.get_filename()
            if not fname.endswith('.png'):
                fname += '.png'
            if self.surface is not None:
                self.surface.write_to_png(fname)

        dialog.destroy()

    def new_image(self, widget):
        """ Start a new sketch by clearing the canvas.
        """

        update_rect = Gdk.Rectangle()
        update_rect.x = 0
        update_rect.y = 0
        update_rect.width = self.width
        update_rect.height = self.height

        # paint to the surface where we store our state
        cairo_ctx = cairo.Context(self.surface)
        cairo_ctx.set_source_rgb(*bgcolor)
        Gdk.cairo_rectangle(cairo_ctx, update_rect)
        cairo_ctx.fill()

        widget.get_window().invalidate_rect(update_rect, False)
