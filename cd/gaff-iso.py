#!/usr/bin/env python

# ---------------------------------------------------------------------
# $Id: gaff-iso 236 2008-08-16 03:33:22Z daaugusto $
#
#   gaff-iso (created on Wed Jul 16 18:29:21 BRT 2008)
#
#   Genetic Algorithm File Fitter (gaffitter)
#
#   Copyright (C) 2008 Douglas A. Augusto
#
# This file is part of gaffitter.
#
# gaffitter is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# gaffitter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gaffitter; if not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------

import sys

if sys.version[:5] < "2.4":
   print "This script requires Python 2.4 or later."
   sys.exit( 1 )

import os
import subprocess
import getopt

def Usage( exitcode = 0 ):
   print "Usage: gaff-iso --{dvd|dvd-dl|cd|cd74|cd90|cd99|size n} [OPTION] files/dirs"
   print ""
   print "Options:"
   print "  --dvd"
   print "     create volumes of 4.38GB (DVD)"
   print "  --dvd-dl"
   print "     create volumes of 7.95GB (Dual Layer DVD)"
   print "  --cd"
   print "     create volumes of 702MB (80min CD)"
   print "  --cd74"
   print "     create volumes of 650MB (74min CD)"
   print "  --cd90"
   print "     create volumes of 790MB (90min CD)"
   print "  --cd99"
   print "     create volumes of 870MB (99min CD)"
   print "  --size n[k,m,g,t]"
   print "     create custom volumes of n KiB/MiB/GiB/TiB each"
   print "  --split"
   print "     just splits the input (i.e. preserves original order)"
   print "  --vols n"
   print "     maximum number of volumes (default = as much as possible)"
   print "  -o dir, --output dir"
   print "     output directory for the ISO images"
   print "  -v"
   print "     verbose mode"
   print "  -y"
   print "     overwrite any existing output files"
   print ""
   print "Advanced options:"
   print "  --mkisofs-opts \"opts\""
   print "     use custom mkisofs options (default = \"-D -r -J -joliet-long\")"
   print ""
   print "Example: gaff-iso --dvd *"
   print ""
   print "Powered by GAFFitter (http://gaffitter.sf.net)"

   sys.exit( exitcode )

def FindInPath( program ):
   if os.path.sep in program:
      if os.path.exists( program ):
         return program
   else:
      for path in os.path.expandvars( "$PATH" ).split( os.path.pathsep ):
         if os.path.exists( os.path.join( path, program ) ):
            return os.path.join( path, program )
   return None

def CheckPrograms( programs ):
   found = {}
   for p in programs:
      for x in programs[p]:
         path = FindInPath( x )
         if path: 
            found[p] = path
            break
      if not path: Error( "Error: %s is required, aborting." %p )
   return found

def Error( msg = "", code = 1 ):
   print >> sys.stderr, ">", msg; sys.stderr.flush()
   sys.exit( code )

def GraftPoints( files ):
   def clean( path ):
      if path[:3] == '../': return path[3:]
      return path

   # escapes '\' and '=' characters
   gp = files.replace( '\\', '\\'+'\\'[-1] ).replace( '=', '\=' )
   
   # format according to mkisofs graftpoints style
   return ''.join( [ "%s=%s\0" %(clean( x ), x) for x in gp.split( '\0' )[:-1] ] )

def SizeInBytes( size ):
   # transform the given size in bytes
   try:
      if size[-1].isalpha():
         if size[-1] in ('t', 'T'):
            size = float( size[:-1] ) * pow( 1024, 4 )
         elif size[-1] in ('g', 'G'):
              size = float( size[:-1] ) * pow( 1024, 3 )
         elif size[-1] in ('m', 'M'):
              size = float( size[:-1] ) * pow( 1024, 2 )
         elif size[-1] in ('k', 'K'):
              size = float( size[:-1] ) * 1024
   except:   
      Error( "Error while parsing the given size '%s', aborting" %size )

   if int( size ) <= 0:
      Error( "Target size must be greater than zero, aborting" )

   return int( size )

def CheckGAFFitterVersion( path, minimum ):
   try:
      gaffitter = subprocess.Popen( [path, '--version'], stdout=subprocess.PIPE )
      gaffitter_ver = gaffitter.stdout.read().split( ' ' )[1]
      gaffitter.stdout.close()
   except:
      Error( "Could not check the GAFFitter's version." )
   if gaffitter_ver < minimum:
      Error( "This script requires GAFFitter %s or later." %minimum )

def main():
   print "GAFFitter ISO9660 image set creator (v0.1.0)\n"

   # Get the options
   try:
       opts, files = getopt.getopt( sys.argv[1:], "hvyo:", ["help", "dvd",
       "dvd-dl", "cd", "cd74", "cd90", "cd99", "size=", "split",
       "vols=", "output=", "mkisofs-opts="] )
   except getopt.GetoptError, err:
       print str( err ) # will print something like "option -a not recognized"
       Usage(2)

   params = { 'size': None, 'prefix': None, 'vols': None, 'verbose': False, \
              'overwrite': False, 'output': None, 'split': '', 'mkisofs-opts':
              '-D -r -J -joliet-long'}

   for o, a in opts:
       if o in ("-h", "--help"):
           Usage()
       elif o == "-v":
           params["verbose"] = True
       elif o == "-y":
           params["overwrite"] = True
       elif o in ("-o", "--output"):
           params["output"] = a
       elif o == "--cd":
           params["size"] = "702m"
           params["prefix"] = "CD80-"
       elif o == "--cd74":
           params["size"] = "650m"
           params["prefix"] = "CD74-"
       elif o == "--cd90":
           params["size"] = "790m"
           params["prefix"] = "CD90-"
       elif o == "--cd99":
           params["size"] = "870m"
           params["prefix"] = "CD99-"
       elif o == "--dvd":
           params["size"] = "4480m"
           params["prefix"] = "DVD-"
       elif o == "--dvd-dl":
           params["size"] = "8140m"
           params["prefix"] = "DVDDL-"
       elif o == "--size":
           params["size"] = a
           params["prefix"] = "CUSTOM-"
       elif o == "--split":
           params["split"] = "--split"
       elif o == "--vols":
           params["vols"] = a
       elif o == "--mkisofs-opts":
           params["mkisofs-opts"] = a
       else:
           assert False, "Unhandled option"

   programs = CheckPrograms( {'gaffitter':['gaffitter'], 'mkisofs':['genisoimage',
                              'mkisofs'], 'xargs':['xargs']} )

   CheckGAFFitterVersion( programs['gaffitter'], "0.6.0" )

   if not params["size"] or ( params["vols"] and params["vols"] <= 0 ): Usage(2)
   if params["output"] and not os.path.exists( params["output"] ):
      Error( "Output dir \'%s\' does not exist, aborting." % params["output"] )

   if not params['verbose']: params['mkisofs-opts'] += ' -quiet'

   params["size"] = SizeInBytes( params["size"] )

   requested_size = params["size"]

   print "Running gaffitter...",
   while True:
      gaffitter_cmd = r"%s - -z -Z --hs -0 %s -t %s -B 2048" \
                       % (programs["gaffitter"], params["split"], params["size"])

      if params["verbose"]: print "(%s)" % gaffitter_cmd,

      sys.stdout.flush()

      try:
         gaffitter = subprocess.Popen( gaffitter_cmd.split(), stdin=subprocess.PIPE, 
                                                           stdout=subprocess.PIPE )
         gaffitter.stdin.write( "".join( [ "%s\0" %x for x in files ] ) )
         gaffitter.stdin.close()
         if gaffitter.wait(): 
            raise
         out = gaffitter.stdout.read()
         gaffitter.stdout.close()
      except:
         Error( "An error occurred while running GAFFitter." )

      bins = [ "%s\0" %x for x in out[:-1].split( "\0\0" ) ]

      # verify the ISO9660 overhead
      residual = 0.0
      for bin in bins:
         mkisofs_cmd = r"%s -0 %s -quiet %s -print-size -V 0000 -graft-points" \
                        % (programs["xargs"], programs["mkisofs"],
                           params['mkisofs-opts'])
         try:
            mkisofs = subprocess.Popen( mkisofs_cmd.split(), stdin=subprocess.PIPE, 
                                                            stdout=subprocess.PIPE )
            mkisofs.stdin.write( GraftPoints( bin ) )
            mkisofs.stdin.close()
            if mkisofs.wait(): 
               raise
            out_size = int( mkisofs.stdout.read() )
            mkisofs.stdout.close()
         except:
            Error( "An error occurred while running %s (%s)." \
                    % (programs['mkisofs'], mkisofs_cmd) )

         if out_size * 2048 > requested_size:
            if out_size * 2048 - requested_size > residual:
               residual = out_size * 2048 - requested_size

      if residual > 0.0: # hmmm, there will be necessary adjustment
         if params['verbose']:
            print "Warning, there is significant ISO9660 file system overhead, running gaffitter again..."
         params["size"] -= int( residual )
         if params["size"] <= 0:
            Error( "ISO9660 overhead is greater than the specified size, aborting." )
      else:
         break

   print "done.\n"
   total = len( bins )

   for v in range( 1, total + 1 ):
      image = params["prefix"] + str(v).zfill(4) + ".iso"
      if params["output"]: image = os.path.join( params["output"], image )

      if os.path.exists( image ) and not params["overwrite"]:
         Error( "Output file %s already exists. Remove it or\n" % image + \
                "  use the overwrite option (-y)." )

   vol = 1
   image_set = []
   for bin in bins:
      #print "[%d/%d] Selected files:\n\n%s\n" % ( vol, total, bin.split('\0')[:-1] )
      print "[%d/%d] Selected files:\n\n%s\n" % ( vol, total, 
                                                  bin.replace('\0','\n')[:-1] )
      suffix = str(vol).zfill(4)
      image = params["prefix"] + suffix + ".iso"
      if params["output"]: image = os.path.join( params["output"], image )

      # mkisofs
      mkisofs_cmd = r"%s -0 %s %s -V %s -graft-points -o %s"\
            % (programs['xargs'], programs["mkisofs"], params['mkisofs-opts'],
            vol, image)

      print "[%d/%d] Creating ISO image %s..." %( vol, total, image ),
      if params["verbose"]: print r"(%s)" %mkisofs_cmd,

      sys.stdout.flush()

      try:
         mkisofs = subprocess.Popen( mkisofs_cmd.split(), stdin=subprocess.PIPE )
         mkisofs.stdin.write( GraftPoints( bin ) )
         mkisofs.stdin.close()
         if mkisofs.wait(): 
            raise
      except:
         Error( "An error occurred while generating the image " + image )

      print "[%s bytes] done.\n" %os.path.getsize( image )

      image_set.append( image )
      vol += 1
   
   print "Generated ISO images:\n"
   for i in image_set:
      print "%s" %i

   sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
