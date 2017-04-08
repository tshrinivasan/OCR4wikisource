import os
import subprocess
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

def index(request):
	os.system("rm config.ini")
	file_url = request.POST.get("file_url", "")
	columns = request.POST.get("columns", "")
	wiki_username = request.POST.get("wiki_username", "")
	wiki_password = request.POST.get("wiki_password", "")
	wikisource_language_code = request.POST.get("wikisource_language_code", "")
	keep_temp_folder_in_google_drive = request.POST.get("keep_temp_folder_in_google_drive", "")
	edit_summary = request.POST.get("edit_summary", "")
	con = open('config.ini', 'w')
	con.write("[settings]\n\n")
	con.write("file_url = "+file_url+'\n')
	con.write("columns = "+columns+'\n')
	con.write("wiki_username = "+wiki_username+'\n')
	con.write("wiki_password = "+wiki_password+'\n')
	con.write("wikisource_language_code = "+wikisource_language_code+'\n')
	con.write("keep_temp_folder_in_google_drive = "+keep_temp_folder_in_google_drive+'\n')
	con.write("edit_summary = "+edit_summary+'\n')
	con.close()
	os.system("python do_ocr.py")
   	return render(request, 'hello.html', {})