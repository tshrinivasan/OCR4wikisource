#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import requests
import os
from clint.textui import progress
import glob
import shutil
import time
import datetime
import ConfigParser
import urllib

config = ConfigParser.ConfigParser()
config.read("config.ini")



ts = time.time()
timestamp  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

#Read the config file

url = config.get('settings','file_url')
columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
wikisource_language_code = config.get('settings','wikisource_language_code')


original_url = urllib.unquote(url).decode('utf8')

filename = os.path.basename(original_url)
filetype = filename.split('.')[-1].lower()

temp_folder = 'temp-'+ timestamp



print "\n\nDownloading the file " + filename + "\n\n"


#Download the file

r = requests.get(url, stream=True)
with open(filename, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()



# Convert djvu to PDF

if filetype.lower() == "djvu" :
        print "Found a djvu file. Converting to PDF file. " + "\n\n"
        command = "ddjvu --format=pdf " + filename + filename.split('.')[0] + ".pdf"
        os.system(command)

        filename = filename.split('.')[0] + ".pdf"
        filetype = filename.split('.')[-1].lower()
        


if filetype.lower() == "pdf":

	# split the PDF files vertically based on the column numbers

        print "Aligining the Pages of PDF file. \n" 
        command = "mutool poster -x " + str(columns)  + " " +  filename + "  currentfile.pdf"

        os.system(command)

        print "Spliting the PDF into single pages. \n"
        burst_command = "pdftk currentfile.pdf burst"
        os.system(burst_command)
        
        files = []
        for filename in glob.glob('pg*.pdf'):
                files.append(filename)
                files.sort()

        chunks=[files[x:x+int(columns)] for x in xrange(0, len(files), int(columns))]

        counter = 1
        print "Joining the PDF files ...\n"
        for i in chunks:
            com =  ' '.join(i)
            command = "pdfunite " + com + " " + "page_" + str(counter).zfill(5) + ".pdf"
             
            counter = counter + 1
            os.system(command)
                                

        

def move_file(file):
        source = file
        destination = temp_folder

        if os.path.isdir(temp_folder):
                shutil.move(source,destination)
        else:
                os.mkdir(temp_folder)
                shutil.move(source,destination)
        print "Moving the file " + file + " to the folder " + temp_folder + "\n"




# Create a temp folder in google drive to upload the files. You can delete this folder later.

print "\nCreating a folder in Google Drive to upload files \n\n"
print "Folder Name : " + temp_folder + "\n\n"

create_folder_in_drive_command = "gdmkdir.py " + temp_folder + " | tee folder_in_google_drive.log"
os.system(create_folder_in_drive_command)


resultfile = open("folder_in_google_drive.log","r").readlines()

for line in resultfile:
        if "id:" in line:
                drive_folder_id = line.split(":")[1].strip()

                
 
files = []
for filename in glob.glob('page_*.pdf'):
            files.append(filename)




#Upload the PDF files to google drive and OCR

upload_counter = 1

for pdf_file in sorted(files):

        
            print "\n\nuploading " + pdf_file + " to google Drive. File " + str(upload_counter) + " of " + str(len(files)) + " \n\n"   
            command = "gdput.py -t ocr -f   " +  drive_folder_id + " "  + pdf_file + " | tee " + pdf_file.split('.')[0] + ".log"
            
            
            os.system(command)

            resultfile = open(pdf_file.split('.')[0] + ".log","r").readlines()

            for line in resultfile:
                        if "id:" in line:
                                    fileid = line.split(":")[1].strip()
                                    filename = pdf_file.split(".")[0] + ".txt"
                                    get_command = "gdget.py -f txt -s " + filename + " " + fileid
                                    print "\n\nDownloading the OCRed text \n\n "
                                    os.system(get_command)

   	    move_file(pdf_file)
            print "\n\n========\n\n"
            upload_counter = upload_counter + 1


files = []
for filename in glob.glob('page_*.txt'):
        files.append(filename)
        files.sort()


# Split the text files to sync with the original images




if int(columns)==1:
        i = 1
        for textfile in files:
                with open(textfile,'r') as filetosplit:
                         content = filetosplit.read()
                        
                         if len(content)>50:
                                 with open('txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                                         towrite.write(content)
                                 i = i+1
                         else:

				with open('txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                                	towrite.write(' ')
                                i = i+1

                                                                                                                              

                                        

elif int(columns)==2:
                                                                                                                                                
    i = 1
    for textfile in files:
        with open(textfile,'r') as filetosplit:
                content = filetosplit.read()
		if "________________" in content:
                	records = content.split('________________')
                	print records
                	for record in records[1::2]:
                                with open('txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                                        towrite.write(record)
                                i = i+1
                else:
                        for no in range(int(columns)):
                                with open('txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                          	      towrite.write(' ')
                                i = i+1
                                
                    


files = []
for filename in glob.glob('txt*.txt'):
        files.append(filename)
        files.sort()

                                                

chunks=[files[x:x+int(columns)] for x in xrange(0, len(files), int(columns))]

counter = 1
                                               
for i in chunks:
        com =  ' '.join(i)
        command = "cat  " + com + " > " + "text_for_page_" + str(counter).zfill(5) + ".txt"
        counter = counter + 1
        os.system(command)



print "\n Moving all temp files to " + temp_folder + "\n"
command = "mv folder*.log currentfile.pdf  doc_data.txt pg*.pdf page* txt* " + temp_folder
os.system(command)

print "\n\nDone. Check the text files start with text_for_page_ "
