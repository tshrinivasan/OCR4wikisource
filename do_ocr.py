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
from configparser import ConfigParser
import urllib
import logging
import os.path
import mwclient
import traceback
import io
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from pathlib import Path

version = "1.60"

#https://stackoverflow.com/questions/14340366/configparser-and-string-with
config = ConfigParser(interpolation=None)
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



latest_version =  urllib.request.urlopen('https://raw.githubusercontent.com/tshrinivasan/OCR4wikisource/master/VERSION').read().decode('utf-8').strip('\n').split(' ')[1]

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




original_url = urllib.parse.unquote(url)# .decode('utf8')

logger.info("Original URL = " + original_url )


filename = os.path.basename(original_url)
filetype = filename.split('.')[-1].lower()

logger.info("File Name = " + filename)
logger.info("File Type = " + filetype)

wiki_url =  wikisource_language_code + ".wikisource.org"
logger.info("Wiki URL = " + wiki_url)

user_agent = 'OCR4WikiSource/0.2 (tshrinivasan@gmail.com)'
site = mwclient.Site(wiki_url, clients_useragent=user_agent)



'''
try:
        wikisite = wiki.Wiki(wiki_url)
except:
        message =  "Can not connect with wiki. Check the URL"
        logger.info(message)
        sys.exit()
'''
page_name = filename + '/1'
page_url = 'https://' + wikisource_language_code + '.wikisource.org/wiki/' + 'Page:'+ page_name
page =site.pages[page_url]
if(page.exists):        
    logger.info("\n\n=========ERROR===========\n\n")
    logger.info(page_url + 'File already uploaded')
    sys.exit()

logger.info(page_url + ' does not exist, Perform OCR')


temp_folder = "OCR-" + filename + '-temp-'+ timestamp
logger.info("Created Temp folder " + temp_folder)

if not os.path.isdir(temp_folder):
    os.mkdir(temp_folder)
                            

if os.path.isfile(filename):
    logging.info(filename + " Already Exists. Skipping the download.")

else:
    print("\n\nDownloading the file " + filename + "\n\n")

    logger.info("Downloading the file " + filename )

    #Download the file

    '''
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()
    '''

    '''
    filename = Path("input_file.pdf")
    response = requests.get(url)
    filename.write_bytes(response.content)    
    '''
    '''
    logger.info(url)
#    urllib.request.urlretrieve(url, "filename.pdf")

#    response = session.get(url)
    session = requests.Session()
    response = session.get(url, stream=True)

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    logger.info("Download Completed")
    '''

    download_file_command = "wget " + url
    logger.info(download_file_command)
    os.system(download_file_command)




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
    command = "mutool poster -x " + str(columns)  + " " + '"' +  filename + '"' + " "  + "currentfile.pdf"
    print(command)
    logger.info("Running " + command)
        
    os.system(command)
                

    message =  "Spliting the PDF into single pages. \n"
    logger.info(message)
    burst_command = "pdftk " + "currentfile.pdf burst"
#        burst_command = "pdfseparate currentfile.pdf pg-%05d.pdf"
        
    os.system(burst_command)
    logger.info("Running " + burst_command) 

        
    files = []
    for filename in glob.glob( 'pg*.pdf'):
        files.append(filename)
        files.sort()

    chunks=[files[x:x+int(columns)] for x in range(0, len(files), int(columns))]

    counter = 1
    message =  "Joining the PDF files ...\n"
    logger.info(message)

    if columns == "1":
        counter = 1
        for pdf in files:
            command = "cp " + pdf + " page_" + str(counter).zfill(5) + ".pdf"
            logger.info("Running Command " + command)
            counter = counter + 1
            os.system(command)


    if columns == "2":

        chunks=[files[x:x+int(columns)] for x in range(0, len(files), int(columns))]

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
'''
logger.info( "\nCreating a folder in Google Drive to upload files. Folder Name : " + temp_folder + "\n\n")

create_folder_in_drive_command = "gdmkdir.py " + '"' +  temp_folder + '"'  + " | tee folder_in_google_drive.log"
logger.info("Running " + create_folder_in_drive_command)
os.system(create_folder_in_drive_command)


resultfile = open("folder_in_google_drive.log","r").readlines()

for line in resultfile:
    if "id:" in line:
        drive_folder_id = line.split(":")[1].strip()

                
'''


SCOPES = 'https://www.googleapis.com/auth/drive.file'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flags= tools.argparser.parse_args([])
#flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    #flags=tools.argparser.parse_args(args=[])
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store, flags)
service = build('drive', 'v3', http=creds.authorize(Http()))


file_metadata = {'name': 'ocr_files_ocr4wikisource',
                  'mimeType': 'application/vnd.google-apps.folder'
                }
folder = service.files().create(body=file_metadata,fields='id').execute()
drive_folder_id=folder.get('id')

print(drive_folder_id)



        
logger.info("Converting all the PDF files to JPEG images")
for pdf in sorted(glob.glob('page_*.pdf')):
    
    basename = pdf.split(".")[0]
    if not os.path.isfile(basename + ".img"):
        pdf_to_jpg = "gs -q -DNOPAUSE -DBATCH -r400 -SDEVICE=jpeg  -sOutputFile=" + basename + ".jpg " + pdf
        logger.info(pdf_to_jpg)
        os.system(pdf_to_jpg)
        create_temp_file = "touch " + basename + ".img"
        logger.info(" Creating temp file " + create_temp_file + "\n")
        os.system(create_temp_file)


move_command = "mv *.jpg *.pdf *.img " + temp_folder
logger.info("moving files to temp folder")
logger.info(move_command)
os.system(move_command)

 
files = []
for filename in glob.glob(temp_folder + "/" + 'page_*.jpg'):
    files.append(filename)



def do_ocr(input_file,temp_folder):
   
    # Upload the file on Goggle Drive
    mime = 'application/vnd.google-apps.document'
    file_metadata = {'name': input_file, 'mimeType': mime, 'parents': [drive_folder_id] }
    #print(file_metadata)
    media = MediaFileUpload(input_file, mimetype= mime, chunksize=256 * 1024, resumable=True )
    #print(media)
    Imgfile = service.files().create(body=file_metadata,media_body=media,fields='id')


    response = None
    while response is None:
        status, response = Imgfile.next_chunk()
        time.sleep(1)
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
    logger.info("Upload of {} is complete.".format(input_file))

    basename = "".join(os.path.basename(input_file).split(".")[:-1])
    

    filename = temp_folder + "/" + basename + ".txt"
    time.sleep(10)

    # Download the file in txt format from Google Drive
    getTxt = service.files().export_media( fileId = response['id'], mimeType='text/plain')
    fh = io.FileIO( filename , 'wb' )
    downloader = MediaIoBaseDownload(fh, getTxt)
#    downloader.next_chunk()
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    


#pages = []
#if not end_page == "END" :
#    for pageno in range(int(start_page), int(end_page) + 1):
#         pages.append("page_" + str(pageno).zfill(5) + ".pdf")   

#if end_page == "END":
#    for pageno in range(int(start_page),len(files) +1):
#        pages.append("page_" + str(pageno).zfill(5) + ".pdf")
        






#Upload the JPG files to google drive and OCR

upload_counter = 1

total_files = len(files)

for jpg_file in sorted(files):
    basename = "".join(os.path.basename(jpg_file).split(".")[:-1])
    if not os.path.isfile(temp_folder + "/" + basename + ".upload"):                        
        message= "\n\nuploading " + jpg_file +" " + str(upload_counter) + "/" + str(total_files) +  " to google Drive. "     # File " + str(upload_counter) + " of " + str(len(files)) + " \n\n"
        logger.info(message)


        try:
            do_ocr(jpg_file, temp_folder)
        except Exception as e:
            logger.info(e)
            logger.info(traceback.format_exc())
                #telegram_send.send(messages=["ALERT : Error on " + filename + ". Script Stopped at " + hostname +". Rerun again"])
#                sys.exit()
#                os.system("python3 pdf2text.py")

            error_message = "Got issues on " + filename + " on " + hostname
                #telegram_send.send(messages=[error_message])
            traceback_text = traceback.format_exc()
            message = "Error on " + __file__ +  "\n" + traceback_text
            logger.info(message)
            #telegram_send.send(messages=[error_message])
        


        f= open(temp_folder + "/" + basename + ".upload","w+")
        f.close()
        logger.info("Creating temp file "  + "\n")


        logger.info("\n\n========\n\n")
        upload_counter = upload_counter + 1

        '''
        command = "gdput.py -t ocr -f   " +  drive_folder_id + " "  + jpg_file + " | tee " + jpg_file.split('.')[0] + ".log"
            
        logger.info("Running " + command)
        os.system(command)



        

        resultfile = open(jpg_file.split('.')[0] + ".log","r").readlines()

        for line in resultfile:
            if "id:" in line:
                fileid = line.split(":")[1].strip()
                filename = jpg_file.split(".")[0] + ".txt"
                get_command = "gdget.py -f txt -s " + filename + " " + fileid
                logger.info( "\n\nDownloading the OCRed text \n\n ")
                logger.info("Running " + command)
                              #      os.system(get_command)

                                    
                download_status = os.system(get_command)
                if download_status == 0:
                    create_temp_file = "touch " + jpg_file.split('.')[0] + ".upload"
                    logger.info("\n  Creating temp file " + create_temp_file + "\n")
                    os.system(create_temp_file)
                        

#           move_file(pdf_file)
        logger.info( "\n\n========\n\n")
        upload_counter = upload_counter + 1

        '''


#for txt_file in glob.glob('page_*.txt'):
#            with open(txt_file) as f:
#                        newText=f.read().replace('\n', '\n\n')
 
#            with open(txt_file, "w") as f:
#                        f.write(newText)




jpg_count = len(glob.glob(temp_folder + "/" + "page_*.jpg"))
text_count = len(glob.glob(temp_folder + "/"  + "page_*.txt"))

missing_files = open('missing_files.txt','w')

if not jpg_count == text_count:

    logger.info("\n\n=========ERROR===========\n\n")
            
    for i in range(1,int(pdf_count)+1):
        txt_file = "page_" + str(i).zfill(5) + ".txt"
        if not os.path.isfile(txt_file):
            missing_files.write(txt_file +"\n")
            logger.info( "Missing " + txt_file)
            logger.info( "page_" + str(i).zfill(5) + ".jpg" + " should be reuploaded ")
                                                                         

    logger.info(" \n\nText files are not equal to JPG files. Some PDF files not OCRed. Run this script again to complete OCR all the Pages. \n\n")
    sys.exit()

            
missing_files.close()
            

files = []
for filename in glob.glob(temp_folder + "/" + 'page_*.txt'):
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
                with open(temp_folder + "/" + 'txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                    towrite.write(content)
                i = i+1
            else:
                with open(temp_folder + "/"  + 'txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                    towrite.write(' ')
                i = i+1
                                        

elif int(columns)==2:
                                                                                                                                                
    i = 1
    for textfile in files:
        with open(textfile,'r') as filetosplit:
            content = filetosplit.read()
            if "________________" in content:
                    records = content.split('________________')
                    print(records)
                    for record in records[1::2]:
                       with open(temp_folder + "/" + 'txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                           towrite.write(record)
                       i = i+1
            else:
                    for no in range(int(columns)):
                        with open(temp_folder + "/" + 'txt_'+str(i).zfill(5)+'.txt', 'w') as towrite:
                            towrite.write(' ')
                        i = i+1
                                
                    


logger.info("Joining text files based on Column No")
                                
files = []
for filename in glob.glob(temp_folder + "/" + 'txt*.txt'):
    files.append(filename)
    files.sort()

                                                

chunks=[files[x:x+int(columns)] for x in range(0, len(files), int(columns))]

counter = 1
                                               
for i in chunks:
    com =  ' '.join(i)
    command = "cat  " + com + " > " + temp_folder + "/" + "text_for_page_" + str(counter).zfill(5) + ".txt"
    counter = counter + 1
    logger.info("Running " + command)
    os.system(command)


'''
message =  "\nMoving all temp files to " + temp_folder + "\n"
logger.info(message)
command = "mv folder*.log currentfile.pdf  doc_data.txt pg*.pdf page* txt* *.jpg *.img " + '"' +  temp_folder + '"'
logger.info("Running " + command)
os.system(command)
'''



original_filename = os.path.basename(original_url)

files = []
for textfile in glob.glob(temp_folder + "/" + 'text_for_page*.txt'):
    files.append(textfile)
    files.sort()

            
single_file = open(temp_folder + "/" + "all_text_for_" + original_filename + ".txt" ,"w")

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
                                                                

logger.info("Merged all OCRed files to  " + temp_folder + "/"  + "all_text_for_" + original_filename + ".txt")


if not os.path.isdir("text-for-" + original_filename):
    os.mkdir("text-for-" + original_filename)

command = "cp " + temp_folder + "/"  + "*.txt text-for-" + original_filename
logger.info("Making a copy of all text files to text-for-" + original_filename)
logger.info("Running " + command)
os.system(command)




if keep_temp_folder_in_google_drive == "no":
    message =  "\nDeleting the Temp folder in Google Drive " + temp_folder + "\n"
    logger.info(message)
    service.files().delete(fileId=drive_folder_id).execute()


message =  "\n\nDone. Check the text files start with text_for_page_ "
logger.info(message)




result_text_count = len(glob.glob(temp_folder + "/" + 'text_for_page_*.txt'))

if not jpg_count == result_text_count:
    logger.info("\n\n=========ERROR===========\n\n")
    logger.info(" \n\nText files are not equal to PDF files. Some PDF files not OCRed. Run this script again to complete OCR all the Pages. \n\n")
    sys.exit()

#if  pdf_count == result_text_count:
#            logger.info("\n\nThe PDF files and result text files are equval. Now running the mediawiki_uploader.py script\n\n")
#            command = "python mediawiki_uploader.py"
#            os.system(command)
            

                                        
