# AmtWiki-Assist
Python program to assist admins of the AmtWiki

Currently command line only.<br>
Requires Python 3.6.1 or above<br>
Selenium 3.4.2 or able<br>
Google Chrome<br>

It will display a page that has been edited in the browser.<br>
On the command line it will tell you <br>
  the message created by the editor<br>
  the username of the editor<br>
  how many edits have been made on this page<br>
It will then ask if this is a spammer.<br>
Appropriate answers are:<br>
  y or Y if the user is a spammer.<br>
  s or S to skip this page (To allow manual approvals)<br>
  x or X to exit the program<br>
  or just hit enter if it is not a spammer, to approve all edits.<br>
  
The first time the program is run, it will ask you for your username and password for your wiki sign on. And will ask you if you want to save these. If you answer yes (y/Y), it will save your credentials and log you in automattically in the future.

TODO:<br>
  Create GUI (Kivy and TKinter)<br>
  Create an options page (Choose browser/CLI etc..)<br>


