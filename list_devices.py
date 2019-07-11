#!/usr/bin/env python3
#
# python-v4l2capture
#
# 2009, 2010 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

import os
import v4l2capture
file_names = [x for x in os.listdir("/dev") if x.startswith("video")]
file_names.sort()
for file_name in file_names:
	path = "/dev/" + file_name
	print(path)
	try:
		video = v4l2capture.Video_device(path)
		driver, card, bus_info, capabilities = video.get_info()
		print("    driver:       {}\n    card:         {}" \
			"\n    bus info:     {}\n    capabilities: {}".format(
				driver, card, bus_info, ", ".join([n.decode() for n in capabilities])))
		print('format', video.get_format())
		for fourcc in video.get_formats():
			for framesize in video.get_framesizes(fourcc):
				x, y = framesize['size_x'], framesize['size_y']
				for frameinterval in video.get_frameintervals(fourcc, x, y):
					print('\t', fourcc.decode(), x, y, frameinterval['fps'])
		video.close()
	except IOError as e:
		print("    " + str(e))
