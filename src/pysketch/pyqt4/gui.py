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

import sip
sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui

import pysketch

#
# Roughly based on scribble.py from the PyQt4 examples
#

# Offsets for drawing
rect_left = pysketch.pen_size / 2
erase_left = rect_left * pysketch.erase_factor
erase_width = pysketch.pen_size * pysketch.erase_factor

fgcolor = QtCore.Qt.black
bgcolor = QtCore.Qt.white
if not pysketch.black_pen:
    fgcolor = QtCore.Qt.white
    bgcolor = QtCore.Qt.black


class ScribbleArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StaticContents)

        self.scribbling = False
        self.image = QtGui.QImage()
        self.fgbrush = QtGui.QBrush(fgcolor, QtCore.Qt.SolidPattern)
        self.bgbrush = QtGui.QBrush(bgcolor, QtCore.Qt.SolidPattern)
        self.lastPoint = QtCore.QPoint()

    def saveImage(self, fileName):
        """ Save the current sketch as PNG image
            under the given filename.
        """

        if self.image.save(fileName, 'png'):
            return True
        else:
            return False

    def newImage(self):
        """ Start a new sketch by clearing the canvas.
        """

        self.image.fill(bgcolor)
        self.update()

    def mousePressEvent(self, event):
        """ React to a button press event.
        """

        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.pos()
            self.draw_brush(event.pos())
            self.scribbling = True
        elif event.button() == QtCore.Qt.RightButton:
            self.lastPoint = event.pos()
            self.erase_brush(event.pos())
            self.scribbling = True

    def mouseMoveEvent(self, event):
        """ React to a mouse move event.
        """

        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            self.draw_brush(event.pos())
        elif (event.buttons() & QtCore.Qt.RightButton) and self.scribbling:
            self.erase_brush(event.pos())

    def mouseReleaseEvent(self, event):
        """ React to a button release event.
        """

        if (((event.button() == QtCore.Qt.RightButton) or
             (event.button() == QtCore.Qt.LeftButton)) and self.scribbling):
            self.scribbling = False

    def paintEvent(self, event):
        """ Redraw the screen from the backing pixmap.
        """

        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self.image)

    def resizeEvent(self, event):
        if self.width() != self.image.width() or self.height() != self.image.height():
            self.resizeImage(self.image, QtCore.QSize(self.width(), self.height()))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def draw_point(self, endPoint, rectshape=True):
        """ Draw a point (=square/circle) on the screen.
        """

        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(fgcolor, 0.1,
                                  QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setBrush(self.fgbrush)
        update_rect = QtCore.QRect(endPoint.x()-rect_left,
                                   endPoint.y()-rect_left,
                                   pysketch.pen_size, pysketch.pen_size)
        if rectshape:
            painter.drawRect(update_rect)
        else:
            painter.drawEllipse(update_rect)
        self.update(update_rect)

    def draw_brush(self, endPoint):
        """ Draw a line or point on the screen.
        """

        if not pysketch.draw_lines:
            self.draw_point(endPoint)
        else:
            if self.scribbling:
                if endPoint != self.lastPoint:

                    painter = QtGui.QPainter(self.image)
                    painter.setPen(QtGui.QPen(fgcolor, pysketch.pen_size,
                                              QtCore.Qt.SolidLine,
                                              QtCore.Qt.RoundCap,
                                              QtCore.Qt.RoundJoin))
                    painter.drawLine(self.lastPoint, endPoint)

                    rad = pysketch.pen_size / 2 + 2
                    self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
            else:
                self.draw_point(endPoint, False)

            # store the current position
            self.lastPoint = QtCore.QPoint(endPoint)

    def erase_point(self, endPoint, rectshape=True):
        """ Erase a point (=square/circle) on the screen.
        """

        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(bgcolor, 0.1,
                                  QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setBrush(self.bgbrush)
        update_rect = QtCore.QRect(endPoint.x()-erase_left,
                                   endPoint.y()-erase_left,
                                   erase_width, erase_width)
        if rectshape:
            painter.drawRect(update_rect)
        else:
            painter.drawEllipse(update_rect)
        self.update(update_rect)

    def erase_brush(self, endPoint):
        """ Erase a line or point on the screen.
        """

        if not pysketch.draw_lines:
            self.erase_point(endPoint)
        else:
            if self.scribbling:
                if endPoint != self.lastPoint:

                    painter = QtGui.QPainter(self.image)
                    painter.setPen(QtGui.QPen(bgcolor, erase_width,
                                              QtCore.Qt.SolidLine,
                                              QtCore.Qt.RoundCap,
                                              QtCore.Qt.RoundJoin))
                    painter.drawLine(self.lastPoint, endPoint)

                    rad = erase_width / 2 + 2
                    self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
            else:
                self.erase_point(endPoint, False)

            # store the current position
            self.lastPoint = QtCore.QPoint(endPoint)

    def resizeImage(self, image, newSize):
        """ Create a new backing pixmap of the appropriate size.
        """

        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(bgcolor)
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.image = newImage


class PyQt4Window(QtGui.QMainWindow):
    def __init__(self):
        super(PyQt4Window, self).__init__()

        self.scribbleArea = ScribbleArea()

        self.panel = QtGui.QWidget()
        self.vbox = QtGui.QVBoxLayout()
        self.hbox = QtGui.QHBoxLayout()
        self.save = QtGui.QPushButton("Save")
        self.new = QtGui.QPushButton("New")
        self.hbox.addWidget(self.save)
        self.hbox.addWidget(self.new)
        self.vbox.addWidget(self.scribbleArea)
        self.vbox.addLayout(self.hbox)
        self.panel.setLayout(self.vbox)

        self.setCentralWidget(self.panel)

        self.setWindowTitle("pysketch %s" % pysketch.version)
        self.scribbleArea.setMinimumSize(pysketch.canvas_width, pysketch.canvas_height)

        self.connect(self.save, QtCore.SIGNAL('clicked()'), self.saveImage)
        self.connect(self.new, QtCore.SIGNAL('clicked()'), self.scribbleArea.newImage)

    def saveImage(self):
        """ Get a filename and save the current sketch
            as PNG image file.
        """

        initialPath = QtCore.QDir.currentPath() + '/untitled.png'

        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As",
                                                     initialPath,
                                                     "PNG Files (*.png);;All Files (*)")
        if fileName:
            return self.scribbleArea.saveImage(fileName)

        return False
