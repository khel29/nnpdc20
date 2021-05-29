
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passwords import *
import smtplib

def sendemail(messagetosend,email_receiver):
#  try:
    if email_receiver=="":
        return

    email_address =  pwd_email_address

    email_password = pwd_email

    # on cree un e-mail
    message = MIMEMultipart("alternative")
    # on ajoute un sujet
    message["Subject"] = "NNPDC"
    # un emetteur
    message["From"] = email_address
    # un destinataire
    message["To"] = email_receiver
    # on cree un texte et sa version HTML
    texte = messagetosend
    html = '<html> <body><h1>'+messagetosend+'</h1> </body> </html> '
    # on cree deux elements MIMEText
    texte_mime = MIMEText(texte, 'plain')
    html_mime =MIMEText(html, 'html')
    # on attache ces deux elements
    message.attach(texte_mime)
    message.attach(html_mime)
    # on cree la connexion
    #context = ssl.create_default_context()
    with smtplib.SMTP_SSL(pwd_mail_server, pwd_smtp_port) as server:
      # connexion au compte
      server.connect()
      server.set_debuglevel(1)
      server.ehlo
      server.login(pwd_mail_user, email_password)
      # envoi du mail
      server.sendmail(email_address, email_receiver, message.as_string())

      server.quit()


 # except:
    pass

if __name__ == "__main__":
#    sendemail("Hi", "nico.guillou@gmail.com")
    sendemail("Hi", "nnpdc@nini.mywire.org")


