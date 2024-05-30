# -*- coding: utf-8 -*-

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

import mwclient

version = "1.60"


#https://stackoverflow.com/questions/14340366/configparser-and-string-with
config = ConfigParser(interpolation=None)
config.read("config.ini")

indic_numbers = ConfigParser()
indic_numbers.read('indian_numerals.ini')


url = config.get('settings','file_url')
columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
is_bot_user = config.get('settings','is_bot_user')
wikisource_language_code = config.get('settings','wikisource_language_code')
edit_summary = config.get('settings','edit_summary')
users_page_suffix = config.get('settings','users_page_suffix')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


ts = time.time()
timestamp  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')


if not os.path.isdir("./log"):
    os.mkdir("./log")



# create a file handler
log_file = './log/wikisource_uploader_' + timestamp + '_log.txt'

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

logger.info("Running wikisource_uploader.py " + version)


os_info = open("/etc/lsb-release")
for line in os_info:
    if  "DISTRIB_DESCRIPTION" in line:
        os_version = line.split("=")[1]

logging.info("Operating system = " + os_version)


logger.info("URL = " + url )
logger.info("Columns = " + columns )
logger.info("Wiki Username = " + wiki_username)
logger.info("Wiki Password = " + "Not logging the password")
logger.info("Wiki Source Language Code = " + wikisource_language_code )
logger.info("Edit Summary = " + edit_summary)



original_url = urllib.parse.unquote(url)
filename = os.path.basename(original_url)

filetype = filename.split('.')[-1].lower()

temp_folder = 'upload-'+ filename + "-" + timestamp

logger.info("File Name = " + filename)
logger.info("File Type = " + filetype)


logger.info("Original URL = " + original_url )


wiki_url =  wikisource_language_code + ".wikisource.org"
logger.info("Wiki URL = " + wiki_url)

user_agent = 'OCR4WikiSource/0.2 (tshrinivasan@gmail.com)'
site = mwclient.Site(wiki_url, clients_useragent=user_agent)


#wiki_url = "https://" + wikisource_language_code + ".wikisource.org/w/api.php"

#logger.info("Wiki URL = " + wiki_url)


try:
#	wiki = wikitools.wiki.Wiki(wiki_url)
        wiki = mwclient.Site(wiki_url, clients_useragent=user_agent)

except:
        message =  "Can not connect with wiki. Check the URL"
        logger.info(message)
        sys.exit()


try:

    wiki.login(wiki_username,wiki_password)
    message =  "\n\nLogged in to "  +  wiki_url
    logging.info(message)

except mwclient.errors.LoginError as e:
    logger.error('Could not login to wikisource: %s' % e)
    sys.exit()    

'''
def check_for_bot(username):
  user = wikitools.User(wiki,username)
  if 'bot' in user.groups:
      return "True"



logging.info("Checking for bot access rights")
bot_flag = check_for_bot(wiki_username)

if bot_flag:
    logging.info("The user " + wiki_username + " has bot access.")
else:
    logging.info("The user " + wiki_username + " does not have bot access")
'''





def convert_to_indic(language,number):
    if language in ['bn','or','gu','ml','kn']:
        number_string = ''
        for num in list(str(number)):
            number_string = number_string + indic_numbers.get(language,num)
        return number_string
    else:
        return number


def move_file(file):
    source = file
    destination = temp_folder

    if os.path.isdir(temp_folder):
        shutil.move(source,destination)
    else:
        os.mkdir(temp_folder)
        shutil.move(source,destination)
    message = "Moving the file " + file + " to the folder " + temp_folder + "\n"
    logging.info(message)
                                                




files = []
source_folder = "text-for-"+filename + "/"
print(source_folder)
for textfile in glob.glob(source_folder + 'text_for_page*.txt'):
#for textfile in glob.glob(source_folder + 'page_*.txt'):
    files.append(textfile)

print(files)
print(len(files))

if len(files) == 0:
    print("No files available")
    sys.exit()

total_files = len(files)

counter = 1
for text_file in sorted(files):

    pageno = int(text_file.split('_')[-1].split(".")[0])
        
                            
    indic_page_number =  str(convert_to_indic(wikisource_language_code, pageno))   
    logging.info("Filename = " + filename)
    logging.info("Indic page no = " + indic_page_number)

   
    pagename = "Page:" + filename + "/"  + indic_page_number
    logging.info("Page name = " + pagename)

           
    content = open(text_file,'r').read()

    if "________________" in content:
        content = content.replace("________________"," ")
 
    message =  "\nUploading content for " + text_file
    logging.info(message)

    page = wiki.pages[pagename]

    #    page = wikitools.Page(wiki,"Page:"+ pagename, followRedir=True)

    if is_bot_user.lower() == 'true':
        page.edit(content,edit_summary,bot="True")
        #TODO - get bot status from the configfile and use here.
    else:                    
        page.edit(content,edit_summary)
        
    message = "Uploaded at https://" + wikisource_language_code + ".wikisource.org/wiki/" + pagename + " " + str(counter) + "/" + str(total_files) + "\n"
    logging.info(message)

    if is_bot_user.lower() == "true":
        time.sleep(5)
    else:
        time.sleep(30)
    logging.info("=========")

    counter = counter + 1
    move_file(text_file)
        
logging.info("\nDone. Uploaded all text files to wiki source\n\n\n")

#book_name = url.split("/")[-1]

line_to_add = "https://" + wiki_url + "/wiki/Index:" + filename

userpage = "User:" + wiki_username + "/" +users_page_suffix

logging.info("User Page name = " + wiki_username)

page = wiki.pages[userpage]

original_content = page.text()
        #print(original_content)

new_content = original_content + "\n\n" + line_to_add

if is_bot_user.lower() == 'true':
    page.edit(new_content,edit_summary,bot="True")
        #TODO - get bot status from the configfile and use here.
else:                    
    page.edit(new_content,edit_summary)

logging.info("updated the book name to users page " + userpage )
 


                                                        

	

def clean_folders():
    if not os.path.isdir("./archives"):
        os.mkdir("./archives")
    if not os.path.isdir("./archives/files-for-" + filename):
        os.mkdir("./archives/files-for-" + filename)

           
            
            
    command = "mv text-*  ocr-* upload-* " + " ./archives/files-for-" + filename
    os.system(command)

    command = "cp -R log " + " ./archives/files-for-" + filename
    os.system(command)

    
    #command = "rm -rf log"
    #os.system(command)
                
            
    #command = "mv " + filename + " ./archives/files-for-" + filename
    #os.system(command)
                                    



logger.removeHandler(handler)
handler.flush()
handler.close()

time.sleep(2)

clean_folders()
