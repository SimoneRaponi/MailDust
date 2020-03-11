

import imaplib
import email
import re

def read_email_from_hotmail():
    email_address = 'email1'
    pwd = 'pw1'
    imap_server = 'imap-mail.outlook.com'

    patternSubject = re.compile("^Password Recovery: Fragment")

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, pwd)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id, first_email_id, -1):
            typ, data = mail.fetch(str(i), '(RFC822)')

            email_content = data[0][1]
            msg = email.message_from_bytes(email_content)

	    '''
            Add any control for the message source
            '''

            if patternSubject.match(msg["Subject"]):
                return msg.get_payload(decode=True).decode('utf-8').lstrip()

    except Exception as e:
        print(str(e))

def read_email_from_yahoo():
    email_address = 'email2'
    pwd = 'pw2'
    imap_server = 'imap.mail.yahoo.com'

    patternSubject = re.compile("^Password Recovery: Fragment")

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, pwd)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id, first_email_id, -1):
            typ, data = mail.fetch(str(i), '(RFC822)')

            email_content = data[0][1]
            msg = email.message_from_bytes(email_content)

            '''
            Add any control for the message source
            '''
            if patternSubject.match(msg["Subject"]):
                return msg.get_payload(decode=True).decode('utf-8').lstrip()

    except Exception as e:
        print(str(e))


def read_email_from_gmail():

    email_address = 'email3'
    pwd = 'pw3'
    imap_server = 'imap.gmail.com'

    patternSubject = re.compile("^Password Recovery: Fragment")

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, pwd)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id, first_email_id, -1):
            typ, data = mail.fetch(str(i), '(RFC822)')

            email_content = data[0][1]
            msg = email.message_from_bytes(email_content)

            '''
            Add any control for the message source
            '''
            if patternSubject.match(msg["Subject"]):
                return msg.get_payload(decode=True).decode('utf-8').lstrip()

    except Exception as e:
        print(str(e))

    return
