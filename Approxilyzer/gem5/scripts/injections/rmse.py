from __future__ import division
import PIL
import PIL.Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import itertools
import sys

IMGDIR = 'saved_outputs'

def load():
    return 'file:out.pgm'

def checkDim(orig, relaxed):
    orig_image = PIL.Image.open(orig)
    relaxed_image = PIL.Image.open(relaxed)
    orig_w, orig_h= orig_image.size
    relaxed_w, relaxed_h = relaxed_image.size
    if (orig_w == relaxed_w and orig_h == relaxed_h):
        return True
    return False


def score(orig, relaxed):
    orig_image = PIL.Image.open(orig)
    relaxed_image = PIL.Image.open(relaxed)
    error = 0
    total = 0

    try:
        orig_data = orig_image.getdata()
        relaxed_data = relaxed_image.getdata()
    except ValueError:
        return 1.0

    for ppixel, apixel in itertools.izip(orig_data, relaxed_data):
        # check for tuples in color image
        if isinstance(ppixel, tuple):
            r_err = abs(ppixel[0] - apixel[0])
            g_err = abs(ppixel[1] - apixel[1])
            b_err = abs(ppixel[2] - apixel[2])
            error += (r_err + g_err + b_err) / 3
            total += 1
        else:
            error += abs(ppixel - apixel)
            total += 1
    return (error / 255 / total) * 100


# main function
dimCheck = checkDim(sys.argv[1], sys.argv[2] )

if (dimCheck is False):
    print "SDC:Eggregious-pixel_mismatch",
else:
    print "SDC:Tolerable;%f" %score(sys.argv[1], sys.argv[2]),
