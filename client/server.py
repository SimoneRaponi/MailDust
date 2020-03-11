from passlib.hash import hex_sha512
import csv
import exrex
import sys

users_database = {}

def recovery_password(username):
    if username in users_database:

        random_string_length = 128

        mail_addresses_number = len(users_database[username][0])

        random_string = get_random_string(random_string_length*mail_addresses_number)
        fragments = []

        password = '0'*512

        for i in range(0, int(len(random_string)/random_string_length)):
            fragment = hex_sha512.hash(random_string[i*random_string_length:i*random_string_length + random_string_length])

            fragments.append(fragment)
            fragment_size = len(fragment) * 4
            binary = (bin(int(fragment, 16))[2:]).zfill(fragment_size)

            password = xor(password, binary)

        password = str(hex(int(password, 2)))[2:]

        users_database[username][1] = hex_sha512.hash(password)

        for i in range(0, len(fragments)):
            print('Sending the fragment {} to the mail address {}'.format(fragments[i], users_database[username][0][i]))
            send_email(fragments[i], 'Password Recovery: Fragment', users_database[username][0][i])

        print(users_database)

    else:
        print("The user is not registered in the system")

def xor(x, y):
    return '{1:0{0}b}'.format(len(x), int(x, 2) ^ int(y, 2))

def get_random_string(string_length):
    return exrex.getone('[a-zA-Z0-9$&+,:;=?@#|\'<>.^*()%!-]{' + str(string_length) + '}', 1)

def registration(username, password, *mail_addresses):
    if username not in users_database:
        credentials = []
        hashed_password = hex_sha512.hash(password)
        credentials.append(mail_addresses)
        credentials.append(hashed_password)
        users_database[username] = credentials
    else:
        print('The username is already registered in the system')

def login(username, password):
    if username in users_database:
        hashed_password, _ = hex_sha512(password)
        if hashed_password == users_database[username][1]:
            print('Logged in')
        else:
            print('Wrong password')
    else:
        print('The username is not registered in the system')

def send_email(body, subject, destination):
    SMTPserver = 'smtp.gmail.com'
    sender = 'server_mail'

    #username = "fernandello.capocchia@gmail.com"
    #password = "ferndCapo99"

    username = 'server_name'
    password = 'server_pw'

    # typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'

    content = """\
    %s
    """ % body

    import sys

    from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)

    from email.mime.text import MIMEText

    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = sender

        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(username, password)

        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.quit()

    except Exception as exc:
        sys.exit("mail failed; %s" % str(exc))
