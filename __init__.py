import os
from libavg.utils import getMediaDir, createImagePreviewNode
from . import app


def createPreviewNode(maxSize):
    filename = os.path.join(getMediaDir(__file__), 'images/thumbnail.png')
    return createImagePreviewNode(maxSize, absHref = filename)

apps = (
        {'class': app.App,
            'createPreviewNode': createPreviewNode},
        )
