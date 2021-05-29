# nnpdc20
Minimalist social media ap, runs on a Raspberry Pi
- Running example: https://nini.mywire.org
- Find other users with interests ans proximity criteria
- Exchange messages and images with orher users.
- User Interface in French for now.

Setup of python flask app, for example on a raspberry pi:
1/ set Mysql users and database + configure database access passwords in password.py file
2/ install dependancies with pip3 install ...
3/ use ddns + reverse proxy nginx for https
4/ configure email smtp parameters in password.py file
5/ Define admin user in password.py file
6/ Launch app with admin rights: nohup python3 me_fr.py&
7/ Read html help page to use app
