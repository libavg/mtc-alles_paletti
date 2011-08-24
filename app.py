#!/usr/bin/env python

# Copyright (C) 2009
#    Nils Dagsson Moskopp (erlehmann) <nils@dieweltistgarnichtso.net>
#
# alles paletti is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# alles paletti is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with alles paletti.  If not, see <http://www.gnu.org/licenses/>.

from libavg import avg, Point2D, Bitmap, anim, AVGApp
from libavg import AVGMTAppStarter
import config
import os
from PIL import Image, ImageDraw
from libavg.utils import getMediaDir

g_Player = avg.Player.get()

class App(AVGApp):
    dirty = True
    endgame = False
    im = None
    oldCoord = None
    tehBrushes = None
    tehImage = None
    tehTime = None

    __onFrameHandler = None
    __clockInterval = None

    def init(self):
        canvasXML = open(os.path.join(getMediaDir(__file__), "canvas.avg"))
        self.__mainNode = g_Player.createNode(canvasXML.read())
        self.__mainNode.mediadir = getMediaDir(__file__)
        self._parentNode.appendChild(self.__mainNode)

        for nodeID in "time", "win":
            node = g_Player.getElementByID(nodeID)
            node.width = self._parentNode.size.x
            node.x = self._parentNode.size.x/2

        g_Player.getElementByID("canvas").setEventHandler(avg.CURSORDOWN, avg.TOUCH, self.getColor) 
        g_Player.getElementByID("canvas").setEventHandler(avg.CURSORMOTION, avg.TOUCH, self.paint)
        g_Player.getElementByID("canvas").setEventHandler(avg.CURSORUP, avg.TOUCH, self.forgetColor)


        self.tehBrushes, self.oldCoord = {}, {}
        self.tehTime = config.roundDuration
        self.tehImage = Bitmap(os.path.join(getMediaDir(__file__), "images/paint.png"))
        self.im = Image.fromstring ('RGBA',
            (int(config.resolution.x),(int(config.resolution.y))),
            self.tehImage.getPixels())

    def winFade(self):
        anim.fadeOut(g_Player.getElementByID("win"), config.fadeOutTime, onStop=self.reset).start()

    def reset(self):
        g_Player.getElementByID("time").text = str(self.tehTime)
        anim.fadeIn(g_Player.getElementByID("time"), config.fadeInTime, 0.5).start()

        # self.tehImage = Bitmap(g_Player.getElementByID("canvas").href)
        self.tehImage = Bitmap(os.path.join(getMediaDir(__file__), "images/paint.png"))

        # the format of tehImage is BGRA not RGBA. we need to take care of that while we analyse the image !
        anim.fadeIn(g_Player.getElementByID("canvas"), config.fadeInTime, 1.0).start()

        self.dirty = True
        self.endgame = False

        # set timers
        if not self.__onFrameHandler:
            self.__onFrameHandler = g_Player.setOnFrameHandler(self.updateImage)
        if not self.__clockInterval:
            self.__clockInterval = g_Player.setInterval(1000, self.checkTime)

    def _enter(self):
        g_Player.getElementByID("time").text = '!'
        self.winFade()

    def _leave(self):
        if self.__onFrameHandler:
            g_Player.clearInterval(self.__onFrameHandler)
            self.__onFrameHandler = None
        if self.__clockInterval:
            g_Player.clearInterval(self.__clockInterval)
            self.__clockInterval = None

    def updateImage(self):
        if self.dirty:
            self.tehImage.setPixels(self.im.tostring())
            g_Player.getElementByID("canvas").setBitmap(self.tehImage)
            self.dirty = False

    def getColor(self, event):
        x,y = event.pos.x, event.pos.y

        r, g, b, a = self.im.getpixel((x,y))
        self.tehBrushes[event.cursorid] = [r,g,b,a]

        self.oldCoord[event.cursorid] = [x,y]
  
    def paint(self, event):
        pos = (event.pos.x, event.pos.y)
        try:
            r, g, b, a = self.tehBrushes[event.cursorid]
        except KeyError: # ignore foreign cursors
            return

        if a:
            draw = ImageDraw.Draw(self.im)
            w = config.brushSize
            rad = w / 2
            x,y = event.pos.x, event.pos.y
            oldx, oldy = self.oldCoord[event.cursorid]
            draw.ellipse((x-rad,y-rad) + (x+rad, y+rad), fill=(r,g,b,a))
            draw.line((x,y) + (oldx, oldy), fill=(r,g,b,a), width=w)
            del draw

            self.oldCoord[event.cursorid] = [x,y]
            self.dirty = True

    def forgetColor(self, event):
        if event.cursorid in self.tehBrushes:
            del self.tehBrushes[event.cursorid]
            del self.oldCoord[event.cursorid]

    def checkTime(self):
        if (self.endgame == False):
            if self.tehTime >= 0:
                g_Player.getElementByID("time").text = str(self.tehTime)

            if (self.tehTime == -2):
                self.endGame()
        self.tehTime = self.tehTime - 1

    def endGame(self):
        self.endgame == True
        colors = {}
        paintedCanvas = self.im.load()
        anim.fadeOut(g_Player.getElementByID("canvas"), config.fadeOutTime).start()
        anim.fadeOut(g_Player.getElementByID("time"), config.fadeOutTime).start()

        for x in range(0,int(config.resolution.x)):
            for y in range(0,int(config.resolution.y)):
                r,g,b,a = self.tehImage.getPixel((x,y))
                if a != 0:
                    colorname = "%02x%02x%02x" % (r,g,b)
                    if not(colors.has_key(colorname)):
                        colors[colorname] = 0
                    colors[colorname] = colors[colorname] + 1
        colors["ffffff"] = 0
        wincolor = max(colors.iterkeys(), key=lambda k: colors[k]) # interesting way to sort dictionaries by values

        win = g_Player.getElementByID("win")
        win.color = wincolor
        #anim.fadeIn(win, config.fadeInTime, 1.0, onStop=self.winFade)
        anim.fadeIn(win, config.fadeInTime, 1.0).start()
        g_Player.setTimeout(config.fadeInTime + config.fadeOutTime, self.leave)


if __name__ == '__main__':
    AVGMTAppStarter(appClass = App, resolution = (1280,720))

