#!/usr/bin/env python

import cairo
import gtk
import subprocess
import time
import os

# Gif length (SECS)
DURATION = 10

class Point:
	def __init__(self, x=0, y=0):
		self.update([x, y])
	def update(self, coords):
		self.x = coords[0]
		self.y = coords[1]
	def __str__(self):
		return '( %f, %f )' % (self.x, self.y)

class Rect:
	def __init__(self, start, end):
		self.x = min(start.x, end.x)
		self.y = min(start.y, end.y)
		self.w = abs(end.x - start.x)
		self.h = abs(end.y - start.y)
	def args(self):
		return ( self.x, self.y, self.w, self.h )

class MyWin (gtk.Window):
	def __init__(self):
		super(MyWin, self).__init__()
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_decorated(False)
		self.set_has_frame(False)
		self.set_app_paintable(True)

		self.image = None # Preview
		self.start_h = None # Start-on-enter handle_id
		self.cr = None # cairo context
		self.rect = None # our Rect object

		self.mouse_down = False
		self.start = Point()
		self.end = Point()


		self.screen = self.get_screen()
		colormap = self.screen.get_rgba_colormap()
		if (colormap is not None and self.screen.is_composited()):
				self.set_colormap(colormap)

		self.connect("button_press_event", self.mouse_press)
		self.connect("button_release_event", self.mouse_release)
		self.connect("motion_notify_event", self.mouse_move)
		self.connect("expose-event", self.expose)
		self.connect("key-press-event", self.key_press)
		self.connect("destroy", gtk.main_quit)

		self.set_events(gtk.gdk.EXPOSURE_MASK
								 | gtk.gdk.LEAVE_NOTIFY_MASK
								 | gtk.gdk.BUTTON_PRESS_MASK
								 | gtk.gdk.BUTTON_RELEASE_MASK
								 | gtk.gdk.POINTER_MOTION_MASK
								 | gtk.gdk.POINTER_MOTION_HINT_MASK)


		self.fullscreen()
		self.show_all()

	def key_press(self, window, event):
		k = event.keyval

		if k == gtk.keysyms.Escape:
			gtk.main_quit()
		elif k == gtk.keysyms.Return or k == gtk.keysyms.space:
			if self.rect and not self.mouse_down:
				self.start_capture(window, event)

	def start_capture(self, window, event):
		'''Start byzanz subprocess'''
		print 'Starting byzanz' 
		
		# Hide window
		window.hide()
		self.clear()

		# Generate save path
		t = time.localtime()
		fpath = os.path.expanduser('~/Pictures')
		fpath += "/Gif from %d-%d-%d %d:%d:%d.gif" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

		# Start process
		settings = '--duration=%d ' % DURATION + '--x=%d --y=%d --width=%d --height=%d ' % self.rect.args()
		settings += fpath.replace(' ', '\ ')
		print settings
		subprocess.call('byzanz-record %s' % settings, shell=True)
	   
		# Re-show window
		window.show()
		window.present()
		self.rect = None

		# Check out what we made
		if os.path.isfile(fpath):
			self.show_preview(fpath)

	def show_preview(self, f):
		'''Display last created GIF'''
		print 'Getting preview'
		pixbufanim = gtk.gdk.PixbufAnimation(f)
		self.image = gtk.Image()
		self.image.set_from_animation(pixbufanim)
		self.image.show()
		self.add(self.image)
		self.show()

	def mouse_release(self, widget, event): self.mouse_down = False
	def mouse_press(self, widget, event):   
		self.mouse_down = True
		self.start.update(event.get_coords())
		if self.image: 
			self.image.destroy()
			self.image = None

	def mouse_move(self, widget, event):
		if self.mouse_down:
			self.end.update(event.get_coords())
			self.rect = Rect(self.start, self.end)
			widget.queue_draw_area(0, 0, *self.get_size())

	
	#
	# Cairo context routines
	#
	def clear(self):		
		# Transparent background
		self.cr.set_operator(cairo.OPERATOR_SOURCE)
		self.cr.set_source_rgba(0.2, 0.2, 0.2, 0.5)
		self.cr.rectangle(0.0, 0.0, *self.get_size())
		self.cr.fill()

	def update_status(self):
		self.cr.set_operator(cairo.OPERATOR_OVER)
		self.cr.set_source_rgb(1, 1, 0)
		self.cr.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		self.cr.set_font_size(14)
		(x, y, width, height, dx, dy) = self.cr.text_extents(self.status)
		self.cr.move_to(self.get_size()[0]/2.0 - width/2, 20)
		self.cr.show_text(self.status)
		self.cr.stroke()

	def update_rect(self):
		'''Outline selection'''
		self.cr.set_operator(cairo.OPERATOR_DEST_OUT)
		self.cr.set_source_rgba(0.2, 0.2, 0.2, 1);
		self.cr.rectangle( *self.rect.args() )
		self.cr.fill()


	def expose(self, widget, event):
		self.cr = widget.window.cairo_create()
		self.clear()

		if self.rect:
			self.update_rect()
			self.status = 'Press Space/Return to begin capturing. Escape to exit.'
		else:
			self.status = 'Click and drag to outline your GIF'

		self.update_status()

MyWin()
gtk.main()