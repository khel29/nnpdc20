# nnpdc20
Minimalist social media app, runs on a Raspberry Pi
- Running example: https://nini.mywire.org
- Make friends with interests and/or proximity match criteria
- Exchange messages and images with other users
- Respects your privacy thanks to data encryption.
- User Interface in French for now.

Setup of python flask app, for example on a raspberry pi:
- 1/ set Mysql/MariaDB users and database + 
   configure database access passwords in password.py file, and load mybase_fr.sql database templarte structure.
- 2/ install python3 dependancies with pip3 install ...
- 3/ use ddns + reverse proxy nginx for https
- 4/ configure email smtp parameters in password.py file
    (I use Citadel mail server on the same Pi)
- 5/ Define admin user in password.py file
  (only admin user can delete: status, genders, interests, users)

- 6/ Launch app with admin rights: nohup python3 me_fr.py&  (or with unicorn)
- 7/ Read html help page to use app



Some Improvement ideas, not implemented yet:

- have a common special user named 'all' where you can post and view messages from/to all the profiles. 
(Sort of public messages chat, without any images).
- possibility to delete all the messages individually if you are its author with a small delete button near each message (+ confirm popup.)
- Make english version of the app. Problem: there will be 2 distinct databases, sometimes sharing the same geographic locations. You know how to solve this?
- have the lets encrypt keys certificate working to avoid main mail providers spam box for the notifications.
