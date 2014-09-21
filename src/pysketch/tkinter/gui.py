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

from Tkinter import *
import tkFileDialog
from PIL import Image, ImageDraw

import pysketch

# Offset for drawing
rect_offset = pysketch.pen_size / 2

fgcolor = "black"
bgcolor = "white"
pilbg = (255, 255, 255)
if not pysketch.black_pen:
    fgcolor = "white"
    bgcolor = "black"
    pilbg = (0, 0, 0)

class ResizingCanvas(Canvas):
    """ A subclass of Canvas for dealing with resizing and
        managing a PIL image in the background, for saving
        drawings to a file.
    """
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

        # create a PIL canvas in memory and use in parallel
        self.pil_img = Image.new("RGB", (self.width, self.height), pilbg)
        self.pil_draw = ImageDraw.Draw(self.pil_img)


    def on_resize(self,event):
        """ Handle a resize by creating a new PIL image, and
            copying contents from the previous drawing over
            to it.
        """
        # create new PIL image
        tpil = Image.new("RGB", (event.width, event.height), pilbg)
        # Copy old image into new one
        copy_box = (0, 0, min(self.width, event.width), min(self.height, event.height))
        tpil.paste(self.pil_img, copy_box)
        self.pil_img = tpil
        self.pil_draw = ImageDraw.Draw(self.pil_img)
        
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)

    def draw_at(self, x, y):
        """ Draw a single 'point' at the given position.
        """
        self.create_rectangle((x - rect_offset, 
                               y - rect_offset, 
                               x + pysketch.pen_size, 
                               y + pysketch.pen_size), 
                               fill=fgcolor, outline=fgcolor)
        self.pil_draw.rectangle(((x - rect_offset, 
                                 y - rect_offset),
                                (x + pysketch.pen_size, 
                                 y + pysketch.pen_size)),
                                fill=fgcolor, outline=fgcolor)
        
    def erase_at(self, x, y):
        """ Erase a single 'point' at the given position, with doubled pen size.
        """
        self.create_rectangle((x - pysketch.pen_size, 
                               y - pysketch.pen_size, 
                               x + 2*pysketch.pen_size, 
                               y + 2*pysketch.pen_size), 
                               fill=bgcolor, outline=bgcolor)
        self.pil_draw.rectangle(((x - pysketch.pen_size, 
                                 y - pysketch.pen_size),
                                (x + 2*pysketch.pen_size, 
                                 y + 2*pysketch.pen_size)),
                                fill=bgcolor, outline=bgcolor)

    def save_image(self):
        """ Save the current drawing to a file.
        """
        fname = tkFileDialog.asksaveasfilename(parent=self,
                                               initialdir='.',
                                               filetypes=[('PNG files','*.png')])

        if fname != "":
            if not fname.endswith('.png'):
                fname += ".png"
                
            # save image as PNG file
            self.pil_img.save(fname)
        
    def new_image(self):
        """ Start a new image by removing all canvas items, and
            clearing the PIL image with the background color.
        """
        self.delete("all")
        self.pil_draw.rectangle(((0,0),(self.width,self.height)), 
                                fill=bgcolor, outline=bgcolor)

class TkinterFrame:
    """ The main window frame.
    """
    
    def __init__(self, root):
        root.title('pysketch %s' % pysketch.version)
        
        self.widgets = {}
        self.canvas = ResizingCanvas(root, 
                                     width=pysketch.canvas_width, 
                                     height=pysketch.canvas_height, 
                                     bg=bgcolor,
                                     highlightthickness=0)
        self.canvas.grid(column=0, columnspan=1, row=0, sticky='nesw')
        
        self.canvas.bind("<Button-1>", self.draw_brush)
        self.canvas.bind("<B1-Motion>", self.draw_brush)

        self.canvas.bind("<Button-3>", self.erase_brush)
        self.canvas.bind("<B3-Motion>", self.erase_brush)
        
        box = Frame(root)

        w = Button(box, text="Save", width=10, command=self.canvas.save_image)
        w.pack(side=LEFT, padx=5, pady=5, fill=X, expand=YES)
        w = Button(box, text="New", width=10, command=self.canvas.new_image)
        w.pack(side=LEFT, padx=5, pady=5, fill=X, expand=YES)

        box.grid(column=0, columnspan=1, row=1, sticky='ew')

        ## Resize behaviour(s)
        root.grid_rowconfigure(0, weight=1, minsize=pysketch.canvas_height)
        root.grid_rowconfigure(1, weight=0, minsize=30)
        root.grid_columnconfigure(0, weight=1, minsize=pysketch.canvas_width)
        
    def draw_brush(self, event):
        self.canvas.draw_at(event.x, event.y)
        
    def erase_brush(self, event):
        self.canvas.erase_at(event.x, event.y)
