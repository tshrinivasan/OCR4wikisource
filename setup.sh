#!/bin/bash
# for ubuntu 23.10

sudo apt-get install djvulibre-bin  libdjvulibre21   libtiff-tools mupdf mupdf-tools pdftk poppler-utils git djview
sudo pip3 install clint requests  oauth2client 

sudo pip3 uninstall -y  apiclient
#sudo pip3 uninstall -y google-api-python-client
#sudo pip3 install google-api-python-client
#sudo pip3 install gdcmdtools

#sudo apt-get install python-software-properties
#sudo add-apt-repository -y ppa:ubuntuhandbook1/apps
#sudo apt-get update
sudo apt-get install mupdf-tools


#sudo add-apt-repository ppa:malteworld/ppa -y
#sudo apt update
#sudo apt install pdftk -y

sudo snap install pdftk

sudo pip3 install mwclient

# https://stackoverflow.com/a/61188575
sudo pip3 install httplib2==0.15.0

sudo pip3 install google-api-python-client==1.6
