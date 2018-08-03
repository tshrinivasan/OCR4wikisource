Version
=======
1.56

Notes
=====
* This program is evolving heavily.
* Always use the latest version.
* Compare the version number with your's version.

Feel free to report any errors in the issues section.

# OCR4wikisource
There are many PDF files and DJVU files in WikiSource in various languages.
In many wikisource projects, those files are splited into individual page as an
Image, using proofRead extension.

Contributors see those images and type them manually.

This project helps the wikisource team to OCR the entire PDF or DJVU file,
using the google drive OCR. Then it will update the relevant page in the
wikisource with the text.

The OCR will not give 100% correct text. But still, it is better than typing
entire page manually.

To run this, you need a GNU/Linux system. Sorry Windows guys. It uses the
commandline utilities available in GNU/Linux heavily.

Check the file INSTALL for installation instructions

config.ini
==========
Edit this file and fill the details as file_url, columns, wiki_usernmae,
wiki_password, wikisource_language_code

do_ocr.py
========
Run this as

```
python do_ocr.py
```

This will do the following things.

* download the file
* if it is DJVU, convert to PDF
* split it into individual files based on column no
* create a folder in your Google Drive
* upload the PDF files to Google Drive
* Download the OCRed text
* split, merge the text files properly to fit as the PDF files


This will give text files as 'text_for_page_00001.txt' etc equvalent to the no of pages in the PDF file.


mediawiki_uploader.py
=====================
run as

```
python mediawiki_uploader.py
```

This uploads the text files provided by do_ocr.py to the wikisource details you provided in config.ini

For testing you can keep only few files provided by do_ocr.py (example from text_for_page_00001.txt to text_for_page_00005.txt)
Move all other text files to another folder.
Once you are satisfied, you can place all the files in the current folder.


For this, the PDF or DJVU file should be already splitted into individual pages in wiki souce, using Proofread extension for wikisource.

```
Example :  "https://" + wikisource_language_code + ".wikisource.org/wiki/Page:" + filename/pageno
```

Contact your wikisource team for splitting the files into individual pages.

ToDo
====
* This program uplads single page PDF to google drive. Google accepts 10 page PDF files. Create 10 page pdf files, upload, split the text files for faster operations.
* Give a web interface using Django or Flask.
* Port to other Operating Systems like Windows.

Contact
=======
T Shrinivasan <tshrinivasan@gmail.com>
