import os
from libavg import avg
from libavg.mathutil import getScaledDim
from libavg.AVGAppUtil import getMediaDir, createImagePreviewNode
from . import app

g_player = avg.Player.get()


def createPreviewNode(maxSize):
    filename = os.path.join(getMediaDir(__file__), 'images/thumbnail.png')
    return createImagePreviewNode(maxSize, absHref = filename)

apps = (
        {'class': app.App,
            'createPreviewNode': createPreviewNode},
        )
