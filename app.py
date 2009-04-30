#!/usr/bin/env python
# coding=utf8

from libavg import avg, Point2D, Bitmap, anim, AVGApp
from libavg import AVGMTAppStarter
import config
import os

from PIL import Image, ImageDraw
from libavg.AVGAppUtil import getMediaDir

g_Player = avg.Player.get()

class App(AVGApp):
    def __init__(self, parentNode):
        print "alles paletti init"
        canvasXML = open(os.path.join(getMediaDir(__file__), "canvas.avg"))
        self.__mainNode = g_Player.createNode(canvasXML.read())
        self.__mainNode.mediadir = getMediaDir(__file__)
        parentNode.appendChild(self.__mainNode)

        g_Player.getElementByID("time").parawidth = int(config.resolution.x)
        g_Player.getElementByID("win").parawidth = int(config.resolution.x)

        g_Player.getElementByID("canvas").setEventHandler(avg.CURSORDOWN, 
avg.TOUCH, self.getColor)
        g_Player.getElementByID("canvas").setEventHandler(avg.CURSORMOTION,
avg.TOUCH, self.paint)
        g_Player.getElementByID("canvas").setEventHandler(avg.CURSORUP,
avg.TOUCH, self.forgetColor)


        global tehBrushes, oldCoord
        tehBrushes, oldCoord = {}, {}
        self.reset()

    def winFade(self):
        anim.fadeOut(g_Player.getElementByID("win"), config.fadeOutTime, onStop=self.reset)

    def reset(self):
        global tehTime
        tehTime = config.roundDuration
        g_Player.getElementByID("time").text = str(tehTime)
        anim.fadeIn(g_Player.getElementByID("time"), config.fadeInTime, 0.5)

        global tehImage
        # tehImage = Bitmap(g_Player.getElementByID("canvas").href)
        tehImage = Bitmap(os.path.join(getMediaDir(__file__), "images/paint.png"))

        global im
        im = Image.fromstring ('RGBA',
(int(config.resolution.x),(int(config.resolution.y))),
tehImage.getPixels())
        anim.fadeIn(g_Player.getElementByID("canvas"), config.fadeInTime, 1.0)

        global dirty
        dirty = True

        global endgame
        endgame = False

    def _enter(self):
        self.__onFrameHandler = g_Player.setOnFrameHandler(self.updateImage)
        self.__clockInterval = g_Player.setInterval(1000, self.checkTime)
        self.winFade()

    def _leave(self):
        g_Player.clearInterval(self.__onFrameHandler)
        g_Player.clearInterval(self.__clockInterval)

    def updateImage(self):
        if dirty:
            tehImage.setPixels(im.tostring())
            g_Player.getElementByID("canvas").setBitmap(tehImage)
            global dirty
            dirty = False

    def getColor(self, event):
        x,y = event.pos.x, event.pos.y

        r, g, b, a = im.getpixel((x,y))
        tehBrushes[event.cursorid] = [r,g,b,a]

        global oldCoord
        oldCoord[event.cursorid] = [x,y]
  
    def paint(self, event):
        pos = (event.pos.x, event.pos.y)
        try:
            r, g, b, a = tehBrushes[event.cursorid]
        except KeyError: # ignore foreign cursors
            return

        if a:
            draw = ImageDraw.Draw(im)
            w = config.brushSize
            rad = w / 2
            x,y = event.pos.x, event.pos.y
            oldx, oldy = oldCoord[event.cursorid]
            draw.ellipse((x-rad,y-rad) + (x+rad, y+rad), fill=(r,g,b,a))
            draw.line((x,y) + (oldx, oldy), fill=(r,g,b,a), width=w)
            del draw

            global oldCoord
            oldCoord[event.cursorid] = [x,y]

            global dirty
            dirty = True

    def forgetColor(self, event):
        if event.cursorid in tehBrushes:
            del tehBrushes[event.cursorid]
            del oldCoord[event.cursorid]

    def checkTime(self):
        if (endgame == False):
            global tehTime

            g_Player.getElementByID("time").text = str(tehTime)
            tehTime = tehTime - 1

            if (tehTime == -2):
                self.endGame()

    def endGame(self):
        global endgame
        endgame == True

        colors = {}
        paintedCanvas = im.load()

        anim.fadeOut(g_Player.getElementByID("canvas"), config.fadeOutTime)
        anim.fadeOut(g_Player.getElementByID("time"), config.fadeOutTime)

        for x in range(0,int(config.resolution.x)):
            for y in range(0,int(config.resolution.y)):
                r,g,b,a = paintedCanvas[x,y]
                colorname = "%02x%02x%02x" % (r,g,b)

                if not(colors.has_key(colorname)):
                    colors[colorname] = 0

                colors[colorname] = colors[colorname] + 1

        colors["ffffff"] = 0
        wincolor = max(colors.iterkeys(), key=lambda k: colors[k]) # interesting way to sort dictionaries by values

        win = g_Player.getElementByID("win")
        win.color = wincolor
        #anim.fadeIn(win, config.fadeInTime, 1.0, onStop=self.winFade)
        anim.fadeIn(win, config.fadeInTime, 1.0)
        g_Player.setTimeout(config.fadeInTime + config.fadeOutTime, self.leave)


if __name__ == '__main__':
    AVGMTAppStarter(appClass = App, resolution = (1280,720))
