#!/bin/bash

sudo apt-get install djvulibre-bin  libdjvulibre21   libtiff-tools mupdf mupdf-tools pdftk poppler-utils git djview
sudo -H pip install --upgrade google-api-python-client
sudo -H pip install clint requests wikitools poster oauth2client apiclient

sudo -H pip uninstall -y  apiclient
sudo -H pip uninstall -y google-api-python-client
sudo -H pip install google-api-python-client
sudo -H pip install gdcmdtools
sudo -H pip install django

sudo apt-get install python-software-properties
sudo add-apt-repository -y ppa:ubuntuhandbook1/apps
sudo apt-get update
sudo apt-get install mupdf-tools
