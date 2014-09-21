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

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk

import pysketch

#
# Roughly based on the simplescribble.py example from the pygtk examples
#

# Backing pixmap for drawing area
pixmap = None
fg_gc = None
bg_gc = None

def style_gc(w, black=True):
    """ Simple helper function for selecting the correct graphics
        context, based on the set polarity.
    """
    global fg_gc
    global bg_gc
    
    if fg_gc is None:
        # Get the styles only once, assuming that always
        # the same widget gets passed...
        style = w.get_style()
        if pysketch.black_pen:
            fg_gc = style.black_gc 
            bg_gc = style.white_gc 
        else:
            fg_gc = style.white_gc 
            bg_gc = style.black_gc
             
    if black:
        return fg_gc
    else:
        return bg_gc

def configure_event(widget, event):
    """ Create a new backing pixmap of the appropriate size.
    """
    global pixmap

    x, y, width, height = widget.get_allocation()
    tpixmap = gtk.gdk.Pixmap(widget.window, width, height)
    tpixmap.draw_rectangle(style_gc(widget, black=False),
                           True, 0, 0, width, height)
    if pixmap:
        # Copy old contents to new bitmap
        colormap = pixmap.get_colormap()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *pixmap.get_size())
        pixbuf = pixbuf.get_from_drawable(pixmap, colormap, 0,0,0,0, *pixmap.get_size())        
        tpixmap.draw_pixbuf(widget.get_style().fg_gc[gtk.STATE_NORMAL], pixbuf,
                            0, 0, 0, 0)
    # Replace current bitmap
    pixmap = tpixmap

    return True

def expose_event(widget, event):
    """ Redraw the screen from the backing pixmap.
    """
    x , y, width, height = event.area
    widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                pixmap, x, y, x, y, width, height)
    return False

rect_offset = pysketch.pen_size / 2

def draw_brush(widget, x, y):
    """ Draw a rectangle on the screen.
    """
    rect = (int(x-rect_offset), int(y-rect_offset), 
            pysketch.pen_size, pysketch.pen_size)
    pixmap.draw_rectangle(style_gc(widget, black=True), True,
                          rect[0], rect[1], rect[2], rect[3])
    widget.queue_draw_area(rect[0], rect[1], rect[2], rect[3])

def erase_brush(widget, x, y):
    """ Erase a double sized rectangle on the screen.
    """
    
    rect = (int(x-pysketch.pen_size), int(y-pysketch.pen_size), 
            pysketch.pen_size*2, pysketch.pen_size*2)
    pixmap.draw_rectangle(style_gc(widget, black=False), True,
                          rect[0], rect[1], rect[2], rect[3])
    widget.queue_draw_area(rect[0], rect[1], rect[2], rect[3])

def button_press_event(widget, event):
    """ React to a button press event.
    """
    if event.button == 1 and pixmap != None:
        draw_brush(widget, event.x, event.y)
    elif event.button == 3 and pixmap != None:
        erase_brush(widget, event.x, event.y)
    return True

def motion_notify_event(widget, event):
    """ React to a motion event.
    """
    if event.is_hint:
        x, y, state = event.window.get_pointer()
    else:
        x = event.x
        y = event.y
        state = event.state

    if state & gtk.gdk.BUTTON1_MASK and pixmap != None:
        draw_brush(widget, x, y)
    elif state & gtk.gdk.BUTTON3_MASK and pixmap != None:
        erase_brush(widget, x, y)

    return True

class PygtkWindow(gtk.Window):
    """ The main window/app.
    """
    def __init__(self):
        super(PygtkWindow, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.set_title("pysketch %s" % pysketch.version)

        tbox = gtk.Table(2, 1, False)
        self.add(tbox)
        tbox.show()
    
        self.connect("destroy", lambda w: gtk.main_quit())
    
        # Create the drawing area
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.set_size_request(pysketch.canvas_width, 
                                      pysketch.canvas_height)
        
        tbox.attach(self.drawing_area, 0, 1, 0, 1,
                    gtk.FILL|gtk.EXPAND, gtk.FILL|gtk.EXPAND)
    
        self.drawing_area.show()
    
        # Signals used to handle backing pixmap
        self.drawing_area.connect("expose_event", expose_event)
        self.drawing_area.connect("configure_event", configure_event)
    
        # Event signals
        self.drawing_area.connect("motion_notify_event", motion_notify_event)
        self.drawing_area.connect("button_press_event", button_press_event)
    
        self.drawing_area.set_events(gtk.gdk.EXPOSURE_MASK
                                | gtk.gdk.LEAVE_NOTIFY_MASK
                                | gtk.gdk.BUTTON_PRESS_MASK
                                | gtk.gdk.POINTER_MOTION_MASK
                                | gtk.gdk.POINTER_MOTION_HINT_MASK)
        
        # .. some buttons
        hbox = gtk.HBox(True, 3)
        sbutton = gtk.Button("Save")
        
        hbox.pack_start(sbutton, True, True, 0)
        sbutton.connect_object("clicked", lambda w: w.save_image(), self)
        sbutton.show()

        nbutton = gtk.Button("New")
        hbox.pack_start(nbutton, True, True, 0)
        nbutton.connect_object("clicked", lambda w: w.new_image(), self)
        nbutton.show()

        hbox.show()
        tbox.attach(hbox, 0, 1, 1, 2,
                    gtk.FILL|gtk.EXPAND, gtk.FILL)

    def save_image(self):
        """ Save the current sketch as PNG image file.
        """
        
        #
        # Get pix buffer first...
        #
        drawable = self.drawing_area.window
        colormap = drawable.get_colormap()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0,0,0,0, *drawable.get_size())
        
        #
        # ...then start the SAVE dialog
        #
        dialog_buttons = (gtk.STOCK_CANCEL
                        , gtk.RESPONSE_CANCEL
                        , gtk.STOCK_SAVE
                        , gtk.RESPONSE_OK)

        file_dialog = gtk.FileChooserDialog(title="Select image file"
                    , action=gtk.FILE_CHOOSER_ACTION_SAVE
                    , buttons=dialog_buttons)
        # Create and add the file filter
        filter = gtk.FileFilter()
        filter.set_name("PNG file")
        filter.add_pattern("*.png")
        file_dialog.add_filter(filter)
    
        # Init the return value
        result = ""
        if file_dialog.run() == gtk.RESPONSE_OK:
            result = file_dialog.get_filename()
            if not result.endswith('.png'):
                result += '.png'
            
            pixbuf.save(result, 'png')
            
        file_dialog.destroy()
        
    def new_image(self):
        """ Start a new sketch by clearing the canvas.
        """
        if pixmap:
            sizes = pixmap.get_size()
            pixmap.draw_rectangle(style_gc(self.drawing_area, black=False),
                                  True, 0, 0, *sizes) 
            self.drawing_area.queue_draw_area(0, 0, *sizes)
