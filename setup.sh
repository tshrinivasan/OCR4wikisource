#!/bin/bash

sudo apt-get install djvulibre-bin  libdjvulibre21   libtiff-tools mupdf mupdf-tools pdftk poppler-utils git djview
sudo pip install --upgrade google-api-python-client
sudo pip install clint requests wikitools poster oauth2client apiclient

sudo pip uninstall -y  apiclient
sudo pip uninstall -y google-api-python-client
sudo pip install google-api-python-client
sudo pip install gdcmdtools

sudo apt-get install python-software-properties
sudo add-apt-repository -y ppa:ubuntuhandbook1/apps
sudo apt-get update
sudo apt-get install mupdf-tools



wget http://mirrors.edge.kernel.org/ubuntu/pool/main/g/gcc-6/libgcj17_6.4.0-8ubuntu1_amd64.deb
wget https://launchpadlibrarian.net/277739894/pdftk_2.02-4build1_amd64.deb
wget http://mirrors.edge.kernel.org/ubuntu/pool/main/g/gcc-defaults/libgcj-common_6.4-3ubuntu1_all.deb
wget http://mirrors.edge.kernel.org/ubuntu/pool/main/g/gcc-6/libgcj17-dev_6.4.0-8ubuntu1_amd64.deb

sudo apt-get install gcc-6-base
sudo dpkg -i libgcj-common_6.4-3ubuntu1_all.deb
sudo dpkg -i libgcj17_6.4.0-8ubuntu1_amd64.deb
sudo dpkg -i pdftk_2.02-4build1_amd64.deb

rm -f *.deb
