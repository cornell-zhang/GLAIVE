#!/usr/bin/python

from PIL import Image
import sys

if len(sys.argv) != 2:
    print("Usage: python convert.py [image_file(.rgb format)]")
    exit()

img_list = []

rgb_file_name = sys.argv[1]
rgb_file_base = rgb_file_name.split('.')[0]

img_list = open(sys.argv[1]).read().splitlines()

dim_info = img_list[0].split(',')
width = int(dim_info[0])
height = int(dim_info[1])

rgb_val_list = []
rgb_tuple_list = []

for i in range(1,len(img_list)-1):
    rgb_val_list.append(img_list[i].split(','))

for line in rgb_val_list:
    for i in range(len(line)):
        if (i + 1) % 3 == 0:
            r = int(line[i-2])
            g = int(line[i-1])
            b = int(line[i])
            rgb_tuple_list.append((r,g,b))

im = Image.new("RGB", (width,height), color=0)
im.putdata(rgb_tuple_list)
im.save("%s.jpg" % rgb_file_base)

