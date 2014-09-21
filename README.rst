###############################
pysketch - For simple scribbles
###############################

Basics
======

This tool can be used to "take notes" in the form of graphical scribbles, as you would paint them on a small
piece of paper with a pencil, pen, Sharpie (tm), or similar. It doesn't offer any special options by design.
You get a canvas and can draw on it, with a fix-sized black pen...that's it.

If you're looking for the more fancy stuff, there are a ton of good drawing applications out
there (gimp, inkscape, ...). 
Go pick one of them, e.g. if you need special brush shapes with dynamics attached.

I try to keep pysketch as minimalistic as possible, such that I can concentrate on *what* I draw, instead of
*how* I draw it.

Idea
====

Basic influences for the design and implementation of pysketch were: gsumi/xink and the "scribblesimple" example
from the pygtk distribution.

Installing
==========

For installing ``pysketch``, you have to get root and then run the command

::

    python setup.py install

Starting
========

After a successful installation, you can call ``pysketch`` from the command-line

::

    pysketch

It supports a few parameters, that get listed with the ``-h`` option (or ``--help``).

Draw with the left mouse button held down, the right button erases with a doubled pen size. The
two push buttons at the bottom of the main widget should be pretty self-explanatory. ;)

Requirements
============

Pysketch should run under any Python2.x, with either the Tkinter or GTK2/pygobject bindings installed.

TODOs and known problems
========================

Tkinter mode: making the canvas larger, drawing, and then shrinking the window again, will
lead to inconsistencies. The canvas items that are off-screen don't get removed (no clipping),
but the PIL image in the background won't have those lines anymore.

Pygobject mode: on a resize, the canvas is cleared completely. Just like for the pygtk binding,
the current surface should be saved into a pixbuf, and then copied to the new surface again.
Additionally, drawing is slow...try double-buffering for a better performance.
