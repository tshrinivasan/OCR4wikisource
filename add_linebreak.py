import mwclient
from configparser import ConfigParser
import logging
import sys
import time
import datetime
import os
import urllib

book_name = "மறைமலையம்_1.pdf"
#book_name = "https://ta.wikisource.org/wiki/%E0%AE%AA%E0%AE%95%E0%AF%8D%E0%AE%95%E0%AE%AE%E0%AF%8D:%E0%AE%87%E0%AE%A8%E0%AF%8D%E0%AE%A4%E0%AE%BF%E0%AE%B0_%E0%AE%AE%E0%AF%8B%E0%AE%95%E0%AE%A9%E0%AE%BE.pdf"
#start = 1
#end = 122



config = ConfigParser(interpolation=None)
config.read("config.ini")


url = config.get('settings','file_url')
columns = config.get('settings','columns')
wiki_username = config.get('settings','wiki_username')
wiki_password = config.get('settings','wiki_password')
is_bot_user = config.get('settings','is_bot_user')
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
log_file = './log/page_fix_' + timestamp + '_log.txt'

handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)

# create a logging format

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger

logger.addHandler(handler)



logger.info("URL = " + url )
logger.info("Columns = " + columns )
logger.info("Wiki Username = " + wiki_username)
logger.info("Wiki Password = " + "Not logging the password")
logger.info("Wiki Source Language Code = " + wikisource_language_code )
logger.info("Edit Summary = " + edit_summary)

original_url = urllib.parse.unquote(url)

wiki_url =  wikisource_language_code + ".wikisource.org"
logger.info("Wiki URL = " + wiki_url)

user_agent = 'OCR4WikiSource/0.2 (tshrinivasan@gmail.com)'
site = mwclient.Site(wiki_url, clients_useragent=user_agent)

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



def add_linebreak(start,end):
    edit_summary = "added line breaks"

    counter = start
    for page_number in range(start,int(end)+1):
        
        pagename = "Page:" + book_name + "/" + str(page_number)
        
        logging.info("Page name = " + pagename)

           
#        content = open(text_file,'r').read()

#    message =  "\nUploading content for " + text_file
#    logging.info(message)

        page = wiki.pages[pagename]

        original_content = page.text()
        #print(original_content)

        original_content = original_content.split("\n")
        new_content = []
        for line in original_content:
#            print ("line="+line)
            if "________________" in line:
                line = line.replace("________________"," ")
            if line.startswith(" "):
                line = line.replace(" ","",1)
#                print(line)
            new_content.append(line + "\n\n")

        change = "".join(new_content)
        #print(change)
#        print(change)
        
#        sys.exit()
    #    page = wikitools.Page(wiki,"Page:"+ pagename, followRedir=True)

        if is_bot_user.lower() == 'true':
            page.edit(change,edit_summary,bot="True")
        #TODO - get bot status from the configfile and use here.
        else:                    
            page.edit(change,edit_summary)
        
        message = "Added linebreaks to https://" + wikisource_language_code + ".wikisource.org/wiki/" + pagename + "  " + str(counter) +"/" +  str(end) + "\n"
        logging.info(message)
        counter = counter + 1
        time.sleep(30)
        logging.info("=========")
#        sys.exit()

    


    '''        
    in_file = open(filename)

    out_file= open(temp_folder + "/"  + basename + ".txt","w")
    all_lines = in_file.readlines()
    for line in all_lines:
        out_file.write(line)
        out_file.write("\n")

    out_file.close()
    '''

add_linebreak(1,330)
