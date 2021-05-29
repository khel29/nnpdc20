# nnpdc20
Minimalist social media app on Raspberry Pi
Setup of python flask app.
User Interface in French for now.

Set up on a raspberry pi:
1/ set Mysql users and database + configure database access passwords in password.py file
2/ install dependancies with pip3 install ...
3/ use ddns + reverse proxy nginx for https
4/ configure email smtp parameters in password.py file
Launch app with admin rights:
>> 

nohup python3 me_fr.py&
