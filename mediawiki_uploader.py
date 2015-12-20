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

config = ConfigParser.ConfigParser()
config.read("config.ini")

indic_numbers = ConfigParser.ConfigParser()
indic_numbers.read('indian_numerals.ini')


url = config.get('settings','file_url')

columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
wikisource_language_code = config.get('settings','wikisource_language_code')



ts = time.time()
timestamp  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')


filename = os.path.basename(url)
filetype = filename.split('.')[-1].lower()

temp_folder = 'temp-'+ timestamp



wiki_url = "https://" + wikisource_language_code + ".wikisource.org/w/api.php"


try:
	wiki = wikitools.wiki.Wiki(wiki_url)
except:
	print "Can not connect with wiki. Check the URL"


try:
	wiki.login(username=wiki_username,password=wiki_password)

except:
	print "Invalid Username or Password"


print "\n\nLogged In to " + wiki_url.split('/w')[0]




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
        print "Moving the file " + file + " to the folder " + temp_folder + "\n"
                                                




files = []
for textfile in glob.glob('text_for_page*.txt'):
        files.append(textfile)



for text_file in sorted(files):
#        pageno = text_file.split('0')[-1].split('.')[0]
        pageno = int(text_file.split('.')[0].split('_')[-1])

        pagename = filename + "/"  + convert_to_indic(wikisource_language_code, pageno)
                            

           
        content = open(text_file,'r').read()

        print "\nUploading content for " + text_file

        page = wikitools.Page(wiki,"Page:"+ pagename, followRedir=True)
        page.edit(text=content)
        print "Uploaded at https://" + wikisource_language_code + ".wikisource.org/wiki/Page:" + pagename + "\n"
        time.sleep(5)
        print "========="


        move_file(text_file)
        
print "\nDone. Uploaded all text files to wiki source"

                                                        

	

