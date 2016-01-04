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

config = ConfigParser.ConfigParser()
config.read("config.ini")

indic_numbers = ConfigParser.ConfigParser()
indic_numbers.read('indian_numerals.ini')


url = config.get('settings','file_url')
columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
wikisource_language_code = config.get('settings','wikisource_language_code')



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


ts = time.time()
timestamp  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')


if not os.path.isdir("./log"):
            os.mkdir("./log")



# create a file handler
log_file = './log/mediawiki_uploader_' + timestamp + '.log'

handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)

# create a logging format

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger

logger.addHandler(handler)


version =  urllib2.urlopen('https://raw.githubusercontent.com/tshrinivasan/OCR4wikisource/master/VERSION').read()
logger.info("Running mediawiki_uploader.py " + version.strip('\n'))


logger.info("URL = " + url )
logger.info("Columns = " + columns )
logger.info("Wiki Username = " + wiki_username)
logger.info("Wiki Password = " + "Not logging the password")
logger.info("Wiki Source Language Code = " + wikisource_language_code )






original_url = urllib.unquote(url).decode('utf8')
filename = os.path.basename(original_url)

filetype = filename.split('.')[-1].lower()

temp_folder = 'temp-'+ timestamp

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
#        pageno = text_file.split('0')[-1].split('.')[0]
        pageno = int(text_file.split('.')[0].split('_')[-1])
        
        pagename = filename + "/"  + str(convert_to_indic(wikisource_language_code, pageno))
                            

           
        content = open(text_file,'r').read()

        message =  "\nUploading content for " + text_file
	logging.info(message)

        page = wikitools.Page(wiki,"Page:"+ pagename, followRedir=True)
        page.edit(text=content)
        message = "Uploaded at https://" + wikisource_language_code + ".wikisource.org/wiki/Page:" + pagename + "\n"
	logging.info(message)
        time.sleep(5)
        logging.info("=========")


        move_file(text_file)
        
logging.info("\nDone. Uploaded all text files to wiki source")

                                                        

	

