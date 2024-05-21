INSTALL
=======

Just run the below command

```
bash ./setup.sh
```

This will install all the required packages.




# API Setup
 * Create a new project for this tool to access your Google drive
    * Visit https://console.developers.google.com/ , create project, name it anything you like, ex: gdcmdtools.

 * Enable the following Google APIs in "APIs & auth/APIs"
    * Drive API


 * Make sure your application has an application name in "APIs & auth/Consent screen"
    * Find "PRODUCT NAME" field. Make sure it's not blank.

 * Grant access to Google Drive for gdcmdtools in "APIs & auth/Credentials"
    1. Click "Create new Client ID", APPLICATION TYPE: Installed application, INSTALLED APPLICATION TYPE: Other
    1. Check the section "Client ID for native application", click at the "Download JSON".
    1. Execute gdauth.py in a terminal and give the downloaded secret file just downloaded as parameter: $ gdauth.py client_secrets.json
    1. You will see message like: INFO:gdcmdtools.base:Please visit the URL in your browser: https://accounts.google.com/o/oauth2/auth?scope=....
    1. Visit the URL with browser and allow the app accessing your Google Drive.
    1. Copy the code you see in your browser, then back to the terminal, paste the code and hit enter.
    1. Done, you won't be asked for the code again unless the credential expired.



## Execution

Check the README.md for execution instructions.