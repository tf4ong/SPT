# Home-cage Sucrose Preference Test
A scipt to run a chronic automated sucrose preference test of mice in home cage. The script is ran on a raspberry-pi with internet connection. A sucrose preferent tunnel is attached to a rodent cage. The tunnel consists of a RFID read for mouse identification, two double spouts for liquid dispension, IR light, and a fish-lens camera for behavir monitoring. An updated hardware list and setup instructions will be uploaded shortly. 
## MySql Database for Data Storage
- All behaviroal data (entries, exits, spout licked, type of reward dispensed) are logged on to the raspberry-pi MySql database. 
- The database is also hosted  by Apache HTTP Sever(version 2.4.43) and can be accessed through the internet
- Subsequent analytical scripts will also be uploaded
## RFID identification
- A ID-20LA RFID tag reader will be at the beginning of the SPT tunnel to identify each mouse
## spout choice
- At the end of the tunnel there are two double spouts on each side.
- A reward water/sucrose water is dispensed for every n links at each double spout. The n number of licks can be set accordingly
- Every 24 hour, the side which dispenses water/sucrose is swaped for the specific mout
