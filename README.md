employee-timecards
==================

A python script to take data from google spreadsheets and graph the data fairly easily.


Blue mountain's script is run as user bluemtnplumb. You can view the crontab for more information on how it is run, such as auths, etc

it calls out to google docs and pulls the info from the spreadsheet, then parses it.

if there are problems with the data parsing, there is no indication. The script simply fails to produce anything. 

The best thing to do in such a case is log in to atticus as bluemtnplumb user and run the script by hand to see how it fails.
