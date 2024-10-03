#!/usr/bin/env python

import logging
import os
import shutil
import signal
import subprocess
import sys
import traceback

def recursive_copy(src_dir, dest_dir):
	if not os.path.exists(dest_dir):
		shutil.copytree(src_dir, dest_dir)
	else:
		files = os.listdir(src_dir)
		for file in files:
			src_file = src_dir + '/' + file
			dest_file = dest_dir + '/' + file
			if os.path.isdir(src_file):
				recursive_copy(src_file,  dest_file)
			else:
				shutil.copy2(src_file, dest_file)

try:
	logging.basicConfig(filename='debug.log',level=logging.INFO)
	logger = logging.getLogger("install_scale_ui_mod.py")
	LINUX = False
	CWD = os.getcwd()
	PROGRAM_BASE = os.environ.get("ProgramFiles(x86)")
	if PROGRAM_BASE is None:
		PROGRAM_BASE = os.environ.get("HOME")
		PROGRAM_BASE = os.path.join(PROGRAM_BASE, ".local/share")
		if os.path.exists(PROGRAM_BASE):
			LINUX = True
	logger.info("USER_HOME = {}".format(CWD))
	logger.info("PROGRAM_BASE = {}".format(PROGRAM_BASE))

	# Determine GIMP install directory
	GIMP_HOME = os.path.normpath("C:\Program Files\GIMP 2")
	if not os.path.exists(GIMP_HOME):
		GIMP_HOME = os.path.normpath("C:\Program Files\GIMP")
	if not os.path.exists(GIMP_HOME):
		GIMP_HOME = os.path.join(os.environ.get("userprofile"), "AppData\Local\Programs\GIMP 2")
	if not os.path.exists(GIMP_HOME):
		GIMP_HOME = os.path.join(os.environ.get("userprofile"), "AppData\Local\Programs\GIMP")
	if LINUX:
		GIMP_HOME = os.path.normpath('/usr')
	while not os.path.exists(GIMP_HOME):
		print ("Could not find GIMP at ( %s )")
		GIMP_HOME = raw_input("Please enter full path to GIMP install directory: ")

	# Check for GIMP dds plugin
	#GIMP_DDS_PLUGIN = os.path.join(GIMP_HOME, "lib/gimp/2.0/plug-ins/file-dds/file-dds.exe")
	GIMP_DDS_PLUGIN = os.path.join(GIMP_HOME, "lib/gimp/2.0/plug-ins/file-dds/dds.exe")
	if LINUX:
		GIMP_DDS_PLUGIN = os.path.normpath("/usr/lib64/gimp/2.0/plug-ins/file-dds/file-dds")
	if not os.path.exists(GIMP_DDS_PLUGIN):
		DDS_PLUGIN = os.path.join(GIMP_HOME, "lib/gimp/2.0/plug-ins/dds.exe")
		if LINUX:
			DDS_PLUGIN = os.path.normpath("/usr/lib64/gimp/2.0/plug-ins/dds")
		while not os.path.exists(DDS_PLUGIN):
			msg = "Could not find GIMP dds plugin at ( {} )".format(DDS_PLUGIN)
			print (msg)
			if not LINUX:
				logger.error(msg)
				sys.exit()
			DDS_PLUGIN = raw_input("Please enter full path to GIMP dds plugin: ")

	# Check for GIMP console
	GIMP_BIN = os.path.join(GIMP_HOME, "bin")
	gimp_console_lst = [file for file in os.listdir(GIMP_BIN) if (file.find('gimp-console') >= 0)]
	if not len(gimp_console_lst):
		msg = "Could not file gimp-console, or gimp-console-X.X.exe"
		print (msg)
		logger.error(msg)
		sys.exit()
	GIMP_CONSOLE = os.path.join(GIMP_BIN, gimp_console_lst[0])

	# Determine GAME install directory
	MOD_HOME, MOD_DIR = os.path.split(CWD)
	MOD_ROOT, _ = os.path.split(MOD_HOME)
	_, GAME = os.path.split(MOD_ROOT)
	GAME_HOME = os.path.join(PROGRAM_BASE, "Steam/steamapps/common", GAME)
	while not os.path.exists(GAME_HOME):
		GAME_HOME = raw_input("Please enter full path to game install directory: ")

	# Determine desired resolution height
	resolution_list = [file.strip('p') for file in os.listdir('.') if (os.path.isdir(file))]
	resolution_list.sort(key=lambda item: (len(item), item))
	if resolution_list.count('temp_gfx'):
		resolution_list.remove('temp_gfx')
	res_height = raw_input("Please enter desire resolution height: ")
	scale_factor = float(res_height) / 1080.0

	SCALE_UI_PREFIX = "scale_ui_%sp" % res_height
	MOD_DIR = MOD_HOME + '/' + SCALE_UI_PREFIX

	with open("scale_ui.cfg", "w") as ff:
		msglist = ["GIMP_HOME={}".format(GIMP_HOME),
					"GAME_HOME={}".format(GAME_HOME),
					"MOD_DIR={}".format(MOD_DIR),
					"SCALE_FACTOR={}".format(scale_factor)]
		for msg in msglist:
			ff.write(msg + '\n')
			logger.info(msg)

	# If mod directory exists ask to remove it
	if os.path.exists(MOD_DIR):
		try:
			removeDir = raw_input("Remove existing mod directory before continuing [n/y]: ")
			if removeDir.find('y') == 0:
				shutil.rmtree(MOD_DIR, True)
		except:
			pass

	# Create mod directory
	if not os.path.exists(MOD_DIR):
		try:
			os.makedirs(MOD_DIR)
		except:
			pass

	# Create mod file
	MOD_FILE = MOD_HOME + '/' + SCALE_UI_PREFIX + '.mod'
	update_version = 'n'
	if os.path.exists(MOD_FILE):
		update_version = raw_input("Update supported version in mod file [n/y]: ")
	if not os.path.exists(MOD_FILE) or update_version.find('y') == 0:
		try:
			version = raw_input("Creating mod file.  Please enter current game version: ")
			with open(MOD_FILE, "w") as ff:
				ff.write("name=\"%s\"\n" % SCALE_UI_PREFIX)
				ff.write("path=\"mod/%s\"\n" % SCALE_UI_PREFIX)
				ff.write("tags={\n")
				ff.write("\t\"Graphics\"\n")
				ff.write("}\n")
				ff.write("supported_version=\"%s\"\n" % version)
		except:
			pass

	if LINUX:
		PYTHON_BIN = os.path.normpath("/usr/bin/python")
	else:
		PYTHON_BIN = os.path.join(GIMP_HOME, "Python/python")
		if not os.path.exists(PYTHON_BIN + ".exe"):
			PYTHON_BIN = os.path.join(GIMP_HOME, "32/bin/python")
			if not os.path.exists(PYTHON_BIN + ".exe"):
				PYTHON_BIN = os.path.join(GIMP_HOME, "bin/python")
	logger.info("PYTHON_BIN={}".format(PYTHON_BIN))
	subprocess.call([PYTHON_BIN, "rescale_interface.py"])
	subprocess.check_output([GIMP_CONSOLE, "-i", "--batch-interpreter=python-fu-eval", "-b", "execfile('rescale_gfx.py')", "-b", "pdb.gimp_quit(1)"])

	scaled_dir = os.path.join(CWD, "%sp" % res_height)
	if os.path.exists(scaled_dir):
		recursive_copy(scaled_dir, MOD_DIR)
	logger.critical("Exiting install_scale_ui_mod.py")

except Exception as e:
	traceback.print_exc()
	logger.exception("Exception")
