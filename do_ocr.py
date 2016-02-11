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
import logging
import urllib2
import os.path


version = "1.46"


config = ConfigParser.ConfigParser()
config.read("config.ini")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



ts = time.time()
timestamp  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')


if not os.path.isdir("./log"):
            os.mkdir("./log")


# create a file handler
log_file = './log/do_ocr_' + timestamp + '_log.txt'

handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)

# create a logging format

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger

logger.addHandler(handler)



latest_version =  urllib2.urlopen('https://raw.githubusercontent.com/tshrinivasan/OCR4wikisource/master/VERSION').read().strip('\n').split(' ')[1]

if not float(version) == float(latest_version):
            logger.info("\n\nYour OCR4WikiSource version is " + version + ". This is old. The latest version is " + latest_version + ". Update from https://github.com/tshrinivasan/OCR4wikisource \n\n")
            sys.exit()




logger.info("Running do_ocr.py " + version)


os_info = open("/etc/lsb-release")
for line in os_info:
	if  "DISTRIB_DESCRIPTION" in line:
		os_version = line.split("=")[1]

logging.info("Operating System = " + os_version)





#Read the config file

url = config.get('settings','file_url')
columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
wikisource_language_code = config.get('settings','wikisource_language_code')
keep_temp_folder_in_google_drive = config.get('settings','keep_temp_folder_in_google_drive')
#start_page = config.get('settings','start_page')
#end_page = config.get('settings','end_page')



logger.info("URL = " + url )
logger.info("Columns = " + columns )
logger.info("Wiki Username = " + wiki_username)
logger.info("Wiki Password = " + "Not logging the password")
logger.info("Wiki Source Language Code = " + wikisource_language_code )
logger.info("Keep Temp folder in  Google Drive = " + keep_temp_folder_in_google_drive)
#logger.info("Start Page = " + str(start_page))
#logger.info("End Page = " + str(end_page))




original_url = urllib.unquote(url).decode('utf8')

logger.info("Original URL = " + original_url )


filename = os.path.basename(original_url)
filetype = filename.split('.')[-1].lower()

logger.info("File Name = " + filename)
logger.info("File Type = " + filetype)


temp_folder = "OCR-" + filename + '-temp-'+ timestamp
logger.info("Created Temp folder " + temp_folder)

if not os.path.isdir(temp_folder):
      os.mkdir(temp_folder)
                            



if os.path.isfile(filename):
            logging.info(filename + " Already Exists. Skipping the download.")

else:
            print "\n\nDownloading the file " + filename + "\n\n"

            logger.info("Downloading the file " + filename )

            #Download the file

            r = requests.get(url, stream=True)
            with open(filename, 'wb') as f:
                        total_length = int(r.headers.get('content-length'))
                        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                                    if chunk:
                                                f.write(chunk)
                                                f.flush()


            logger.info("Download Completed")




# Convert djvu to PDF

if filetype.lower() == "djvu" :

            if os.path.isfile(filename.split('.')[0] + ".pdf"):
                        logging.info("Found PDF version. Skipping DJVU to PDF conversion")
                        filename = filename.split('.')[0] + ".pdf"
                        filetype = filename.split('.')[-1].lower()
                                                        
            else:
                        
                        message  =  "Found a djvu file. Converting to PDF file. " + "\n\n"
                        logger.info(message)
        
                        command = "ddjvu --format=pdf " +  '"' + filename +  '"' + "   " + '"' +  filename.split('.')[0] + '"' + ".pdf"
                        os.system(command.encode('utf-8'))
                        logger.info("Running " + command)

                        filename = filename.split('.')[0] + ".pdf"
                        filetype = filename.split('.')[-1].lower()
        


if filetype.lower() == "pdf":

	# split the PDF files vertically based on the column numbers

        message =  "Aligining the Pages of PDF file. \n"
        logger.info(message)
        command = "mutool poster -x " + str(columns)  + " " + '"' +  filename + '"' +  "  currentfile.pdf"
        logger.info("Running " + command.encode('utf-8'))
        
        os.system(command.encode('utf-8'))
                

        message =  "Spliting the PDF into single pages. \n"
        logger.info(message)
        burst_command = "pdftk currentfile.pdf burst"
        os.system(burst_command)
        logger.info("Running " + burst_command) 

        
        files = []
        for filename in glob.glob('pg*.pdf'):
                files.append(filename)
                files.sort()

        chunks=[files[x:x+int(columns)] for x in xrange(0, len(files), int(columns))]

        counter = 1
        message =  "Joining the PDF files ...\n"
        logger.info(message)

        if columns == "1":
                counter = 1
                for pdf in files:
                        command = "cp " + pdf +  " page_" + str(counter).zfill(5) + ".pdf"
                        logger.info("Running Command " + command)
                        counter = counter + 1
                        os.system(command)


        if columns == "2":

	        chunks=[files[x:x+int(columns)] for x in xrange(0, len(files), int(columns))]

	        counter = 1
	        message =  "Joining the PDF files ...\n"
	        logger.info(message)
	        
	        for i in chunks:
	            com =  ' '.join(i)
	            command = "pdfunite " + com + " " + "page_" + str(counter).zfill(5) + ".pdf"
	            logger.info("Running " + command) 
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
        message =  "Moving the file " + file + " to the folder " + temp_folder + "\n"
        logger.info(message)




# Create a temp folder in google drive to upload the files. You can delete this folder later.

logger.info( "\nCreating a folder in Google Drive to upload files. Folder Name : " + temp_folder + "\n\n")

create_folder_in_drive_command = "gdmkdir.py " + '"' +  temp_folder + '"'  + " | tee folder_in_google_drive.log"
logger.info("Running " + create_folder_in_drive_command.encode('utf-8'))
os.system(create_folder_in_drive_command.encode('utf-8'))


resultfile = open("folder_in_google_drive.log","r").readlines()

for line in resultfile:
        if "id:" in line:
                drive_folder_id = line.split(":")[1].strip()

                
 
files = []
for filename in glob.glob('page_*.pdf'):
            files.append(filename)




#pages = []
#if not end_page == "END" :
#    for pageno in range(int(start_page), int(end_page) + 1):
#         pages.append("page_" + str(pageno).zfill(5) + ".pdf")   

#if end_page == "END":
#    for pageno in range(int(start_page),len(files) +1):
#        pages.append("page_" + str(pageno).zfill(5) + ".pdf")
        






#Upload the PDF files to google drive and OCR

upload_counter = 1

for pdf_file in sorted(files):


    if not os.path.isfile(pdf_file.split('.')[0] + ".upload"):                        
                                                

            message= "\n\nuploading " + pdf_file + " to google Drive. "     # File " + str(upload_counter) + " of " + str(len(files)) + " \n\n"
            logger.info(message)
            command = "gdput.py -t ocr -f   " +  drive_folder_id + " "  + pdf_file + " | tee " + pdf_file.split('.')[0] + ".log"
            
            logger.info("Running " + command)
            os.system(command)

                                                            

            resultfile = open(pdf_file.split('.')[0] + ".log","r").readlines()

            for line in resultfile:
                        if "id:" in line:
                                    fileid = line.split(":")[1].strip()
                                    filename = pdf_file.split(".")[0] + ".txt"
                                    get_command = "gdget.py -f txt -s " + filename + " " + fileid
                                    logger.info( "\n\nDownloading the OCRed text \n\n ")
                                    logger.info("Running " + command)
                              #      os.system(get_command)


                                    download_status = os.system(get_command)

                                    if download_status == 0:
                                                create_temp_file = "touch " + pdf_file.split('.')[0] + ".upload"
                                                logger.info("\n  Creating temp file " + create_temp_file + "\n")
                                                os.system(create_temp_file)
                        

#   	    move_file(pdf_file)
            logger.info( "\n\n========\n\n")
            upload_counter = upload_counter + 1



pdf_count = len(glob.glob('page_*.pdf'))
text_count = len(glob.glob('page_*.txt'))



if not pdf_count == text_count:

            logger.info("\n\n=========ERROR===========\n\n")
            
            for i in range(1,int(pdf_count)+1):
                        txt_file = "page_" + str(i).zfill(5) + ".txt"
                        if not os.path.isfile(txt_file):
                                    logger.info( "Missing " + txt_file)
                                    logger.info( "page_" + str(i).zfill(5) + ".pdf" + " should be reuploaded ")
                                                                         

            logger.info(" \n\nText files are not equal to PDF files. Some PDF files not OCRed. Run this script again to complete OCR all the PDF files \n\n")
            sys.exit()

            

            

files = []
for filename in glob.glob('page_*.txt'):
        files.append(filename)
        files.sort()


# Split the text files to sync with the original images

logger.info("Split the text files to sync with the original images")


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
                                
                    


logger.info("Joining text files based on Column No")
                                
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
        logger.info("Running " + command)
        os.system(command)



message =  "\nMoving all temp files to " + temp_folder + "\n"
logger.info(message)
command = "mv folder*.log currentfile.pdf  doc_data.txt pg*.pdf page* txt*   " + '"' +  temp_folder + '"'
logger.info("Running " + command.encode('utf-8'))
os.system(command.encode('utf-8'))




original_filename = os.path.basename(original_url)

files = []
for textfile in glob.glob('text_for_page*.txt'):
            files.append(textfile)
            files.sort()

            
single_file = open("all_text_for_" + original_filename + ".txt" ,"w")

counter = 1
for filename in files:
            content = open(filename).read()
            single_file.write("\n\n")
            single_file.write("Page " + str(counter))
            single_file.write("\n\n")
            single_file.write(content)
            single_file.write("\n\n")
            single_file.write("xxxxxxxxxx")
            counter = counter + 1

single_file.close()
                                                                

logger.info("Merged all OCRed files to  all_text_for_" + original_filename + ".txt")



if keep_temp_folder_in_google_drive == "no":
        message =  "\nDeleting the Temp folder in Google Drive " + temp_folder + "\n"
        logger.info(message)
        command = "gdrm.py " + drive_folder_id
        logger.info("Running " + command)
        os.system(command)


message =  "\n\nDone. Check the text files start with text_for_page_ "
logger.info(message)




result_text_count = len(glob.glob('text_for_page_*.txt'))

if not pdf_count == result_text_count:
            logger.info("\n\n=========ERROR===========\n\n")
            logger.info(" \n\nText files are not equal to PDF files. Some PDF files not OCRed. Run this script again to complete OCR all the PDF     files \n\n")
            sys.exit()

if  pdf_count == result_text_count:
            logger.info("\n\nThe PDF files and result text files are equval. Now running the mediawiki_uploader.py script\n\n")
            command = "python mediawiki_uploader.py"
            os.system(command)
            

                                        
