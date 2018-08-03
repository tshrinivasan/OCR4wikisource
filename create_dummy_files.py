import os.path
import sys

if not os.path.exists('missing_files.txt'):
    print "The file missing_files.txt is not available"
    sys.exit()
else:
    missing_files = open('missing_files.txt', 'r')
    for missing_file in missing_files:
        filename = missing_file.strip()
        dummy_file = open(filename, 'w')
        dummy_file.write("Google can not OCR this file.")
        dummy_file.close()

        upload_file = open(filename.split('.txt')[0], 'w')
        upload_file.write(" ")
        upload_file.close()

print "Created all dummy files. Done!"
