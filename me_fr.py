
# Ninipraudchien2.0 app
# MIT Copyleft Niakniak 2021
import glob
from cryptography.fernet import Fernet
import onetimepad as otpd
from flaskext.mysql import MySQL
from funcs import *
from mails import *
import flask
import mpu
from dateutil.relativedelta import relativedelta
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
import mysql.connector
import hashlib
from datetime import datetime
from datetime import timedelta
from flask import Flask,render_template,request
import logging
import secrets
from passwords import *

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
import time
import threading

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])

def cleanup(name):
    time.sleep(60.0) #suppression des images en clair apres 1 minute
    try:
        os.remove(name)
    except:
        pass

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


logging.basicConfig(level=logging.DEBUG) #uncomment for debug mode
# todo:
# check if fields not null and if they dont already exist before adding them in base
# allow multiple genders status  interests
# allow interests pre selection with wildcards in  search page

cnx =""
app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 16 * 1024 * 1024

app.secret_key = pwd_secret_key_flask
app.permanent_session_lifetime = timedelta(minutes=15)

nosqlstrs=["truncate","grant","drop","TRUNCATE", "GRANT" , "*", "DROP", "=",  "--", " OR ", "#", "/", "+", "\\", " AND ", "true", "false", ";", ":","`", "%%"]
mysql2 = MySQL(app)
app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_PORT'] = pwd_mysql_port
app.config['MYSQL_DATABASE_USER'] = pwd_mysql_user
app.config['MYSQL_DATABASE_PASSWORD'] = pwd_mysql_database 
app.config['MYSQL_DATABASE_DB'] = pwd_mysql_base
mysql2.init_app(app)

def ecr(stri):
    try:
        v = otpd.encrypt(stri, pwd_enc_decryption)
        return v
    except:
        pass
        return "encryption problem."
def dcr(stri):
    try:
        v = otpd.decrypt(stri, pwd_enc_decryption)
        return v
    except:
        pass
        return "decryption problem."

def nosql(str):
    for nnn in nosqlstrs:
        str=str.replace(nnn, "_")
    return str

def getinfostr(usid,ctcid,cur):
                if usid==0 or ctcid==0:	
                    return ""
                selecteduserid=ctcid
                txt="SELECT name,birthday,comment,lastconnection,notification FROM  users WHERE user_id='"+str(selecteduserid)+"';"
                app.logger.info("sql get infos1:"+txt)
                cur.execute(txt)
                infos =cur.fetchall()

                txt="SELECT users.user_id,users.name, gender.gender_desc,\
                status.status_desc, interests.interest_desc\
                FROM users JOIN gender JOIN status JOIN interests ON\
                users.gender_id = gender.gender_id\
                AND users.status_id = status.status_id AND users.interests_id= \
                interests.interest_id\
                WHERE users.user_id="+selecteduserid+";"
                app.logger.info("sql get infos2:"+txt)
                cur.execute(txt)
                infos2 =cur.fetchall()

                userage=abs(relativedelta(infos[0][1],datetime.utcnow()).years)

                txt="SELECT locationlat,locationlong FROM  users WHERE user_id='"+str(selecteduserid)+"';"
                app.logger.info("sql get ctc loc:"+txt)
                cur.execute(txt)
                posctc =cur.fetchall()

                txt="SELECT locationlat,locationlong FROM  users WHERE user_id='"+str(usid)+"';"
                app.logger.info("sql get my loc:"+txt)
                cur.execute(txt)
                posmy =cur.fetchall()

                dist ="%.3f" % mpu.haversine_distance(\
                (float(posmy[0][0]), float(posmy[0][1])), \
                (float(posctc[0][0]), float(posctc[0][1])))


                if(infos[0][4]==1):
                    notifs="oui"
                else:
                    notifs="non"

                deg = get_bearing(\
                float(posmy[0][0]), float(posmy[0][1]), \
                float(posctc[0][0]), float(posctc[0][1]))
                direc=getdirs(deg)
                direc=direc.replace("W","O")
                direc=direc.replace("w","o")
                infosmsg = infos[0][0]+" ,  age: "+str(userage)+" ans,  genre: "+\
                infos2[0][2]+" ,  statut: "+ infos2[0][3]+" ,  centre d'intérêt: "+ \
                infos2[0][4]+ " ,  présentation: "+infos[0][2]+" ,  distance: "+dist+" km ,  direction: "+direc+" ,  dernière connexion: "+str(infos[0][3])+  " ,  notifications par e-mail: "+ notifs

                return infosmsg

def myhash(stri):
    res = hashlib.sha1(stri.encode())
    return (res.hexdigest())

#input: 1d array
def buildintxt1(myarray):
        if len(myarray)==0:
            return " ( -1 ) "
        else:
            i=0
            txt2=" ( "
            for ctcs in myarray:
                txt2=txt2+str(ctcs)
                if i != (len(myarray)-1):
                    txt2=txt2+","
                i=i+1
            txt2=txt2+" ) "
            return txt2


#input: 2d array
def buildintxt(myarray,column=0):
        if len(myarray)==0:
            return " ( -1 ) "
        else:
            i=0
            txt2=" ( "
            for ctcs in myarray:
                txt2=txt2+str(ctcs[column])
                if i != (len(myarray)-1):
                    txt2=txt2+","
                i=i+1
            txt2=txt2+" ) "
            return txt2

def getctcts(usid,cur):
            txt ="SELECT DISTINCT messages.id_touser from messages where\
            (messages.id_touser<>"+usid+" AND messages.id_fromuser="+usid+") UNION SELECT DISTINCT\
            messages.id_fromuser from messages where (messages.id_fromuser<>"+usid+"\
            AND messages.id_touser="+usid+") ORDER BY id_touser ASC;"
            app.logger.info("sql get ctcs:"+txt)
            cur.execute(txt)
            ctcsids =cur.fetchall()
            txt2= "SELECT user_id,name,lastconnection FROM users WHERE user_id IN" +\
            buildintxt(ctcsids)+";"
            app.logger.info("sql get ctcs names:"+txt2)
            cur.execute(txt2)
            userslist =cur.fetchall()
            return userslist


def write_key():
    #Generates a key and save it into a file
    key =  Fernet.generate_key()
    if os.path.isfile("key.key")==False:
        with open("key.key", "wb") as key_file:
            key_file.write(key)

def encrypt(filenamein,filenameout ):
    write_key()
    key = open("key.key", "rb").read()
    f = Fernet(key)
    with open(filenamein, "rb") as file:
        file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        with open(filenameout, "wb") as file:
            file.write(encrypted_data)

def decrypt(filenamein,filenameout):
    key = open("key.key", "rb").read()
    f = Fernet(key)
    with open(filenamein, "rb") as file:
        encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        with open(filenameout, "wb") as file:
            file.write(decrypted_data)

def cleanup_tmp_files(): #supprimme les fichiers image en clair qui pourraient rester apres un crash
    decrfilesname = "decr_*.*"
    decrfullfilesnames = os.path.join(app.config['UPLOAD_FOLDER'],decrfilesname)
    fileList = glob.glob( decrfullfilesnames)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            #print("Error while deleting file : ", filePath)
            pass

@app.route("/get_my_ip",methods=["GET"])
def get_my_ip():
    return  request.remote_addr


@app.route('/help_fr.html')
def helppage():
    ip=get_my_ip()
    app.logger.info("get ip:"+str(ip))
    return render_template('help_fr.html')

@app.route('/messages_fr.html', methods=["POST", "GET"])
def msgs():
    if "user" in session:
        if 'btnbck' in request.form:
            return render_template('index_fr.html')
        cnx = mysql2.connect();cur=cnx.cursor()
        user = session["user"]
        messages =mess=[]
        cur.execute("SELECT user_id,notification FROM  users WHERE name='"+user+"';") 
        usids =cur.fetchall()
        usid = str(usids[0][0])
        infosmsg="   "

        #cleanup_tmp_files() #cleanup previously decrypted images

        if request.method == "GET" :
            userslist=getctcts(usid,cur)
            dspmsgs=0

            txt= "Select id_fromuser , count(*) from messages where id_touser = "+str(usid)+" and rank_to =0 group by id_fromuser"
            app.logger.info("sql get nor red msgs:"+txt)
            cur.execute(txt)
            notred =cur.fetchall()

            cur.close();cnx.close()
            return render_template('messages_fr.html',user=user,messages=messages,userslist=userslist,dspmsgs=dspmsgs,selecteduserid='1',notred=notred,mess=mess)

        if request.method == "POST":
            selecteduserid = request.form['userslist']
            app.logger.info("userselected:"+str(selecteduserid))
            
            userslist=getctcts(usid,cur)
            app.logger.info("userslist:"+str(userslist))
            ctcid = str(request.form['userslist'])

            imuid="0"
            if 'file1' in request.files:
                file = request.files['file1']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename != '':
                #    flash('No selected file')
                #    return redirect(request.url)
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        extens= filename[-4:]
                        fulid = uuid.uuid4().hex
                        filename= fulid[:-4]+extens
                        fulid = "tmp_"+str(uuid.uuid4().hex)
                        file.save(fulid)
                        encrfilefullname=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        encrypt(fulid,encrfilefullname)
                        imuid=filename
                        os.remove(fulid)

            if ('btnm' in request.form) :
                msg = str(nosql(request.form['message']))
                datet = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                txt="INSERT INTO messages(id_fromuser,id_touser,message,image_uuid,rank_to,image_load_counter, date) VALUE ('"+usid+"','"+ctcid+"','"+ecr(msg)+"','"+str(imuid)+"','"+str(0)+"','"+str(0)+"','"+datet+"');"
                app.logger.info("sql insert msg:"+txt)
                cur.execute(txt)
                cnx.commit()

                mmsg=""
                if 'notification' in request.form:
                    notif = request.form['notification']
                else:
                    notif = ""

                if (notif=="on" ):
                    selecteduserid = request.form['notification']
                    cur.execute("SELECT email, name,notification FROM  users WHERE user_id='"+ctcid+"';")
                    ret =cur.fetchall()
                    mmail = str(ret[0][0])
                    uname =str(ret[0][1])
                    notifctc =str(ret[0][2])
                    if 'includen' in request.form:
                        incl = request.form['includen']
                    else:
                        incl = ""

                    if (incl=="on"):
                        mmsg ="Msg de: " +uname+": "
                    else:
                        mmsg="Hi. "

                    if ( notifctc=='1'):
                        sendemail ( mmsg+msg,mmail)

            if 'btnd' in request.form:
                #remove image files
                txt="SELECT  messages.image_uuid \
                FROM users FULL JOIN messages ON user_id = messages.id_fromuser \
                AND ((messages.id_fromuser="+usid+" AND messages.id_touser="+ctcid+") OR \
                (messages.id_fromuser="+ctcid+" AND\
                messages.id_touser="+usid+")) ;"
                app.logger.info("sql sel all messages to delete:"+txt)
                cur.execute(txt)
                uuids =cur.fetchall()
                for uuidf in uuids :
                    decrfilefullname=os.path.join(app.config['UPLOAD_FOLDER'],"decr_" +uuidf[0])
                    filefullname=os.path.join(app.config['UPLOAD_FOLDER'], uuidf[0])
                    try:
                        os.remove(filefullname)
                    except:
                        pass

                txt="SELECT  messages.message_id \
                FROM users FULL JOIN messages ON user_id = messages.id_fromuser \
                AND ((messages.id_fromuser="+usid+" AND messages.id_touser="+ctcid+") OR \
                (messages.id_fromuser="+ctcid+" AND\
                messages.id_touser="+usid+")) ;"
                app.logger.info("sql sel all messages to delete:"+txt)
                cur.execute(txt)
                msids =cur.fetchall()

                txt="DELETE from messages WHERE messages.message_id IN"+buildintxt(msids)+" ;"
                app.logger.info("sql del all messages:"+txt)
                cur.execute(txt)
                cnx.commit()

                userslist=getctcts(usid,cur)
                dspmsgs=0

                txt= "Select id_fromuser , count(*) from messages where id_touser = "+str(usid)+" and rank_to =0 group by id_fromuser"
                app.logger.info("sql get no red msgs:"+txt)
                cur.execute(txt)
                notred =cur.fetchall()

                cur.close();cnx.close()
                return render_template('messages_fr.html',imuid=imuid,notred=notred,user=user,messages=messages,userslist=userslist,dspmsgs=dspmsgs,selecteduserid='1',mess=mess)

            if ('btns' in request.form ):
                txt="UPDATE messages SET rank_to = rank_to + 1 WHERE  messages.id_touser="+str(usid)+" AND messages.id_fromuser = "+str(ctcid)+" ;"
                app.logger.info("sql inc rank msgs from selected user:"+txt)
                cur.execute(txt)
                cnx.commit()

            if ('btnm' in request.form )or ('btns' in request.form):
                txt="SELECT name, messages.message , messages.date, messages.rank_to, messages.image_uuid\
                FROM users FULL JOIN messages ON user_id = messages.id_fromuser \
                AND ((messages.id_fromuser="+usid+" AND messages.id_touser="+ctcid+") OR \
                (messages.id_fromuser="+ctcid+" AND\
                messages.id_touser="+usid+")) ;"
                app.logger.info("sql get messages:"+txt)
                cur.execute(txt)
                messages =cur.fetchall()
                dspmsgs=1
                infosmsg=getinfostr(usid,ctcid,cur)

                vv=0
                mess=[""]*(len(messages)+1)
                imagefiles=[""]*(len(messages)+1)

                for mx in messages: # decrypt all messages
                    dd=dcr(str((messages[vv][1])))
                    app.logger.info("dd:"+str(dd))
                    app.logger.info("message[vv][1]:"+str(messages[vv][1]))
                    mess[vv]=str(dd)
                    if mx[3]>=2 and mx[4]!="0":
                        try:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], mx[4]))
                        except:
                            pass
                        txt= "update messages set image_uuid='suppr' where rank_to >= 2 and image_uuid!='0'"
                        cur.execute(txt)
                        cnx.commit()
                    if mx[3]<=1 and mx[4]!="0":
                        extens= mx[4][-4:]
                        fulid = uuid.uuid4().hex
                        decrfilefullname=os.path.join(app.config['UPLOAD_FOLDER'],"decr_"+str(fulid) +mx[4])

                        #decrypt here
                        filefullname=os.path.join(app.config['UPLOAD_FOLDER'], mx[4])
                        decrypt(filefullname,decrfilefullname)
                        imagefiles[vv]="decr_"+str(fulid) +mx[4]

                        x = threading.Thread(target=cleanup, args=( decrfilefullname,), daemon=False)
                        x.start()
                    else:
                        if mx[4]!="0":
                            decrfilefullname=os.path.join(app.config['UPLOAD_FOLDER'],"decr_" +mx[4])
                            imagefiles[vv]="suppr"
                    vv=vv+1

                txt= "Select id_fromuser , count(*) from messages where id_touser = "+str(usid)+" and rank_to =0 group by id_fromuser"
                app.logger.info("sql get nor red msgs:"+txt)
                cur.execute(txt)
                notred =cur.fetchall()

                cur.close();cnx.close()
                if infosmsg[-3:]=='oui':
                    notifs=1
                else:
                    notifs=0
                return  render_template('messages_fr.html',imagefiles=imagefiles,imuid=imuid,notred=notred,user=user,messages=messages,userslist=userslist,dspmsgs=dspmsgs,selecteduserid=selecteduserid,infomsg=infosmsg, mess=mess, notifs=notifs)
    else:
        return redirect(url_for("login"))


@app.route('/me_fr.html',methods=['GET'])
def index():
    infos=[]
    name=""
    cnx = mysql2.connect();cur=cnx.cursor()
    cur.execute('SELECT gender_id, gender_desc FROM gender ORDER BY used ASC;')
    genders =cur.fetchall()
    cur.execute('SELECT status_id, status_desc FROM status ORDER BY used ASC;')
    status =cur.fetchall()
    cur.execute('SELECT interest_id, interest_desc FROM interests  ORDER BY used ASC;')
    interests =cur.fetchall()

    if "user" in session:
        name = session["user"] 
        cur.execute("SELECT *  FROM users WHERE name = '"+name+"';")
        infos =cur.fetchall()

        cur.execute("SELECT name FROM users;")
        userslist =cur.fetchall()

        cur.close();cnx.close()
        return render_template('me_fr.html',userslist=userslist,pwd_admin_name=pwd_admin_name,username=name, genders = genders, interests=interests,status=status,addit=0,infos=infos )
    else:
        cur.close();cnx.close()
        return render_template('me_fr.html',pwd_admin_name=pwd_admin_name,username=name, genders = genders, interests=interests,status=status, addit=1, infos=infos)

@app.route('/me_fr.html', methods=['POST']) 
def my_form_post():
    global cnx;
    infos=[]
    name =""
    if 'btnbck' in request.form:
        return render_template('index_fr.html')

    comment = nosql(request.form['comment'])
    email = nosql(request.form['email'])
    password = nosql(request.form['password'])
    cpassword = nosql(request.form['cpassword'])
    genre = nosql(request.form['genders'])
    interest = nosql(request.form['interests'])
    status = nosql(request.form['status'])
    currdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')


    cnx = mysql2.connect();cur=cnx.cursor()


    cur.execute('SELECT gender_id, gender_desc FROM gender ORDER BY used ASC;')
    genders =cur.fetchall()
    cur.execute('SELECT status_id, status_desc FROM status ORDER BY used ASC;')
    status =cur.fetchall()
    cur.execute('SELECT interest_id, interest_desc FROM interests  ORDER BY used ASC;')
    interests =cur.fetchall()

    sizeg=len(genders)
    sizes=len(status)
    sizei=len(interests)

    if "user" in session:
        cur.execute("SELECT name FROM users;")
        userslist =cur.fetchall()
        name = session["user"]
        cur.execute("SELECT *  FROM users WHERE name = '"+name+"';")
        infos =cur.fetchall()

    if  'addg' in request.form and sizeg<=50:
        text = nosql(request.form['add gender'])
        if text !="":
            cur.execute("SELECT gender_desc FROM gender WHERE gender_desc = '"+text+"';")
            isany =cur.fetchall()
            if  len(isany)==0:
                cur.execute("SELECT MIN(used)  FROM gender;")
                ming =cur.fetchall()
                cur.execute("INSERT INTO gender(gender_desc,used) VALUE ('"+text+"','"+str(ming[0][0])+"');")
                cnx.commit()
                cur.execute('SELECT gender_id, gender_desc FROM gender ORDER BY used ASC;')
                genders =cur.fetchall()


    if  'delg' in request.form:
        genre = request.form['genders']
        #find all used instances of deleted gender and replace them with the default one
        txt="SELECT user_id FROM users WHERE gender_id = "+str(genre)+";"
        app.logger.info("find gender id:"+txt)
        cur.execute(txt)
        isany =cur.fetchall()
        if  len(isany)!=0:
            gstr=buildintxt(isany)
            txt="SELECT gender_id FROM gender WHERE gender_desc = 'Default';"
            cur.execute(txt)
            app.logger.info(" users: ids to update"+txt)
            isany =cur.fetchall()
            if  len(isany)!=0:
                gid=str(isany[0][0])
            else:
                gid=str(1)
            txt="UPDATE  users SET gender_id="+gid+" WHERE user_id IN "+gstr+";"
            app.logger.info("mod users deleted gender:"+txt)
            cur.execute(txt)
            cnx.commit()
        txt="DELETE from gender WHERE gender_id ="+str(genre)+" ;"
        app.logger.info("del gender:"+txt)
        cur.execute(txt)
        cnx.commit()
        cur.execute('SELECT gender_id, gender_desc FROM gender ORDER BY used ASC;')
        genders =cur.fetchall()

    if  'adds' in request.form and sizes<=75:
        text = nosql(request.form['add status'])
        if text !="":
            cur.execute("SELECT status_desc FROM status WHERE status_desc = '"+text+"';")
            isany =cur.fetchall()
            if  len(isany)==0:
                cur.execute("SELECT MIN(used)  FROM status;")
                mins =cur.fetchall()
                cur.execute("INSERT INTO status(status_desc,used) VALUE ('"+text+"','"+str(mins[0][0])+"');")
                cnx.commit()
                cur.execute('SELECT status_id, status_desc FROM status ORDER BY used ASC;')
                status =cur.fetchall()

    if  'dels' in request.form:
        genre = request.form['status']
        #find all used instances of deleted gender and replace them with the default one
        txt="SELECT user_id FROM users WHERE status_id = "+str(genre)+";"
        app.logger.info("find status id:"+txt)
        cur.execute(txt)
        isany =cur.fetchall()
        if  len(isany)!=0:
            gstr=buildintxt(isany)
            txt="SELECT status_id FROM status WHERE status_desc = 'Default';"
            cur.execute(txt)
            app.logger.info(" users: ids to update"+txt)
            isany =cur.fetchall()
            if  len(isany)!=0:
                gid=str(isany[0][0])
            else:
                gid=str(1)
            txt="UPDATE  users SET status_id="+gid+" WHERE user_id IN "+gstr+";"
            app.logger.info("mod users deleted status:"+txt)
            cur.execute(txt)
            cnx.commit()
        txt="DELETE from status WHERE status_id ="+str(genre)+" ;"
        app.logger.info("del status:"+txt)
        cur.execute(txt)
        cnx.commit()
        cur.execute('SELECT status_id, status_desc FROM status ORDER BY used ASC;')
        status =cur.fetchall()

    if  'addi' in request.form and sizei<=200:
        text = nosql(request.form['add interest'])
        if text !="":
            cur.execute("SELECT interest_desc FROM interests WHERE interest_desc = '"+text+"';")
            isany =cur.fetchall()
            if  len(isany)==0:
                cur.execute("SELECT MIN(used)  FROM interests;")
                mini =cur.fetchall()
                cur.execute("INSERT INTO interests(interest_desc,used) VALUE ('"+text+"','"+str(mini[0][0])+"');")
                cnx.commit()
                cur.execute('SELECT interest_id, interest_desc FROM interests  ORDER BY used ASC;')
                interests =cur.fetchall()

    if  'deli' in request.form:
        genre = request.form['interests']
        #find all used instances of deleted gender and replace them with the default one
        txt="SELECT user_id FROM users WHERE interests_id = "+str(genre)+";"
        app.logger.info("find interest id:"+txt)
        cur.execute(txt)
        isany =cur.fetchall()
        if  len(isany)!=0:
            gstr=buildintxt(isany)
       	    txt="SELECT interest_id FROM interests WHERE interest_desc = 'Default';"
            cur.execute(txt)
            app.logger.info(" users: ids to update"+txt)
            isany =cur.fetchall()
            if  len(isany)!=0:
                gid=str(isany[0][0])
            else:
                gid=str(1)
            txt="UPDATE  users SET interests_id="+gid+" WHERE user_id IN "+gstr+";"
            app.logger.info("mod users deleted interest:"+txt)
            cur.execute(txt)
            cnx.commit()
        txt="DELETE from interests WHERE interest_id ="+str(genre)+" ;"
        app.logger.info("del interest:"+txt)
        cur.execute(txt)
        cnx.commit()
        cur.execute('SELECT interest_id, interest_desc FROM interests  ORDER BY used ASC;')
        interests =cur.fetchall()

    if  'deluser' in request.form:
        name = request.form['listofusers']
        app.logger.info("delete user: "+name)

    if  'delu' in request.form or  'deluser' in request.form :
                #delete all messages from to user
                cur.execute("SELECT user_id FROM  users WHERE name='"+name+"';")
                geted =cur.fetchall()
                ctcid=geted[0][0]

                txt="SELECT\
                messages.image_uuid FROM messages\
                WHERE  messages.id_touser="+str(ctcid)+" OR \
                messages.id_fromuser="+str(ctcid)+" ;"
                app.logger.info("sql sel all images to delete:"+txt)
                cur.execute(txt)
                uuids =cur.fetchall()
                for uuidf in uuids :
                    decrfilefullname=os.path.join(app.config['UPLOAD_FOLDER'],"decr_" +uuidf[0])
                    filefullname=os.path.join(app.config['UPLOAD_FOLDER'], uuidf[0])
                    try:
                        os.remove(filefullname)
                    except:
                        pass


                txt="DELETE\
                FROM messages\
                WHERE  messages.id_touser="+str(ctcid)+" OR \
                messages.id_fromuser="+str(ctcid)+" ;"
                app.logger.info("sql sel all messages to delete:"+txt)
                cur.execute(txt)
                cnx.commit()

                txt="DELETE from users WHERE user_id ="+str(ctcid) +" ;"
                app.logger.info("del user:"+txt)
                cur.execute(txt)
                cnx.commit()

                logout()



    if  'modu' in request.form:
        comment = nosql(request.form['comment'])
        email = nosql(request.form['email'])
        password = nosql(request.form['password'])
        cpassword = nosql(request.form['cpassword'])
        genre = nosql(request.form['genders'])
        interest = nosql(request.form['interests'])
        status = nosql(request.form['status'])
        currdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        if password!="" and password == cpassword:
            if 'notification' in request.form:
                notif=1
            else:
                notif=0

            if 'changepwd' in request.form:
                    txt="UPDATE  users SET comment='"+comment+"',lastconnection='"+currdate+"',gender_id='"+genre+"',interests_id='"+interest+"',status_id='"+status+"',email='"+email+"',pwdhash='"+str(myhash(password))+"' , notification='"+str(notif)+"' WHERE user_id='"+str(infos[0][0])+"';"
                    app.logger.info(txt)
                    cur.execute(txt)
                    cnx.commit()

            else:
                if(infos[0][12]==myhash(password)):
                    txt="UPDATE  users SET comment='"+comment+"',lastconnection='"+currdate+"',gender_id='"+genre+"',interests_id='"+interest+"',status_id='"+status+"',email='"+email+"' , notification='"+str(notif)+"' WHERE user_id='"+str(infos[0][0])+"';"
                    app.logger.info(txt)
                    cur.execute(txt)
                    cnx.commit()
                else:
                    cur.close();cnx.close()
                    return "Erreur: mot de passe nécessaire pour réaliser cette opération."

            cur.close();cnx.close()
            return "parametres utilisateur changés !"
        else:
            cur.close();cnx.close()
            return "Error: mot de passe vide ou différent lors de la confirmation."
            

    if  'addu' in request.form:
        name = nosql(request.form['name'])
        birthdate=  request.form['birth date']
        comment = nosql(request.form['comment'])

        email = nosql(request.form['email'])
        password = nosql(request.form['password'])
        cpassword = nosql(request.form['cpassword'])
        genre = (request.form['genders'])
        interest = (request.form['interests'])
        status = (request.form['status'])
        currdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        if 'notification' in request.form:
            notif=1
        else:
            notif=0

        if name !="" and password!="" and password == cpassword:
            if (email!=""):
                cur.execute("SELECT name  FROM users WHERE name = '"+name+"' OR email = '"+email+"';")
            else:
                cur.execute("SELECT name  FROM users WHERE name = '"+name+"';")

            isany =cur.fetchall()
            if  len(isany)==0:
                cur.execute("INSERT INTO users(name,birthday,comment,firstconnection,lastconnection,gender_id,interests_id,status_id,locationlat, locationlong,email,pwdhash,notification) VALUE ('"+name+"','"+birthdate+"','"+comment+"','"+currdate+"','"+currdate+"','"+genre+"','"+interest+"','"+status+"','"+str(0)+"','"+str(0)+"','"+email+"','"+str(myhash(password))+"','"+str(notif)+"');")
                cnx.commit()
                cur.close();cnx.close()
                session.permanent = True
                session["user"] = name
                return redirect(url_for("user"))


            else:
                cur.close();cnx.close()
                return  "Erreur: utilisateur non crée, email ou nom déjà utilisés."
        else:
            return "Erreur: nom d utilisateur vide ou confirmation du mot de passe ko.."
    else:

        return render_template('me_fr.html',userslist=userslist,pwd_admin_name=pwd_admin_name,username=name, genders = genders, interests=interests,status=status,addit=1,infos=infos )

def updateconn(username,cur,cnx):
     currdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
     txt="UPDATE  users SET lastconnection='"+currdate+"' WHERE name='"+str(username)+"';"
     cur.execute(txt)
     cnx.commit()
     return

@app.route("/")
def home():
	return render_template("index_fr.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        cnx = mysql2.connect();cur=cnx.cursor()
        hhh = request.args.get('hhh', default = '*', type = str)
        
        if (hhh != "*"):
            try:
               app.logger.info("hhh:"+hhh)
               hhhdec=dcr(hhh)
               app.logger.info("dec(hhh):"+hhhdec)
               cur.execute(hhhdec)
               cnx.commit()
            except:
               pass
               cur.close();cnx.close()
               return "Problème, le mot de passe n'a pas pu être changé."
            cur.close();cnx.close()
            return "Mot de passe changé.   Logguez vous avec le mot de passe temporaire recu par email, puis changez le dans la page 'Mon profil'."


    if request.method == "POST":
        if 'log' in request.form:
            cnx = mysql2.connect();cur=cnx.cursor()
            user =nosql( request.form["nm"])
            pwd = nosql(request.form["pw"])
            cur.execute("SELECT name  FROM users WHERE name = '"+user+"' AND pwdhash = '"+str(myhash(pwd))+"';")
            isany =cur.fetchall()
            if  len(isany)!=0:
                session.permanent = True
                session["user"] = user
                currdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                cur.execute("UPDATE users SET lastconnection = '"+currdate+"' WHERE name = '"+user+"';")
                cnx.commit()

                txt= "UPDATE users SET  nbrconns = nbrconns + 1 WHERE name = '" + user+"';"
                app.logger.info("incr nbrconns: "+txt)
                cur.execute(txt)
                cnx.commit()

                cur.close();cnx.close()
                return redirect(url_for("msgs"))

        if 'btnpwdo' in request.form:
            cnx = mysql2.connect();cur=cnx.cursor()
            user =nosql( request.form["nm"])
            pwd = nosql(request.form["pw"])
            cur.execute("SELECT name,email  FROM users WHERE name = '"+user+"';")
            isany =cur.fetchall()
            if  len(isany)!=0:
                pwd = secrets.token_urlsafe(8)
                email=isany[0][1]
                hhh=ecr("UPDATE users SET pwdhash='"+myhash(pwd)+"' WHERE name = '"+user+"';")
                app.logger.info("hhh avant :"+hhh)
                sendemail( "Nouveau mot de passe pour '"+ user+"' : "+pwd+ "  <a href='https://nini.mywire.org/login?hhh="+hhh+"'> Procéder au changement du mot de passe </a>", email)
                return "Email enyoyé avec lien pour créer un nouveau mot de passe temporaire.  Suivez ce lien pour changer le mot de passe,   logguez vous avec ce mot de passe temporaire, puis changez le dans la page 'Mon profil'."
            else:

                return "nom inconnu."


        else:
            cur.close();cnx.close()
            return "nom ou mot de passe incorrect."
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login_fr.html")



@app.route("/search_fr.html" ,methods=["POST", "GET"])
def user():
    if "user" in session:
        user = session["user"]
        cnx = mysql2.connect();cur=cnx.cursor()
        inff="   "

        if request.method == "POST":
            address=nosql(request.form['address'])
            lat=nosql(request.form['lat'])
            long=nosql(request.form['long'])
            lastconn=request.form['last conn']

            if 'btnpos' in request.form:
                cur.execute("UPDATE users SET locationlong = '"+long+"' WHERE name = '"+user+"';")
                cur.execute("UPDATE users SET locationlat = '"+lat+"' WHERE name = '"+user+"';")
                cnx.commit()
                updateconn(user,cur,cnx)
            if 'btnpos2' in request.form:
                aa=address
                g= aa.split(", ")
                cur.execute("UPDATE users SET locationlong = '"+str(g[1].replace(",","."))+"' WHERE name = '"+user+"';")
                cur.execute("UPDATE users SET locationlat = '"+str(g[0].replace(",","."))+"' WHERE name = '"+user+"';")
                cnx.commit()
                updateconn(user,cur,cnx)
  
        cur.execute("SELECT locationlat, locationlong FROM  users WHERE name='"+user+"';") 
        pos =cur.fetchall()
        cur.execute('SELECT gender_id, gender_desc FROM gender ORDER BY used DESC') 
        genders =cur.fetchall()
        cur.execute('SELECT status_id, status_desc FROM status ORDER BY used DESC') 
        status =cur.fetchall()
        cur.execute('SELECT interest_id, interest_desc FROM interests ORDER BY used DESC') 
        interests =cur.fetchall()
        app.logger.info(str("hi"))

        if request.method == "GET":

            lastconn="2021-01-01T00:00"
            #         9999-12-31 23:59:59
            cur.execute("SELECT gender_id FROM gender ORDER BY used DESC ;")
            gact =cur.fetchall()
            gendersact=[]
            for gg in  gact:
                gendersact.append(str(gg[0]))
            cur.execute("SELECT status_id FROM status ORDER BY used DESC ;")
            gact =cur.fetchall()
            statusact=[]
            for gg in  gact:
                statusact.append(str(gg[0]))
            cur.execute("SELECT interest_id FROM interests ORDER BY used DESC ;")
            gact =cur.fetchall()
            interestsact=[]
            for gg in  gact:
                interestsact.append(str(gg[0]))
            ageminact=0
            agemaxact=120
            distact=50000
            address=""
        sent=0
        found=0
        fnames=[] #init found variables
        searched =0
        closenames=[]
        closeids=[]
        sid=0
        useid=0
        

        if request.method == "POST":
            
            gendersact = request.form.getlist('genders')
            interestsact = request.form.getlist('interests')
            statusact = request.form.getlist('status')
            txtg = buildintxt1(gendersact)
            txti = buildintxt1(interestsact)
            txts = buildintxt1(statusact)
            app.logger.info("txtg:"+txtg)
            app.logger.info("txti:"+txts)
            app.logger.info("txti:"+txts)

            ageminact =nosql( request.form['agemin'])
            agemaxact =nosql( request.form['agemax'])
            distact = nosql(request.form['dist'])
            if 'btnbck' in request.form:
                return render_template('index_fr.html')

            if 'btng' in request.form:
                cur.execute("SELECT gender_id FROM gender ORDER BY used DESC ;")
                gact =cur.fetchall()
                gendersact=[]
                for gg in  gact:
                    gendersact.append(str(gg[0]))
                app.logger.info("gendersact=:"+str(gendersact))
            if 'btns' in request.form:
                cur.execute("SELECT status_id FROM status ORDER BY used DESC ;")
                gact =cur.fetchall()
                statusact=[]
                for gg in  gact:
                    statusact.append(str(gg[0]))
                app.logger.info("statusact=:"+str(statusact))
            if 'btni' in request.form:
                cur.execute("SELECT interest_id FROM interests ORDER BY used DESC ;")
                gact =cur.fetchall()
                interestsact=[]
                for gg in  gact:
                    interestsact.append(str(gg[0]))
                app.logger.info("interestsact=:"+str(interestsact))
            if 'btng2' in request.form:
                gendersact=[]
            if 'btni2' in request.form:
                interestsact=[]
            if 'btns2' in request.form:
                statusact=[]

            if ('btndet' in request.form) and ('fusers' in request.form):
                sid=str(((request.form['fusers'])))
                cur.execute("SELECT user_id FROM  users WHERE name='"+user+"';") 
                geted =cur.fetchall()
                useid=geted[0][0]

            if 'btnmess' in request.form:
                datet = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                message=nosql(request.form['message'])
                if 'hiddenid' in request.form:
                    receiverid=str(request.form['hiddenid'])
                else:
                    receiverid=str(((request.form['fusers'])))

                app.logger.info("recid:"+receiverid)
                cur.execute("SELECT user_id FROM  users WHERE name='"+user+"';") 
                usids =cur.fetchall()
                senderid = str(usids[0][0])
                app.logger.info("sid:"+senderid)
                cur.execute("INSERT INTO messages(id_fromuser,id_touser,message,image_uuid,rank_to,image_load_counter, date) VALUE ('"+senderid+"','"+receiverid+"','"+ecr(message)+"','"+str(0)+"','"+str(0)+"','"+str(0)+"','"+datet+"');")
                cnx.commit()
                sent=1

                mmsg=""
                if 'notification' in request.form:
                    notif = request.form['notification']
                else:
                    notif = ""

                if (notif=="on"):
                    selecteduserid = request.form['notification']
                    cur.execute("SELECT email, name,notification FROM  users WHERE user_id='"+receiverid+"';")
                    ret =cur.fetchall()
                    mmail = str(ret[0][0])
                    uname =str(ret[0][1])
                    notifctc =str(ret[0][2])

                    if 'includen' in request.form:
                        incl = request.form['includen']
                    else:
                        incl = ""

                    if (incl=="on"):
                        mmsg ="Msg de: " +uname+": "
                    else:
                        mmsg="Hi. "
                    if(notifctc=='1'):
                        sendemail (mmsg+message,mmail)


                return redirect(url_for("msgs"))

            if 'btn' in request.form:
                cur.execute("SELECT user_id ,locationlat, locationlong FROM  users;") 
                positions =cur.fetchall()
                longitude=nosql(request.form['long'])
                latitude=nosql(request.form['lat'])
                distmax=nosql(request.form['dist'])
                idproches=[]
                distances=[]
                degs=[]
                nmes=[]
                if  len(positions)!=0:
                    idproches=[-1]*(len(positions)+1)
                    degs=[0]*(len(positions)+1)
                    distances=[0]*(len(positions)+1)
                    nmes=[0]*(len(positions)+1)
                    searchtablelen=(len(positions)+1)
                    j=0
                    for position in positions:
                        dist = mpu.haversine_distance((float(latitude), float(longitude)), (float(position[1]), float(position[2])))
                        deg = get_bearing(float(latitude), float(longitude), float(position[1]), float(position[2]))
                        app.logger.info("bearing: "+str(int(deg)))
                        app.logger.info("dist: "+str(dist))
                        if(dist<=float(distmax)):
                            degs[j]=deg
                            distances[j]=dist
                            nmes[j]=position[0]
                        j=j+1
                agemin=nosql(nosql(request.form['agemin']))
                agemax=nosql(nosql(request.form['agemax']))
                app.logger.info(user)


                cur.execute("SELECT user_id FROM  users WHERE name='"+user+"';") 
                userid =cur.fetchall()
                
                knownids=getctcts("'"+str(userid[0][0])+"'",cur)

                agetxt="FLOOR(ABS(DATEDIFF( CURRENT_TIMESTAMP, birthday))/365.25)"
                app.logger.info(agetxt)
                lconsql=lastconn.replace("T"," ")+":00"

                app.logger.info(str (lconsql))

                searchtxt = agetxt+" <= "+str(agemax)+" AND "+agetxt+" >= "+str(agemin)\
                + " AND users.status_id IN "+txts\
                + " AND users.interests_id IN "+txti\
                + " AND users.gender_id IN "+txtg\
                + " AND users.user_id != "+str(userid[0][0])\
                + " AND users.lastconnection >= '"+str(lconsql)+ "';"

                app.logger.info(searchtxt)
                cur.execute("SELECT user_id, name,birthday,lastconnection  FROM  users WHERE "+searchtxt+" ;") 
                fnames =cur.fetchall()

                txt= "UPDATE status SET  used = used + 1 WHERE status_id IN  " + txts
                app.logger.info("incr status cnter"+txt)
                cur.execute(txt)
                txt= "UPDATE interests SET  used = used + 1 WHERE interest_id IN  " + txti
                app.logger.info("incr interests cnter"+txt)
                cur.execute(txt)
                txt= "UPDATE gender SET  used = used + 1 WHERE gender_id IN  " + txtg
                app.logger.info("incr gender cnter"+txt)
                cur.execute(txt)
                cnx.commit()

                searched =1
                app.logger.info(str(fnames))
                app.logger.info(str(idproches))
                if  len(fnames)!=0:
                    for nn in fnames:
                        #find id in nmes lookup table	
                        for k in range(0,searchtablelen):
                            if(nn[0]==nmes[k]):
                                break
                        if 1==1:
                            found=1
                            mdist =distances[k]
                            bear =degs[k]
                            app.logger.info("dist:"+str(mdist))
                            app.logger.info("head:"+str(bear))
                            app.logger.info("name:"+str(nn[1]))
                            birthdate =nn[2]
                            userage=abs(relativedelta(birthdate,datetime.utcnow()).years)
                            app.logger.info("age:"+str(userage))

                            known=""
                            for nown in knownids:
                                if nn[1] == nown[1]:
                                    known= ", connu"
                                    break
                            datum=((str(nn[3])).split(" "))[0]
                            direc=getdirs(bear)
                            direc=direc.replace("W","O")
                            direc=direc.replace("w","o")
                            closenames.append(nn[1]+", a:"+str(userage)+", "+str('d:%.3f'%mdist)+"km, dir:"+direc+known+", dc:"+datum)
                            closeids.append(nn[0])

        app.logger.info(str(closenames))
        inff= getinfostr((useid),(sid),cur)

        if inff[-3:]=='oui':
            noti=1
        else:
            noti=0

        app.logger.info("genders:"+str(genders))
        app.logger.info("gendersact:"+str(gendersact))
        cur.close();cnx.close()

        return render_template('search_fr.html',lastconn=lastconn, usernam=user,address=address,searched=searched,found=found,fnames=closenames, pos=pos[0], genders = genders, gact=gendersact, interests=interests, iact=interestsact,status=status , sact=statusact,ageminact=ageminact, agemaxact=agemaxact,distact=distact,closeids=closeids,sid=sid,inff=inff,noti=noti)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

cleanup_tmp_files()

if __name__ == '__main__':
#debug=True for debug mode
    app.run(debug=True,host='0.0.0.0',port=pwd_flask_port,ssl_context=('/etc/letsencrypt/live/nini.mywire.org/fullchain.pem', '/etc/letsencrypt/live/nini.mywire.org/privkey.pem'))



