# Home-cage Sucrose Preference Test
A scipt to run a chronic automated sucrose preference test of mice in home cage. The script is ran on a raspberry-pi with internet connection. A sucrose preferent tunnel is attached to a rodent cage. The tunnel consists of a RFID read for mouse identification, two double spouts for liquid dispension, IR light, and a fish-lens camera for behavir monitoring. An update hardware list and setup instructions will be uploaded shortly. 
##MySql Database for Data Storage
- All behaviroal data (entries, exits, spout licked, type of reward dispensed) are logged on to the raspberry-pi MySql database. 
- The database is also hosted  by Apache HTTP Sever(version 2.4.43) and can be accessed through the internet
- Subsequent analytical scripts will also be uploaded
##RFID identification
