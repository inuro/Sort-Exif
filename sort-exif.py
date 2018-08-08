#   sort-exif.py
#   copy img files recursively sorting by EXIF:DateTimeOriginal
#   depends on https://smarnach.github.io/pyexiftool/
#
#   [usage]
#   $ python sort-exif.py source_dir dest_dir
#   $ python sort-exif.py photos_from photos_to

import sys
import os
import re
import struct
import subprocess
import datetime
import shutil
import exiftool

args = sys.argv
if(len(args)<3):
    print("usage: $ python sort-exif.py source_dir dest_dir")
    sys.exit()

source_dir = args[1]
dest_dir = args[2]
print("source: " + args[1])
print("dest: " + args[2])

file_count = 0
dup_count = 0
result = {}
for root, dirs, files in os.walk(source_dir):
    for f in files:
        matchOB = re.search(r'^[^\.]',f) 
        if matchOB:
            file_count = file_count + 1
            full_path = os.path.join(root, f)
            
            #get all tags
            with exiftool.ExifTool() as et:
                tags = et.get_metadata(full_path)
            
            #distinguish oldest date
            dates = []
            original_dates = []
            for name in tags:
                #except Files:tags
                matchOB = re.search(r'^([^\:]*)\:?([^\:]+)$', name)
                if(matchOB and matchOB.group(1) not in ['File','ICC_Profile']):
                    tag = matchOB.group(2)
                    value = tags[name]
                    if(isinstance(value, unicode) == False):
                        value = str(value)
                    matchOB = re.search(r'^([0-9]+):([0-9]+):([0-9]+)\s([0-9]+):([0-9]+):([0-9]+)([\+\-]?[^+]*)$',value)
                    if(matchOB):
                        year = matchOB.group(1)[:4]
                        month = matchOB.group(2)[:2]
                        day = matchOB.group(3)[:2]
                        hour = matchOB.group(4)[:2]
                        minute = matchOB.group(5)[:2]
                        second = matchOB.group(6)[:2]
                        candidate = '{0}:{1}:{2} {3}:{4}:{5}'.format(year,month,day,hour,minute,second)
                        try:
                            if(int(year) < 1990):
                                raise ValueError('Year {} is before 1990!'.format(year))
                            new_date = datetime.datetime.strptime(candidate, '%Y:%m:%d %H:%M:%S')
                            if(tag in ['DateTimeOriginal','CreateDate']):
                                original_dates.append(new_date)
                            else:
                                dates.append(new_date)
                        except Exception, e:
                            print "error:", e
            #use original_dates if available
            if(len(original_dates) > 0):
                dates = sorted(original_dates)
            else:
                dates = sorted(dates)

            oldestDate = None
            for value in dates:
                oldestDate = value
                break
            
            #create directory structure for the date
            photo_dir = None
            if(oldestDate != None):
                try:
                    photo_dir = os.path.join(dest_dir, oldestDate.strftime('%Y/%m/%d'))
                except Exception, e:
                    print "error:", e
            if(photo_dir == None):
                photo_dir = os.path.join(dest_dir, 'no_exif')
            if not os.path.exists(photo_dir):
                os.makedirs(photo_dir)
            
            #copy file to the directory
            if not os.path.exists(os.path.join(photo_dir, f)):
                shutil.copy(full_path, photo_dir)
                print str(file_count) + "\t" + full_path + "\t" + photo_dir
            #case dup
            else:
                body, ext = os.path.splitext(f)
                renamed_f = body + '(' + str(dup_count) + ')' + ext
                renamed_path = os.path.join(photo_dir, renamed_f)
                shutil.copy(full_path, renamed_path)
                dup_count = dup_count + 1
                print str(file_count) + "\t" + full_path + "\t" + renamed_path + "\t" + ' *dup*'

print 'Files moved total: {}'.format(file_count)
