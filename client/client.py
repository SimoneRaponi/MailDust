import email
import imaplib
import re
import csv
from passlib.hash import hex_sha512


emails = ['email1', 'email2', 'email3']

def get_fragments():

    imap_mapping = read_mapping()
    fragments = []

    for recovery_mail in emails:
        imap_server = imap_mapping[re.findall('@[0-9a-z]+', recovery_mail)[0][1:]]
        password = input("Please, write the password for the account " + recovery_mail + ': ')
        fragments.append(read_email(recovery_mail, password, imap_server))

    return fragments
'''
def generate_password(fragments):

    password = '0' * 512

    for fragment in fragments:
        hash = hex_sha512.hash(fragment)
        hash_size = len(hash) * 4
        print(fragment)
        binary = bin(int(fragment, 16))[2:].zfill(hash_size)
        password = xor(password, binary)

    return str(hex(int(password, 2)))[2:]


def xor(x, y):
    return '{1:0{0}b}'.format(len(x), int(x, 2) ^ int(y, 2))
'''

def read_email(email_address, pwd, imap_server):
    patternSubject = re.compile("^Password Recovery: Fragment")
    fragment = ''

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
            fragment = email.message_from_bytes(email_content)

            # emailDate = msg["Date"]
            # emailSubject = msg["Subject"]
            # emailFrom = msg["From"]

            '''
            Think about some controls related to the source of the message
            '''
            if patternSubject.match(fragment["Subject"]):

                return re.findall('^[0-9]+-[0-9a-f]+', fragment.get_payload(decode=True).decode('utf-8'))[0]

    except Exception as e:
        print(str(e))

    return fragment

def read_mapping():
    mappingDict = dict()
    with open('./csv/mapping.csv', 'r') as inputFile:
        reader = csv.reader(inputFile)
        for row in reader:
            mappingDict[row[0]] = row[1]
    return mappingDict
