#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############   tesseract-gui.py - version 2.1   ##############################
# 
# Copyright 2009 Juan Ramon Castan <juanramoncastan at yahoo.es>
# Based in the previous work of Filip Domenic "guitesseract.py" 
# guitesseract.py
# Copyright 2008 Filip Dominec <filip.dominec at gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.#}}}


import pygtk
pygtk.require('2.0')
import gtk
import os
import pango
import sys
import subprocess
import pygtk
import string

class Whc:
	def __init__(self):
		###---Window and framework -----------------------------
		self.mainwindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.mainwindow.connect("destroy", self.destroy)
		
		self.mainwindow.set_title("Tesseract GUI")
		self.mainwindow.connect('destroy', lambda w: gtk.main_quit())
		


		self.vboxWindow = gtk.VBox(False, 1)
		self.mainwindow.add(self.vboxWindow)
		self.vboxWindow.show()

		self.hboxWindow = gtk.HBox(False, 3)
		self.vboxWindow.pack_start(self.hboxWindow,True, True, 1)
		self.hboxWindow.show()
		#---------------------------------------------------

	###---Left of Window-------------------------------------
		self.vboxLeft = gtk.VBox(False, 1)
		self.hboxWindow.pack_start(self.vboxLeft, False, True, 2)
		self.vboxLeft.show()



		#--- File Selector
		self.dlgFiles = gtk.FileChooserDialog("Select images", None,\
					        gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,\
					        gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		self.dlgFiles.set_select_multiple(True)
		self.filterFiles = gtk.FileFilter()
		self.filterFiles.add_mime_type("image/png")
		self.filterFiles.add_mime_type("image/tiff")
		self.filterFiles.add_mime_type("image/jpeg")
		self.filterFiles.add_mime_type("image/bmp")
		self.dlgFiles.add_filter(self.filterFiles)
		self.dlgFiles.connect("response", self.f_load_files)

		self.lblSelectfile = gtk.Label()
		self.lblSelectfile.set_markup("<b>Select Files</b>")
		self.vboxLeft.pack_start(self.lblSelectfile, False, False, 1)
		self.lblSelectfile.show()

		self.btnFiles = gtk.FileChooserButton(self.dlgFiles)
		self.btnFiles.set_width_chars(18)
		self.vboxLeft.pack_start(self.btnFiles, False, False, 1)
		self.btnFiles.set_filename("Abrir")
		self.btnFiles.show()

		self.lblDirectory = gtk.Label()
		self.lblDirectory.set_markup("<b>Folder</b>")
		self.vboxLeft.pack_start(self.lblDirectory, False, False, 1)
		self.lblDirectory.show()
		self.dlgDestFolder=gtk.FileChooserDialog("Select destination directory"\
								, None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER \
								, (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL\
								, gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		self.btnDirectory = gtk.FileChooserButton(self.dlgDestFolder)
		self.btnDirectory.set_current_folder(os.getenv('HOME'))
		self.btnDirectory.connect("current_folder_changed"\
												, self.f_output_filename,None)

		self.btnDirectory.set_width_chars(10)
		self.vboxLeft.pack_start(self.btnDirectory, False, False, 1)
		self.btnDirectory.show()

		#---Images List
		self.imgList = gtk.ListStore(str)

		self.treeView = gtk.TreeView(self.imgList)
		self.treeView.connect("row-activated", self.f_show_img,None,False)
		self.tvSeleccion = self.treeView.get_selection()
		self.tvSeleccion.connect("changed", self.f_show_img,None,None,None,True)
		self.cell = gtk.CellRendererText()
		self.tvColumn = gtk.TreeViewColumn("", self.cell, text=0)
		self.treeView.append_column(self.tvColumn)
		self.treeView.show()

		self.scrollFiles = gtk.ScrolledWindow()
		self.vboxLeft.pack_start(self.scrollFiles, True, True, 1)
		self.scrollFiles.set_size_request(170,100)
		self.scrollFiles.show()
		self.scrollFiles.add(self.treeView)




#-- OCR -----------------
# Pack-ends
		self.frameOcr = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameOcr, False, False, 1)
		self.frameOcr.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameOcr.show()

		self.vboxOcr = gtk.VBox(False,5)
		self.frameOcr.add(self.vboxOcr)
		self.vboxOcr.show()

		#--Page--

		self.hboxProcess = gtk.HBox(False, 3)
		self.vboxOcr.pack_end(self.hboxProcess)
		self.hboxProcess.show()

		self.btnProcess = gtk.Button("OCR",gtk.STOCK_EXECUTE,False)
		self.btnProcess.connect("clicked", self.f_process_img)
		self.hboxProcess.pack_start(self.btnProcess, False, False, 3)

		self.btnProcess.show()

		self.vboxProcess = gtk.VBox(False,1)
		self.hboxProcess.pack_end(self.vboxProcess,False, False,1)
		self.vboxProcess.show()

		self.rdAllimages = gtk.RadioButton(None,"All",False)
		self.vboxProcess.pack_start(self.rdAllimages, True, False, 1)
		self.rdAllimages.show()

		self.rdSelectedimages = gtk.RadioButton(self.rdAllimages\
															,"Selected",False)
		self.vboxProcess.pack_start(self.rdSelectedimages, True, False, 1)
		self.rdSelectedimages.show()

		self.hboxPager = gtk.HBox(False, 3)
		self.vboxOcr.pack_end(self.hboxPager, False, False,1)
		self.hboxPager.show()

		self.vboxPagePrefix = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxPagePrefix, False, False, 1)
		self.vboxPagePrefix.show()


		self.vboxPagStart = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxPagStart, False, False, 1)
		self.vboxPagStart.show()

		self.vboxPagStep = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxPagStep, False, False, 1)
		self.vboxPagStep.show()

		self.edtPagePrefix =  gtk.Entry(25)
		self.edtPagePrefix.set_text("page_")
		self.vboxPagePrefix.pack_end(self.edtPagePrefix, False, False, 1)
		self.edtPagePrefix.connect("changed", self.f_output_filename, None)
		self.edtPagePrefix.show()
		self.edtPagePrefix.set_width_chars(15)

		self.lblInit = gtk.Label()
		self.lblInit.set_markup("Index")
		self.vboxPagStart.pack_start(self.lblInit, False, False, 1)
		self.lblInit.show()

		self.edtInitPage =  gtk.SpinButton()
		self.vboxPagStart.pack_start(self.edtInitPage, False, False, 1)
		self.edtInitPage.set_adjustment(gtk.Adjustment(0, 1, 10000, 1, 1))
		self.edtInitPage.set_value(1),
		self.edtInitPage.connect("changed", self.f_output_filename, None)
		self.edtInitPage.show()


		self.lblStep = gtk.Label()
		self.lblStep.set_markup("Step")
		self.vboxPagStep.pack_start(self.lblStep, False, False, 1)
		self.lblStep.show()

		self.edtPageStep =  gtk.SpinButton()
		self.vboxPagStep.pack_start(self.edtPageStep, False, False, 1)
		self.edtPageStep.set_adjustment(gtk.Adjustment(0, 1, 4, 1, 1))
		self.edtPageStep.set_value(1),
		self.edtPageStep.connect("changed", self.f_output_filename, None)
		self.edtPageStep.show()


		self.chkPageNumbering = gtk.CheckButton("Automatic page numbering",True)
		self.vboxOcr.pack_end(self.chkPageNumbering, False, False, 1)
		self.chkPageNumbering.connect("clicked", self.f_output_filename, None)
		self.chkPageNumbering.show()

		#--Language--
		self.hboxLanguage = gtk.HBox(False, 3)
		self.vboxOcr.pack_end(self.hboxLanguage)
		self.hboxLanguage.show()

		self.cmbLang = gtk.combo_box_new_text()
		self.hboxLanguage.pack_end(self.cmbLang, False, False, 1)
		self.cmbLang.connect("changed" , self.f_lang_choice)
		self.cmbLang.show()

		self.lblLan = gtk.Label()
		self.lblLan.set_markup("Language")
		self.hboxLanguage.pack_end(self.lblLan, False, False, 1)
		self.lblLan.show()

		self.lblOcr = gtk.Label()
		self.lblOcr.set_markup("<b>OCR</b>")
		self.hboxLanguage.pack_start(self.lblOcr, False, False, 1)
		self.lblOcr.show()



		# Rotate
		self.frameRotate = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameRotate, False, False, 1)
		self.frameRotate.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameRotate.show()

		self.vboxRotate = gtk.VBox(False,5)
		self.frameRotate.add(self.vboxRotate)
		self.vboxRotate.show()

		self.hboxRotBut = gtk.HBox(False, 3)
		self.vboxRotate.pack_start(self.hboxRotBut, False, False,1)
		self.hboxRotBut.show()

		self.edtRotAngle =  gtk.SpinButton()
		self.edtRotAngle.set_text("0")
		self.hboxRotBut.pack_start(self.edtRotAngle, False, False, 1)
		self.edtRotAngle.set_width_chars(6)
		self.edtRotAngle.show()

		self.btnResRot = gtk.Button("Reset 0º")
		self.btnResRot.connect("clicked", self.f_angle_change,None, True)
		self.hboxRotBut.pack_start(self.btnResRot, False, False, 1)
		self.btnResRot.show()

		#self.lblRotate = gtk.Label()
		#self.lblRotate.set_markup(" Degrees")
		#self.hboxRotBut.pack_start(self.lblRotate, False, False, 1)
		#self.lblRotate.show()

		self.btnResRot = gtk.Button("Generallize")
		self.btnResRot.connect("clicked", self.f_generallize,5)
		self.hboxRotBut.pack_end(self.btnResRot, False, False, 1)
		self.btnResRot.show()

		self.rotateDegrees = gtk.HScrollbar()
		self.vboxRotate.pack_start(self.rotateDegrees, True, True, 1)
		self.rotateDegrees.show()
		self.rotateDegrees.set_adjustment(gtk.Adjustment\
													(0 , -720 , 721 , 1 ,1 , 1))

		self.rotateDegrees.set_value(0)
		self.rotateDegrees.connect("value-changed",self.f_angle_change2)
		self.rotateDegrees.connect("button-release-event" \
												, self.f_angle_change, False)

		# Normalize
		self.frameProc = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameProc, False, False, 1)
		self.frameProc.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameProc.show()

		self.vboxProc = gtk.VBox(False,5)
		self.frameProc.add(self.vboxProc)
		self.vboxProc.show()

		self.hboxNorm = gtk.HBox(False,5)
		self.vboxProc.pack_start(self.hboxNorm,False,False,1)
		self.hboxNorm.show()

		self.chkNormalize = gtk.CheckButton("_Normalize", True)
		self.chkNormalize.set_active(False)
		self.hboxNorm.pack_start(self.chkNormalize, False, False, 1)
		self.chkNormalize.connect("clicked", self.f_normalize_change)
		self.chkNormalize.show()

		self.btnNormalize = gtk.Button("Generallize")
		self.btnNormalize.connect("clicked", self.f_generallize,4)
		self.hboxNorm.pack_end(self.btnNormalize, False, False, 1)
		self.btnNormalize.show()

		# Crop
		self.frameCrop = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameCrop, False, False, 1)
		self.frameCrop.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameCrop.show()

		self.hboxCrop = gtk.HBox(False,5)
		self.frameCrop.add(self.hboxCrop)
		self.hboxCrop.show()

		self.vboxCropL = gtk.VBox(False,5)
		self.hboxCrop.pack_start(self.vboxCropL,False,False,1)
		self.vboxCropL.show()

		self.hboxCropL = gtk.HBox(False,5)
		self.vboxCropL.pack_start(self.hboxCropL,False,False,1)
		self.hboxCropL.show()

		self.lblCropL = gtk.Label()
		self.lblCropL.set_markup(" Left: ")
		self.hboxCropL.pack_start(self.lblCropL, False, False, 1)
		self.lblCropL.show()

		self.hboxCropT = gtk.HBox(False,5)
		self.vboxCropL.pack_start(self.hboxCropT,False,False,1)
		self.hboxCropT.show()

		self.lblCropT = gtk.Label()
		self.lblCropT.set_markup(" Top:  ")
		self.hboxCropT.pack_start(self.lblCropT, False, False, 1)
		self.lblCropT.show()

		self.vboxCropC = gtk.VBox(False,5)
		self.hboxCrop.pack_start(self.vboxCropC,True,True,1)
		self.vboxCropC.show()

		self.hboxCropR = gtk.HBox(False,5)
		self.vboxCropC.pack_start(self.hboxCropR,False,False,1)
		self.hboxCropR.show()

		self.lblCropR = gtk.Label()
		self.lblCropR.set_markup(" Right: ")
		self.hboxCropR.pack_start(self.lblCropR, False, False, 1)
		self.lblCropR.show()

		self.hboxCropB = gtk.HBox(False,5)
		self.vboxCropC.pack_start(self.hboxCropB,False,False,1)
		self.hboxCropB.show()

		self.lblCropB = gtk.Label()
		self.lblCropB.set_markup(" Bottom:  ")
		self.hboxCropB.pack_start(self.lblCropB, False, False, 1)
		self.lblCropB.show()

		self.vboxCropR = gtk.VBox(False,5)
		self.hboxCrop.pack_end(self.vboxCropR,False,True,1)
		self.vboxCropR.show()

		self.btnCrop = gtk.Button("Generallize")
		self.btnCrop.connect("clicked", self.f_generallize,6)
		self.vboxCropR.pack_end(self.btnCrop, False, False, 1)
		self.btnCrop.show()



		# Right of Window ---------------------------------
		self.vboxRight = gtk.VBox(False, 1)
		self.hboxWindow.pack_start(self.vboxRight, True, True, 2)
		self.vboxRight.show()

		self.frameInfo = gtk.Frame(None)
		self.vboxRight.pack_start(self.frameInfo, False, False, 1)
		self.frameInfo.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameInfo.show()

		self.vboxInfo = gtk.VBox(False, 1)
		self.frameInfo.add(self.vboxInfo)
		self.vboxInfo.show()

		self.hboxInfoIn = gtk.HBox(False, 1)
		self.vboxInfo.add(self.hboxInfoIn)
		self.hboxInfoIn.show()

		self.lblInfoIn = gtk.Label()
		self.lblInfoIn.set_markup("<b> Image:</b> (none)")
		self.hboxInfoIn.pack_start(self.lblInfoIn, False, False, 1)
		self.lblInfoIn.show()

		self.hboxInfoOut = gtk.HBox(False, 1)
		self.vboxInfo.add(self.hboxInfoOut)
		self.hboxInfoOut.show()

		self.lblInfoOut = gtk.Label()
		self.lblInfoOut.set_markup("<b> Text File:</b> (none)")
		self.hboxInfoOut.pack_start(self.lblInfoOut, False, False, 1)
		self.lblInfoOut.show()

		# Preview Buttons
		self.framePrevOp = gtk.Frame(None)
		self.vboxRight.pack_start(self.framePrevOp, False, False, 1)
		self.framePrevOp.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.framePrevOp.show()
		
		self.hboxPrevOp = gtk.HBox(False,1)
		self.framePrevOp.add(self.hboxPrevOp)
		self.hboxPrevOp.show()

		self.btnAutoPrev = gtk.ToggleButton("Auto Resize", False)
		self.hboxPrevOp.pack_start(self.btnAutoPrev, False, False, 1)
		self.btnAutoPrev.connect("clicked", self.f_show_buttons)
		self.btnAutoPrev.set_mode(True)
		self.btnAutoPrev.show()

		self.btnPrevMax = gtk.Button("",gtk.STOCK_ZOOM_FIT,False)
		self.btnPrevMax.connect("clicked", self.f_show_img,None,None,None,False)
		self.hboxPrevOp.pack_start(self.btnPrevMax, False, False, 1)
		self.btnPrevMax.show()

		self.btnPrevPlus = gtk.Button("",gtk.STOCK_ZOOM_IN,False)
		self.btnPrevPlus.connect("clicked", self.f_show_img,None,None,1.1,False)
		self.hboxPrevOp.pack_start(self.btnPrevPlus, False, False, 1)
		self.btnPrevPlus.show()

		self.btnPrevMinus = gtk.Button("",gtk.STOCK_ZOOM_OUT,False)
		self.btnPrevMinus.connect("clicked", self.f_show_img,None,None,0.9,False)
		self.hboxPrevOp.pack_start(self.btnPrevMinus, False, False, 1)
		self.btnPrevMinus.show()


		#---Show Window
		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
		self.vboxRight.pack_start(self.scrolledwindow, True, True, 2)
		self.scrolledwindow.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
		#self.scrolledwindow.connect("button-press-event", self.f_coord)
		#self.scrolledwindow.set_size_request(400,100)
		self.scrolledwindow.show()

		self.drawingArea = gtk.DrawingArea()
		self.drawingArea.set_size_request(0,0)
		self.drawingArea.set_events(gtk.gdk.EXPOSURE_MASK \
			| gtk.gdk.LEAVE_NOTIFY_MASK | gtk.gdk.BUTTON_PRESS_MASK \
			| gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK \
			| gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_RELEASE \
			| gtk.gdk.MOTION_NOTIFY )
		                        
		self.drawingArea.connect("expose-event",self.f_redraw_area)
		self.drawingArea.connect("button_press_event",self.f_init_rect,1)
		self.drawingArea.connect("button_release_event",self.f_init_rect,0)
		self.drawingArea.connect("motion_notify_event",self.f_draw_rect,1)
		self.scrolledwindow.add_with_viewport(self.drawingArea)
		self.drawingArea.show()


		# Show the window-------------------------------------------------------
		self.mainwindow.show()
		self.f_init_variables()
		self.f_create_lang()
		
	# __init__ END

################################################################################
### Functions-------------------------------------------------------------------
	### Importatnt Functions ---------------------------------------------------
	def f_init_variables(self):
		print "reseting variables..."
		#self.imgList.clear()
		self.Scale=None
		self.LeftWinW=280
		self.Images=[]
		self.ImageWidth=None
		self.ImageHeight=None
		self.Selected=None
		self.pixBuf=None
		self.pixBufPrev=None
		self.Pressed=None
		self.rectangle=None
		self.Home = os.environ["HOME"] + "/"
		self.ConfFile = ".tesseract-guirc"
		self.f_read_conf()

	#}} f_init_variables END

	def f_load_files(self, widget, Data):
		self.f_init_variables()
		self.imgList.clear()
		self.DirectoryIn = self.dlgFiles.get_current_folder() + "/"
		self.FolderOut= self.DirectoryIn
		self.btnDirectory.set_current_folder(self.FolderOut) # Output Folder
		self.tvColumn.set_title(self.DirectoryIn) # Column Title
		self.Files=self.dlgFiles.get_filenames()
		if self.Files :
			print "\nLoading images from: " + self.DirectoryIn
			nnfin = len(self.Files)
			for nn in range(0,nnfin) :
				File = self.Files[nn]
				(Path,Image) = File.rsplit("/",1)
				(Name,Ext) = Image.rsplit(".",1)
				Ext = "." + Ext
				self.imgList.append([Image])
				#### Images is a list:
	            # 0=Index
				# 1=Image
				# 2=Name
				# 3=Extension
				# 4=Normalize
				# 5=Rotate
				# (6=Rectangles)[n]
				if self.chkNormalize.get_active() == True : Norm = True
				else : Norm = False
				rect=None 
				self.Images.append([nn,Image,Name,Ext,Norm,0,[rect]])
				print " " + Image
	#}} f_load_files END

	def f_show_img(self,widget,Data,Data2,Zoom,WritePrev):
		#----- Image = (self.Images[self.Selected])[1]
		#----- Name = (self.Images[self.Selected])[2]
		#----- Ext = (self.Images[self.Selected])[3]
		#----- Norm = (self.Images[self.Selected])[4]
		#----- Rotate = (self.Images[self.Selected])[5]
		#----- Rect = (self.Images[self.Selected])[6]
		                                            
		self.f_select_img()

		ScrolledWidth = int((self.scrolledwindow.window.get_size()[0])\
																- self.LeftWinW)

		if self.Selected != None:
			self.f_output_filename(None,self.Selected)
			Index = (self.Images[self.Selected])[0]
			Image = (self.Images[self.Selected])[1]
			Name = (self.Images[self.Selected])[2]
			Ext = (self.Images[self.Selected])[3]
			Norm = (self.Images[self.Selected])[4]
			Rotate = (self.Images[self.Selected])[5]
			Rect = (self.Images[self.Selected])[6]
			# print "Image " + str(Index) + ": "+self.DirectoryIn +Image

			self.chkNormalize.set_active(Norm)
			self.rotateDegrees.set_value(int(float(Rotate) / 0.25))
			self.rectangle = Rect[0]
			#self.chkNormalize.set_active(Norm)

			if WritePrev == True:
				rotate_option = self.f_opRotate(Index)
				normalize_option = self.f_opNormalize(Index)
				options= normalize_option + " " + rotate_option 
				runBash("convert -quality 80 " + options + " '" \
											+ self.DirectoryIn + Image \
											+ "' '/tmp/tesseract_preview.jpg'")

				self.pixBuf=gtk.gdk.pixbuf_new_from_file\
												("/tmp/tesseract_preview.jpg")

				self.ImageW = self.pixBuf.get_width()
				self.ImageH = self.pixBuf.get_height()

			if Zoom and self.Scale:
				self.Scale = self.Scale * Zoom
			else:
				self.Scale = (float(ScrolledWidth) / float(self.ImageW))

			self.Interp = gtk.gdk.INTERP_NEAREST

			self.drawingArea.set_size_request(int(self.ImageW * self.Scale)\
												,int(self.ImageH * self.Scale))

			self.pixBufPrev = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8\
												,int(self.ImageW*self.Scale)\
												,int(self.ImageH*self.Scale))

			self.pixBuf.scale(self.pixBufPrev,0,0,int(self.ImageW * self.Scale)\
											,int(self.ImageH * self.Scale),0,0\
											,self.Scale,self.Scale,self.Interp)

			self.f_redraw_area(self,None)
	#}} f_show_img END

	def f_redraw_area(self, widget, event):
		gc = self.drawingArea.get_style().fg_gc[gtk.STATE_NORMAL]

		colormap= self.drawingArea.get_colormap()
		color = colormap.alloc_color(40000,0,0,False,False)
		gcArea = self.drawingArea.window.new_gc()
		gcArea.set_foreground(color)
		gcArea.set_dashes(15, (6,6))
		gcArea.line_width = 2
		gcArea.line_style = gtk.gdk.LINE_ON_OFF_DASH

		gcHand = self.drawingArea.window.new_gc()
		gcHand.set_foreground(color)
		gcHand.line_width = 3
		gcHand.line_style = gtk.gdk.SOLID
		gcHand.fill = gtk.gdk.SOLID

		if self.pixBufPrev:
			ScrolledWidth = int((self.scrolledwindow.window.get_size()[0]) \
																- self.LeftWinW)
			Scale = self.Scale
			if self.btnAutoPrev.get_active() == True:
				Scale = (float(ScrolledWidth) / float(self.ImageW))
				self.pixBufPrev = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8\
								,int(self.ImageW*Scale),int(self.ImageH*Scale))

				self.pixBuf.scale(self.pixBufPrev,0,0,int(self.ImageW*Scale)\
							,int(self.ImageH*Scale),0,0,Scale,Scale,self.Interp)

				self.drawingArea.set_size_request(int(self.ImageW * Scale)\
													,int(self.ImageH * Scale))

			self.drawingArea.window.draw_pixbuf(gc, self.pixBufPrev, 0, 0, 0, 0)


			if self.rectangle :
				x = self.rectangle.x
				y = self.rectangle.y
				xx = (self.rectangle.x + self.rectangle.width)
				yy = (self.rectangle.y + self.rectangle.height)
				w = self.rectangle.width
				h = self.rectangle.height
				rectx = int(x * Scale)
				recty = int(y * Scale)
				rectxx = int((x + w) * Scale)
				rectyy = int((y + h) * Scale)
				rectw = int(w * Scale)
				recth = int(h * Scale)
				self.lblCropL.set_markup(" Left: " + str(x))
				self.lblCropR.set_markup(" Right: " + str(xx))
				self.lblCropT.set_markup(" Top: " + str(y))
				self.lblCropB.set_markup(" Bottom: " + str(yy))
				self.drawingArea.window.draw_rectangle( gcArea , False \
												, rectx , recty , rectw , recth)

				self.drawingArea.window.draw_rectangle( gcHand , False \
										, (rectx + 5) , (recty + 5 ) , 10 ,10)

				self.drawingArea.window.draw_rectangle( gcHand , False \
											, (rectxx-7) , ( rectyy-7) , 5 , 5 )
			else:
				self.lblCropL.set_markup(" Left: ")
				self.lblCropR.set_markup(" Right: ")
				self.lblCropT.set_markup(" Top: ")
				self.lblCropB.set_markup(" Bottom: ")
			self.Scale = Scale
	#}} f_redraw_area END

	def f_process_img(self,widget):
		ImagesToProcess=[]
		if self.rdAllimages.get_active() :
			if self.Images: ImagesToProcess = self.Images
		elif self.rdSelectedimages.get_active() :
			if self.Selected != None : ImagesToProcess.append(\
													self.Images[self.Selected])
		else:
			ImagesToProcess=None

		if ImagesToProcess:
			nnfin = len(ImagesToProcess)
			for nn in range(0,nnfin):
				Index = (ImagesToProcess[nn])[0]
				Image = (ImagesToProcess[nn])[1]
				Name = (ImagesToProcess[nn])[2]
				Ext = (ImagesToProcess[nn])[3]
				Norm = (ImagesToProcess[nn])[4]
				Rotate = (ImagesToProcess[nn])[5]
				Rect = (ImagesToProcess[nn])[6]

				normalize_option = self.f_opNormalize(Index)
				rotate_option = self.f_opRotate(Index)
				crop_option = self.f_opCrop(Index)
				options= rotate_option +" "+crop_option + " " + normalize_option
				NameOut = self.f_output_filename(None,Index)
				FileIn = self.DirectoryIn + Image
				Processtif = "/tmp/tesseract_process"+str(nn)+".tif"
				Processjpg = "/tmp/tesseract_process"+str(nn)+".jpg"

				runBash("convert -compress None '" + FileIn + "' " \
											+ rotate_option + " " + Processtif )

				runBash("mogrify " + normalize_option + " " + Processtif )
				runBash("mogrify " + crop_option + " "  + Processtif )
				runBash("mogrify -antialias " + Processtif )
				runBash("mogrify -monochrome " + Processtif )
                                                      
				runBash("tesseract '" + Processtif + "' '" + self.FolderOut  \
													+ NameOut + "' -l " + lang )

				print "Recognition: "+self.FolderOut+NameOut+"' Language: "+lang
				#runBash("rm " + Processtif)
			print "Text Recogniton Finished !!!!"
			self.f_dialog("Text Recogniton Finished !!!!")
	# f_process_img END

	### Secondary Functions-----------------------------------------------------
	def f_select_img(self):
		if self.tvSeleccion.get_selected_rows()[1] != []:
			Sel = self.tvSeleccion.get_selected_rows()[1]
			Selected = ((self.tvSeleccion.get_selected_rows()[1])[0])[0]
			self.Selected = Selected
			return Selected
	#}} f_select_img END

	def f_output_filename(self,widget,Index):
		self.f_destination_folder(self,None)
		NameOut = "name of file"
		if self.Images:
			if Index == None : 
				Index = self.Selected
			if self.chkPageNumbering.get_active() == True:
				if Index != None and self.edtInitPage.get_text() != '': 
					Page = (int(self.edtInitPage.get_text()) \
								+ (int(self.edtPageStep.get_text() )*Index ))

					NameOut = (self.edtPagePrefix.get_text() + str( Page ) ) 
                                           
				else:
					NameOut = self.edtPagePrefix.get_text() + "(index)"
			else:
				if Index != None :
					NameOut = (self.Images[Index])[2]
					self.lblInfoIn.set_markup("<b> Image:</b> "\
									+ self.DirectoryIn + (self.Images[Index])[1])
				else:
					self.lblInfoIn.set_markup("<b>Image:</b> "\
											+ self.DirectoryIn + "Name of File")

			self.lblInfoOut.set_markup("<b> Text File:</b> " \
										+ self.FolderOut  + NameOut + ".txt")

			return NameOut
	#}} f_output_filename END

	def f_destination_folder(self,widget,Data):
		if self.Images :
			self.FolderOut = self.btnDirectory.get_current_folder() + "/"
			return self.FolderOut		
	#}} f_destination_folder END

	def f_show_buttons(self,widget):
		if self.btnAutoPrev.get_active() == True:
			self.btnPrevMinus.hide()
			self.btnPrevMax.hide()
			self.btnPrevPlus.hide()
		if self.btnAutoPrev.get_active() == False:
			self.btnPrevMinus.show()
			self.btnPrevMax.show()
			self.btnPrevPlus.show()
			self.f_show_img(None,None,None,None,False)
	#}} f_show_buttons END

	def f_angle_change(self , widget,Dato, Reset):
		if Reset: self.rotateDegrees.set_value(0)
		angle = (int (self.rotateDegrees.get_value()) * 0.25 )
		angulo = str(angle)
		self.f_angle_change2(None)
		if self.Selected != None:
			(self.Images[self.Selected])[5] = angulo
		self.f_show_img(None,None,None,1,True)
	# f_angle_change END

	def f_angle_change2(self,widget):
		self.edtRotAngle.set_text(str(int(self.rotateDegrees.get_value())*0.25))
	# f_angle_change2 END

	def f_normalize_change(self,widget):
		if self.Selected != None:
			(self.Images[self.Selected])[4] = self.chkNormalize.get_active()
		self.f_show_img(None,None,None,1,True)
	# f_normalize_change END

	def f_init_rect(self,widget,dato, Evento):
		self.x=None
		self.y=None
		
		self.AreaAction="resize"
		self.Pressed = Evento
		if self.Pressed == 1:
			Pressx , Pressy , Nada= self.drawingArea.window.get_pointer()
			self.Pressx = Pressx
			self.Pressy = Pressy
			if self.Selected != None:
				self.rectangle = ((self.Images[self.Selected])[6])[0]
				if self.rectangle :
					self.Pressx=None
					self.Pressy=None
					#self.Pressed=0
					self.x = int((self.rectangle.x) * self.Scale)
					self.y = int((self.rectangle.y)* self.Scale)
					self.xx = int((self.rectangle.x + self.rectangle.width) \
																* self.Scale)

					self.yy = int((self.rectangle.y + self.rectangle.height) \
																* self.Scale)

					if Pressx < (self.xx) and Pressy < (self.yy) and Pressx > \
												(self.x) and Pressy > (self.y) :
	
						self.drawingArea.window.set_cursor(\
												gtk.gdk.Cursor(gtk.gdk.FLEUR))

						self.AreaAction = "move"
						self.Pressx = Pressx
						self.Pressy = Pressy
					if Pressx > (self.x + 6) and Pressy > (self.y + 6)  and \
							Pressx < (self.x  + 16) and Pressy < (self.y + 16) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
															(gtk.gdk.X_CURSOR))

						self.AreaAction="clear"
						self.Pressx=None
						self.Pressy=None
						self.rectangle=None
						((self.Images[self.Selected])[6])[0] = None
						self.f_redraw_area(self,None)
					if Pressx < (self.xx) and Pressy < (self.yy) and \
							Pressx > (self.xx - 7) and Pressy > (self.yy - 7) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
												(gtk.gdk.BOTTOM_RIGHT_CORNER))

						self.AreaAction = "resize"
						self.Rectx = self.x
						self.Recty = self.y
		if self.Pressed == 0:
			self.drawingArea.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
		self.f_show_img(None,None,None,1,False)
	# f_init_rect END

	def f_draw_rect(self,widget,dato, evento):
		if self.Selected != None:
			Movex , Movey , Nada= self.drawingArea.window.get_pointer()

			self.rectangle = ((self.Images[self.Selected])[6])[0]
			if self.Pressed == 0:
				if self.rectangle:
					x = int((self.rectangle.x) * self.Scale)
					y = int((self.rectangle.y)* self.Scale)
					xx = int((self.rectangle.x + self.rectangle.width) \
																* self.Scale)

					yy = int((self.rectangle.y + self.rectangle.height) \
																* self.Scale)

					self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
																(gtk.gdk.ARROW))
					if Movex < (xx) and Movey < (yy) and Movex > (x) and \
																Movey > (y) :
	
						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
																(gtk.gdk.HAND1))

					if Movex > (x + 6) and Movey > (y + 6)  and Movex < \
												(x  + 16) and Movey < (y + 16) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
															(gtk.gdk.X_CURSOR))
					if Movex < (xx) and Movey < (yy) and Movex > (xx - 7) and \
															Movey > (yy - 7) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
																(gtk.gdk.HAND2))

			if self.Pressed == 1:
				if self.Pressx and self.Pressy :
					if self.x == None : self.x = self.Pressx
					if self.y == None : self.y = self.Pressy
					if self.rectangle:
						x = int((self.rectangle.x) * self.Scale)
						y = int((self.rectangle.y)* self.Scale)
						xx = int((self.rectangle.x + self.rectangle.width) \
																* self.Scale)

						yy = int((self.rectangle.y + self.rectangle.height) \
																* self.Scale)

						if self.AreaAction == "resize":
							self.Rectxx = xx - (xx - Movex) 
							self.Rectyy = yy - (yy - Movey)
							if Movex < self.x :
								self.Rectxx = self.x
								self.Rectx = Movex
							if Movey < self.y :
								self.Rectyy = self.y
								self.Recty =  Movey

						elif self.AreaAction == "move":
							if self.x + (Movex - self.Pressx) > 0 :
								#if Movex == None: Movex = 0
								self.Rectx = self.x + (Movex - self.Pressx)
							else:
								self.Rect = 0
							if self.y + (Movey - self.Pressy) > 0  :
								self.Recty = self.y + (Movey - self.Pressy)
							else:
								self.Recty = 0
							if int((self.xx + (Movex - self.Pressx))  \
													/ self.Scale) < self.ImageW:

								self.Rectxx = self.xx + (Movex - self.Pressx)
							else:
								self.Rectxx = int(self.ImageW  * self.Scale)
							if int((self.yy + (Movey - self.Pressy))  \
													/ self.Scale) < self.ImageH:

								self.Rectyy = self.yy + (Movey - self.Pressy)
							else:
								self.Rectyy = int(self.ImageH  * self.Scale)
					else:
						self.Rectx = self.Pressx
						self.Recty = self.Pressy
						self.Rectxx = Movex
						self.Rectyy = Movey
						
						
					cropx = int(self.Rectx / self.Scale)
					cropy = int(self.Recty  / self.Scale)
					cropxx = int(self.Rectxx  / self.Scale)
					cropyy = int(self.Rectyy  / self.Scale)
					if cropx < 0 : cropx = 0
					if cropy < 0 : cropy = 0
					if cropxx > self.ImageW : cropxx = self.ImageW
					if cropyy > self.ImageH : cropyy = self.ImageH
					cropw = cropxx - cropx
					croph = cropyy - cropy

					self.rectangle = gtk.gdk.Rectangle(cropx,cropy,cropw,croph)

					((self.Images[self.Selected])[6])[0] = self.rectangle
					
					self.f_redraw_area(self,None)
	# f_draw_rect END

	def f_generallize(self,widget,Nn):
		nnfin = len(self.Images)
		for nn in range(0,nnfin):
			if Nn == 6 :
				((self.Images[nn])[Nn])[0]=((self.Images[self.Selected])[Nn])[0]
			else:
				(self.Images[nn])[Nn] = (self.Images[self.Selected])[Nn]
		self.f_show_img(None,None,None,1,False)
	# f_generallize END

	def f_create_lang(self):
		Languages = { "Spanish":"spa",\
					"Portuguese":"por",\
					"Italian":"ita",\
					"Dutch":"nld",\
					"German":"deu",\
					"French":"fra",\
					"English":"eng"}
		self.ListLanguages={}
		nnfin=len(Languages)
		Nn=0
		for nn in range (0,nnfin):
			LangExist = runBash("ls /usr/share/tesseract-ocr/tessdata/" \
						+ (Languages.values()[nn]) + ".unicharset 2> /dev/null")
			if LangExist :
				self.ListLanguages[Languages.keys()[nn]]=Languages.values()[nn]
				self.cmbLang.append_text(Languages.keys()[nn])
				if self.ConfVars["Language"] == Languages.keys()[nn]:
					self.cmbLang.set_active(Nn)
				Nn = Nn + 1
	# f_create_lang END

	def f_lang_choice(self , widget): 
		global lang
		model = self.cmbLang.get_model()
		active = self.cmbLang.get_active()
		if active < 0:
			return None
		lang = self.ListLanguages[(model[active][0])]
		self.ConfVars["Language"]= model[active][0] + "\n"
		self.f_write_conf()
	# f_lang_coice END

	def f_read_conf(self):
		self.ConfVars={}
		try :
			Conff = open(self.Home+self.ConfFile, "r")
			lineas = Conff.readlines()
			nnfin = len(lineas)
			for nn in range(0,nnfin):
				if lineas[nn] == "\n": lineas[nn] = None
				if lineas[nn] :
					linea = lineas[nn].rstrip("\n")
					(Key,Value) = linea.split("=",1)
					self.ConfVars[Key] = Value
				nn = nn+1
			Conff.close() 
		except IOError:
			nn = 0
			self.ConfVars = {"Language":"English" \
							, "Normalize":"True"}
			Conff = open(self.Home+self.ConfFile, "w")
			nnfin = len(self.ConfVars)
			for nn in range(0,nnfin):
				Par =  self.ConfVars.keys()[nn]+"="+self.ConfVars.values()[nn]
				Conff.write(Par+"\n")
				nn = nn+1
			Conff.write("\n")
			Conff.close()
		if "Normalize" not in self.ConfVars :
			self.ConfVars["Normalize"] = "True"

		if (self.ConfVars["Normalize"] == "True" \
										or self.ConfVars["Normalize"] == "Yes"):

			self.ConfVars["Normalize"] = "True"
			self.chkNormalize.set_active(True)
		else:
			self.chkNormalize.set_active(False)
	# f_read_conf END

	def f_write_conf(self):
		Conff = open(self.Home+self.ConfFile, "w")
		nnfin = len(self.ConfVars)
		for nn in range(0,nnfin):
			Par =  self.ConfVars.keys()[nn]+"="+self.ConfVars.values()[nn]
			Conff.write(Par+"\n")
			nn = nn+1
		Conff.close()
	# f_write_conf END

	def f_dialog(self,Data):
		self.processdialog = gtk.Dialog("Processing",self.mainwindow\
			,gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

		self.processdialog.connect("response",self.f_dialog_destroy)
		self.lblProcessDialog = gtk.Label()
		self.lblProcessDialog.set_markup(Data)
		self.processdialog.action_area.pack_start(self.lblProcessDialog \
															, False, False, 1)

		self.lblProcessDialog.show()
		self.processdialog.show()
	def f_dialog_destroy(self,widget,Data=None):
		self.processdialog.destroy()


	### Process Options -------------------------
 	def f_opRotate(self,Nn):
		rotate_option = ""
		if (self.Images[Nn])[5] != 0: 
			rotate_option = "-rotate " + str((self.Images[Nn])[5])
		return rotate_option
	# f_opRotate END

	def f_opNormalize(self,Nn):	
		normalize_option = ""
		if (self.Images[Nn])[4] == True: normalize_option = "-normalize" 
		return normalize_option
	# f_opNormalize END

	def f_opCrop(self,Nn):
		crop_option = ""
		if ((self.Images[Nn])[6])[0]:
			rectangle = (((self.Images[Nn])[6])[0])
			x = str(rectangle.x)
			y = str(rectangle.y)
			w = str(rectangle.width)
			h = str(rectangle.height)
			crop_option = "-crop " + w + "x" + h + "+" + x + "+" + y
		return crop_option
	# f_crop_option END

	def destroy(self, widget, data=None):	# exit when main window closed
		gtk.main_quit()
	#}} destroy END

	def main(self):
		gtk.main()
	# main end
	# __init__ END
# Whc END 

# Funciones globales------------------------------------------------------------
def runBash(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	out = p.stdout.read().strip()
	return out
# runBash END

if __name__ == "__main__": 
	base = Whc()
    	base.main()

