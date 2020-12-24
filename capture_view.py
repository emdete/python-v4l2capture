#!/usr/bin/env python3
from select import select
from time import time
from os.path import exists
from os import listdir, makedirs
from functools import cmp_to_key
from configparser import RawConfigParser
from PIL.Image import frombytes, open as fromfile, eval as image_eval, merge as image_merge
from PIL.ImageTk import PhotoImage
from PIL.ImageOps import invert, autocontrast, grayscale, equalize, solarize
from tkinter import Tk, Canvas, TOP, Frame
from v4l2capture import Video_device

def cmp(a, b):
	return (a > b) - (a < b)

class Cam(Frame):
	def __init__(self, device='/dev/video0'):
		self.root = Tk()
		def bind(e, f):
			self.root.bind(e, f)
			print(e, 'is', f.__name__, )
		bind('q', lambda e: self.root.quit())
		bind('<Home>', self.raise_saturation)
		bind('<End>', self.lower_saturation)
		bind('k', self.raise_hue)
		bind('j', self.lower_hue)
		bind('<Prior>', self.raise_gamma)
		bind('<Next>', self.lower_gamma)
		bind('<Up>', self.raise_exposure)
		bind('<Down>', self.lower_exposure)
		bind('<space>', self.raise_contrast)
		bind('<BackSpace>', self.lower_contrast)
		bind('<Right>', self.raise_brightness)
		bind('<Left>', self.lower_brightness)
		Frame.__init__(self, self.root)
		self.x_canvas = Canvas(self.root, width=800, height=800, )
		self.x_canvas.pack(side=TOP)
		self.video = None
		self.do_start_video(device)

	def lower_hue(self, *args):
		if self.video:
			self.hue = self.video.set_hue(self.hue - 10)
			print('hue', self.hue)

	def raise_hue(self, *args):
		if self.video:
			self.hue = self.video.set_hue(self.hue + 10)
			print('hue', self.hue)

	def lower_gamma(self, *args):
		if self.video:
			self.gamma = self.video.set_gamma(self.gamma - 10)
			print('gamma', self.gamma)

	def raise_gamma(self, *args):
		if self.video:
			self.gamma = self.video.set_gamma(self.gamma + 10)
			print('gamma', self.gamma)

	def lower_saturation(self, *args):
		if self.video:
			self.saturation = self.video.set_saturation(self.saturation - 10)
			print('saturation', self.saturation)

	def raise_saturation(self, *args):
		if self.video:
			self.saturation = self.video.set_saturation(self.saturation + 10)
			print('saturation', self.saturation)

	def lower_contrast(self, *args):
		if self.video:
			self.contrast = self.video.set_contrast(self.contrast - 10)
			print('contrast', self.contrast)

	def raise_contrast(self, *args):
		if self.video:
			self.contrast = self.video.set_contrast(self.contrast + 10)
			print('contrast', self.contrast)

	def lower_brightness(self, *args):
		if self.video:
			self.brightness = self.video.set_brightness(self.brightness - 10)
			print('brightness', self.brightness)

	def raise_brightness(self, *args):
		if self.video:
			self.brightness = self.video.set_brightness(self.brightness + 10)
			print('brightness', self.brightness)

	def lower_exposure(self, *args):
		if self.video:
			self.exposure = self.video.set_exposure_absolute(self.exposure - 10)
			print('exposure', self.exposure)

	def raise_exposure(self, *args):
		if self.video:
			self.exposure = self.video.set_exposure_absolute(self.exposure + 10)
			print('exposure', self.exposure)

	def do_stop_video(self, *args):
		if self.video is not None:
			self.video.stop()
			self.video.close()
			self.video = None

	def do_start_video(self, device, *args):
		if self.video is None:
			self.video = Video_device(device)
			_, _, self.fourcc = self.video.get_format()
			print('fourcc', self.fourcc)
			caps = self.video.get_framesizes(self.fourcc)
			caps = sorted(caps, key=cmp_to_key(lambda a, b: cmp(a['size_x']*a['size_y'], b['size_x']*b['size_y'])))
			print('caps', caps)
			self.framesize = caps[len(caps)//2]
			print('framesize', self.framesize)
			self.framesize['size_x'], self.framesize['size_y'] = self.video.set_format(self.framesize['size_x'], self.framesize['size_y'], 0, 'MJPEG')
			if True:
				try: self.video.set_auto_white_balance(True)
				except: print('error setting wb')
				try: self.video.set_exposure_auto(True)
				except: print('error setting ae')
				try: self.video.set_focus_auto(True)
				except: print('error setting af')
			self.exposure = self.video.get_exposure_absolute()
			print('exposure', self.exposure)
			self.brightness = self.video.get_brightness()
			print('brightness', self.brightness)
			self.hue = self.video.get_hue()
			print('hue', self.hue)
			self.saturation = self.video.get_saturation()
			print('saturation', self.saturation)
			self.contrast = self.video.get_contrast()
			print('contrast', self.contrast)
			self.gamma = self.video.get_gamma()
			print('gamma', self.gamma)
			self.video.create_buffers(30)
			self.video.queue_all_buffers()
			self.video.start()
			self.root.after(1, self.do_live_view)

	def do_live_view(self, *args):
		if self.video is not None:
			select((self.video, ), (), ())
			data = self.video.read_and_queue()
			self.image = frombytes('RGB', (self.framesize['size_x'], self.framesize['size_y']), data)
			self.photo = PhotoImage(self.image)
			self.x_canvas.create_image(800/2, 800/2, image=self.photo)
			self.root.after(3, self.do_live_view)

def main(*args):
	' main start point of the program '
	app = Cam(*args)
	app.mainloop()
	app.root.destroy()

if __name__ == '__main__':
	from sys import argv
	main(*argv[1:])
# vim:tw=0:nowrap
