# -*- coding: utf-8 -*-

import wikitools
import poster
import os
import shutil
import sys
import ConfigParser
import time
import datetime
import glob
import urllib
import logging
import urllib2


version = "1.53"

config = ConfigParser.ConfigParser()
config.read("config.ini")

indic_numbers = ConfigParser.ConfigParser()
indic_numbers.read('indian_numerals.ini')


url = config.get('settings','file_url')
columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
wikisource_language_code = config.get('settings','wikisource_language_code')
edit_summary = config.get('settings','edit_summary')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


ts = time.time()
timestamp  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')


if not os.path.isdir("./log"):
            os.mkdir("./log")



# create a file handler
log_file = './log/mediawiki_uploader_' + timestamp + '_log.txt'

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

logging.info("Operating system = " + os_version)



logger.info("URL = " + url )
logger.info("Columns = " + columns )
logger.info("Wiki Username = " + wiki_username)
logger.info("Wiki Password = " + "Not logging the password")
logger.info("Wiki Source Language Code = " + wikisource_language_code )
logger.info("Edit Summary = " + edit_summary)





original_url = urllib.unquote(url).decode('utf8')
filename = os.path.basename(original_url)

filetype = filename.split('.')[-1].lower()

temp_folder = 'upload-'+ filename + "-" + timestamp

logger.info("File Name = " + filename)
logger.info("File Type = " + filetype)


logger.info("Original URL = " + original_url )




wiki_url = "https://" + wikisource_language_code + ".wikisource.org/w/api.php"

logger.info("Wiki URL = " + wiki_url)


try:
	wiki = wikitools.wiki.Wiki(wiki_url)
except:
	message =  "Can not connect with wiki. Check the URL"
	logger.info(message)




login_result = wiki.login(username=wiki_username,password=wiki_password)
message =  "Login Status = " + str(login_result)
logging.info(message)


if login_result == True:
        message =  "\n\nLogged in to "  +  wiki_url.split('/w')[0]
	logging.info(message)
else:
        message =  "Invalid username or password error"
	logging.info(message)
        sys.exit()





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






def convert_to_indic(language,number):
        if language in ['bn','or','gu','te','ml','kn']:
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
for textfile in glob.glob('text_for_page*.txt'):
        files.append(textfile)



for text_file in sorted(files):

        pageno = int(text_file.split('.')[0].split('_')[-1])
        
                            
	indic_page_number =  str(convert_to_indic(wikisource_language_code, pageno))   
	logging.info("Filename = " + filename)
	logging.info("Indic page no = " + indic_page_number)

   
        pagename = filename.encode('utf-8') + "/"  + indic_page_number
        logging.info("Page name = " + pagename)

           
        content = open(text_file,'r').read()

        message =  "\nUploading content for " + text_file
	logging.info(message)

        page = wikitools.Page(wiki,"Page:"+ pagename, followRedir=True)

        if bot_flag:
                    page.edit(text=content,summary=edit_summary,bot="True")
        else:                    
                    page.edit(text=content,summary=edit_summary)
        
        message = "Uploaded at https://" + wikisource_language_code + ".wikisource.org/wiki/Page:" + pagename + "\n"
	logging.info(message)
        time.sleep(5)
        logging.info("=========")


        move_file(text_file)
        
logging.info("\nDone. Uploaded all text files to wiki source\n\n\n")

                                                        

	

def clean_folders():
            if not os.path.isdir("./archives"):
                        os.mkdir("./archives")
            if not os.path.isdir("./archives/files-for-" + filename):
                        os.mkdir("./archives/files-for-" + filename)

           
            
            
            command = "mv  all_text_for* OCR* upload-* " + " ./archives/files-for-" + filename
            os.system(command.encode('utf-8'))

            command = "cp -R log " + " ./archives/files-for-" + filename
            os.system(command.encode('utf-8'))

            command = "rm -rf log"
            os.system(command.encode('utf-8'))
                
            
            command = "mv " + filename + " ./archives/files-for-" + filename
            os.system(command.encode('utf-8'))
                                    



logger.removeHandler(handler)
handler.flush()
handler.close()

time.sleep(2)

clean_folders()
