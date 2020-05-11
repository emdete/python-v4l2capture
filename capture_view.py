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
from tkinter import Frame, Button, Tk, Label, Canvas, BOTH, TOP, Checkbutton, OptionMenu, StringVar, BooleanVar, Menu, IntVar, LEFT, RIGHT, TOP
from v4l2capture import Video_device

def cmp(a, b):
	return (a > b) - (a < b)

class Cap(Frame):
	def __init__(self):
		self.root = Tk()
		self.root.bind('q', lambda e: self.root.quit())
		Frame.__init__(self, self.root)
		self.x_canvas = Canvas(self.root, width=800, height=800, )
		self.x_canvas.pack(side=TOP)
		self.video = None
		self.do_start_video()

	def do_stop_video(self, *args):
		if self.video is not None:
			self.video.stop()
			self.video.close()
			self.video = None

	def do_start_video(self, *args):
		if self.video is None:
			self.video = Video_device('/dev/video0')
			_, _, self.fourcc = self.video.get_format()
			print('fourcc', self.fourcc)
			caps = self.video.get_framesizes(self.fourcc)
			caps = sorted(caps, key=cmp_to_key(lambda a, b: cmp(a['size_x']*a['size_y'], b['size_x']*b['size_y'])))
			print('caps', caps)
			self.framesize = caps[len(caps)//2]
			print('framesize', self.framesize)
			self.framesize['size_x'], self.framesize['size_y'] = self.video.set_format(self.framesize['size_x'], self.framesize['size_y'], 0, 'MJPEG')
			try: self.video.set_auto_white_balance(True)
			except: print('error setting wb')
			try: self.video.set_exposure_absolute(600) # self.video.set_exposure_auto(True)
			except: print('error setting ae')
			try: self.video.set_focus_auto(True)
			except: print('error setting af')
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

def main():
	' main start point of the program '
	app = Cap()
	app.mainloop()
	app.root.destroy()

if __name__ == '__main__':
	from sys import argv
	main(*argv[1:])
# vim:tw=0:nowrap
