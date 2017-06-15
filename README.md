# AmtWiki-Assist
Python program to assist admins of the AmtWiki

Currently command line only.
Requires Python 3.6.1 or above
Selenium 3.4.2 or able
Google Chrome

It will display a page that has been edited in the browser.
On the command line it will tell you 
  the message created by the editor
  the username of the editor
  how many edits have been made on this page
It will then ask if this is a spammer.
Appropriate answers are:
  y or Y if the user is a spammer.
  s or S to skip this page (To allow manual approvals)
  x or X to exit the program
  or just hit enter if it is not a spammer, to approve all edits.
  
The first time the program is run, it will ask you for your username and password for your wiki sign on. 
And will ask you if you want to save these. If you answer yes (y/Y), it will save your credentials and log you in
automattically in the future.

TODO:
Create GUI (Kivy and TKinter)
Create an options page (Choose browser/CLI etc..)


