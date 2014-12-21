#!/usr/bin/env python
from Image import frombytes, open as fromfile
from ImageTk import PhotoImage
from ImageOps import invert, autocontrast, grayscale
from select import select
from v4l2capture import Video_device
from time import time
from Tkinter import Frame, Button, Tk, Label, Canvas, BOTH, TOP
from os.path import exists

# TODO:
# - get v4l properties (sizes & fps)
# - set v4l properties (contrast, hue, sat, ..)
# - get event from usb dev

def ascii_increment(val):
	a = ord('a')
	i = (ord(val[0]) - a) * 26 + (ord(val[1]) - a)
	i += 1
	return chr(a + i / 26) + chr(a + i % 26)

class Cap(Frame):
	def __init__(self):
		self.role = 'aa'
		self.serial = 0
		self.invert = True
		self.bw = True
		self.ac = True
		self.videodevice = '/dev/video1'
		self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
		while exists(self.filename):
			self.serial += 1
			self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
		self.root = Tk()
		self.root.bind('<Destroy>', self.stop_video)
		Frame.__init__(self, self.root)
		self.root.bind("<space>", self.single_shot)
		self.root.bind("<Return>", self.single_shot)
		self.root.bind("q", self.quit)
		self.pack()
		self.canvas = Canvas(self, width=640, height=480, )
		self.canvas.pack(side='top')
		self.resetrole = Button(self, text='First role', command=self.first_role)
		self.resetrole.pack(side='left')
		self.fnl = Label(self, text=self.filename)
		self.fnl.pack(side='left')
		self.nextrole = Button(self, text='Next role', command=self.inc_role)
		self.nextrole.pack(side='left')
		self.take = Button(self, text='Take!', command=self.single_shot)
		self.take.pack(side='right')
		self.video = None
		self.start_video()

	def first_role(self):
		self.serial = 0
		self.role = 'aa'
		self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
		while exists(self.filename):
			self.serial += 1
			self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
		self.fnl['text'] = self.filename

	def inc_role(self):
		self.serial = 0
		self.role = ascii_increment(self.role)
		self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
		while exists(self.filename):
			self.serial += 1
			self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
		self.fnl['text'] = self.filename

	def set_pauseimage(self):
		self.image = fromfile('image.png')
		self.photo = PhotoImage(self.image)
		self.canvas.create_image(320, 240, image=self.photo)

	def quit(self, event):
		self.root.destroy()

	def stop_video(self, *args):
		if self.video is not None:
			self.video.stop()
			self.video.close()
			self.video = None

	def start_video(self):
		if self.video is not None:
			self.stop_video()
		self.video = Video_device(self.videodevice)
		self.video.set_format(640, 480)
		self.video.create_buffers(30)
		self.video.queue_all_buffers()
		self.video.start()
		#width, height, mode = self.video.get_format() # YCbCr
		self.root.after(1, self.live_view)

	def live_view(self, delta=3.0):
		if self.video is not None:
			select((self.video,), (), ())
			data = self.video.read_and_queue()
			self.image = frombytes('RGB', (640, 480), data)
			if self.invert:
				self.image = invert(self.image)
			if self.bw:
				self.image = grayscale(self.image)
			if self.ac:
				self.image = autocontrast(self.image)
			self.photo = PhotoImage(self.image)
			self.canvas.create_image(320, 240, image=self.photo)
			self.root.after(1, self.live_view)

	def single_shot(self, *args):
		def go():
			self.video = Video_device(self.videodevice)
			try:
				width, height = self.video.set_format(2592, 1944)
				mode = 'RGB'
				self.video.create_buffers(7)
				self.video.queue_all_buffers()
				self.video.start()
				for n in range(7): # wait for auto
					select((self.video, ), (), ())
					data = self.video.read_and_queue()
				image = frombytes(mode, (width, height), data)
				if self.invert:
					image = invert(image)
				if self.bw:
					image = grayscale(image)
				if self.ac:
					image = autocontrast(image)
				image.save(self.filename)
				self.serial += 1
				self.filename = 'scanned.{}-{:04}.jpg'.format(self.role, self.serial, )
				self.fnl['text'] = self.filename
				self.video.stop()
			finally:
				self.video.close()
				self.video = None
			self.root.after(10, self.start_video)
		self.stop_video()
		self.set_pauseimage()
		self.root.after(10, go)


app = Cap()
app.mainloop()
exit(0)