from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask import Flask, render_template, flash, request, url_for, redirect, session
from secretsharing import SecretSharer
from passlib.hash import hex_sha512
from math import floor
import exrex
import pickle
import os
import re

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class RegistrationForm(Form):
    username = TextField('Username:', validators=[validators.required()])
    email1 = TextField('Email:', validators=[validators.required(), validators.Length(min=10, max=256)])
    email2 = TextField('Email:', validators=[validators.required(), validators.Length(min=10, max=256)])
    email3 = TextField('Email:', validators=[validators.required(), validators.Length(min=10, max=256)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=12, max=32)])

class LoginForm(Form):
    username = TextField('Username:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required()])

class LoginWithFragmentsForm(Form):
    username = TextField('Username:', validators=[validators.required()])
    fragment1 = TextField('Fragment 1:')
    fragment2 = TextField('Fragment 2:')
    fragment3 = TextField('Fragment 3:')

class ChangePasswordForm(Form):
    username = TextField('Username:', validators=[validators.required()])
    oldpassword = TextField('Old Password:', validators=[validators.required()])
    newpassword = TextField('New Password:', validators=[validators.required()])

class ChangePasswordWithFragmentsForm(Form):
    username = TextField('Username:', validators=[validators.required()])
    fragment1 = TextField('Fragment 1:')
    fragment2 = TextField('Fragment 2:')
    fragment3 = TextField('Fragment 3:')
    password = TextField('Password', validators=[validators.required(), validators.Length(min=12, max=32)])

class RecoveryForm(Form):
    username = TextField('Username:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

def get_users():
    if os.path.isfile('users.pk'):
        users = pickle.load(open('users.pk', 'rb'))
        return users
    return {}

@app.route("/registration", methods=['GET', 'POST'])
def registration():
    EMAIL_ADDRESSES_NUMBER = 3
    form = RegistrationForm(request.form)
    loginForm = LoginForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        emails = set([request.form['email1'], request.form['email2'], request.form['email3']])

        mail_pattern = re.compile("[^@ ]+@[^@ ]+\.[^@ ]+")

        addresses_format_validity = True
        addresses_length_validity = True

        for email in emails:
            print(email)
            if not mail_pattern.match(email):
                flash("Error: The string ' + email + ' is not a valid mail address.")
                addresses_format_validity = False
            if len(email) < 10 or len(email) > 256:
                addresses_length_validity = False

        users = get_users()

        if not form.validate():
            if not addresses_length_validity or len(request.form['password']) < 12 or len(request.form['password']) > 32:
                if not addresses_length_validity:
                    flash("Error: The e_mail addresses should have a number of characters between 10 and 256.")
                else:
                    flash("Error: The password should have a number of character between 12 and 32.")
            else:
                flash("Error: All the form fields are required.")
        else:
            if username in users or len(emails) != EMAIL_ADDRESSES_NUMBER:
                if username in users:
                    flash("Error: The username is already registered.")
                else:
                    flash("Error: The e-mail addresses should be different.")
            else:
                if form.validate() and addresses_format_validity and addresses_length_validity:
                    credentials = []
                    hashed_password = hex_sha512.hash(password)
                    credentials.append(list(emails))
                    credentials.append(hashed_password)
                    credentials.append('')
                    users[username] = credentials
                    pickle.dump(users, open('users.pk', 'wb'))
                    print(users)
                    return render_template('index.html')
    return render_template('registration.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        if form.validate():
            users = get_users()
            username = request.form['username']
            if username in users:
                if users[username][1] != '':
                    user_password = hex_sha512.hash(request.form['password'])
                    if user_password != users[username][1]:
                        flash("Error: Invalid Credentials. Please try again.")
                    else:
                        session['logged_in'] = True
                        credentials = users[username]
                        if credentials[2] != '':
                            credentials[2] = ''
                            users[username] = credentials
                            pickle.dump(users, open('users.pk', 'wb'))
                else:
                    flash("Error: Login not allowed, please login with the fragments")
            else:
                flash("Error: The username is not registered in the system.")
        else:
            if request.form['username'] == '':
                flash("Error: You didn't insert your username!")
            if request.form['password'] == '':
                flash("Error: You didn't insert your password!")

    return render_template('login.html', form=form)

@app.route("/login_with_fragments", methods=['GET', 'POST'])
def login_with_fragments():
    form = LoginWithFragmentsForm(request.form)

    if request.method == 'POST':
        users = get_users()
        username = request.form['username']
        if username in users:
            fragments = []
            for i in range(1, 4):
                if request.form['fragment'+str(i)] != '':
                    fragments.append(request.form['fragment'+str(i)])
            try:
                user_password = SecretSharer.recover_secret(fragments)

                if users[username][2] != '':
                    if user_password != users[username][2]:
                        flash("Error: Invalid Fragments. Please try again.")
                    else:
                        session['logged_in'] = True
                        credentials = users[username]
                        credentials[1] = ''
                        users[username] = credentials
                        pickle.dump(users, open('users.pk', 'wb'))
                else:
                    flash("Error: You are not allowed to use this login.")
            except:
                flash("Error: Why are you trying to bruteforce?")
        else:
            flash("Error: Your are not registered in the system!")

    return render_template('login_with_fragments.html', form=form)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('logout.html')

@app.route("/change_password_with_fragments", methods=['GET', 'POST'])
def change_password_by_fragments():
    form = ChangePasswordWithFragmentsForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            if len(request.form['password']) < 12 or len(request.form['password']) > 32:
                flash("Error: The password length should have between 12 and 32 characters")
            else:
                flash("Error: The username is mandatory")
        else:
            users = get_users()
            username = request.form['username']
            if username in users:
                fragments = []
                for i in range(1, 4):
                    if request.form['fragment'+str(i)] != '':
                        fragments.append(request.form['fragment'+str(i)])

                try:
                    user_password = SecretSharer.recover_secret(fragments)

                    if user_password != users[username][2]:
                        flash("Error: Invalid Fragments. Please try again.")
                    else:
                        new_password = hex_sha512.hash(request.form['password'])
                        credentials = users[username]
                        credentials[1] = new_password
                        credentials[2] = ''
                        users[username] = credentials
                        pickle.dump(users, open('users.pk', 'wb'))
                        return render_template('index.html')
                except:
                    flash("Error: Why are you trying to bruteforce?")

            else:
                flash("Error: The username is not registered in the system.")

    return render_template('change_password_with_fragments.html', form=form)

@app.route("/change_password", methods=['GET','POST'])
def change_password():
    form = ChangePasswordForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            if len(request.form['newpassword']) < 12 or len(request.form['newpassword']) > 32:
                flash("Error: The password length should have between 12 and 32 characters")
            else:
                flash("Error: The username is mandatory")
        else:
            users = get_users()
            username = request.form['username']
            if username in users:
                credentials = users[username]
                if credentials[1] != '':
                    user_password = hex_sha512.hash(request.form['oldpassword'])
                    if user_password != users[username][1]:
                        flash('Error: Invalid Credentials. Please try again..')
                    else:
                        new_password = hex_sha512.hash(request.form['newpassword'])
                        credentials = users[username]
                        credentials[1] = new_password
                        users[username] = credentials
                        pickle.dump(users, open('users.pk', 'wb'))
                        return render_template('index.html')
                else:
                    flash("Error: You can login only with fragments, please change your password with fragments")
            else:
                flash("Error: The username is not registered in the system.")

    return render_template('change_password.html', form=form)

@app.route("/recovery", methods=['GET','POST'])
def recovery():
    if request.method == 'POST':
        users = get_users()
        username = request.form['username']
        if username in users:
            user_credentials = users[username]
            RANDOM_STRING_LENGTH = 128
            mail_addresses_number = len(user_credentials[0])
            random_string = get_random_string(RANDOM_STRING_LENGTH)
            hashed_string = hex_sha512.hash(random_string)
            fragments = SecretSharer.split_secret(hashed_string, floor(mail_addresses_number/2) + 1, mail_addresses_number)

            user_credentials[2] = hashed_string
            pickle.dump(users, open('users.pk', 'wb'))
            print(users)

            for i in range(0, len(fragments)):
                print('Sending the fragment {} to the mail address {}'.format(fragments[i], users[username][0][i]))
                send_email(fragments[i], 'Password Recovery: Fragment', users[username][0][i])

            return render_template('index.html')

        else:
            flash("Error: The username is not registered in the system")

    return render_template('recovery.html')

def get_random_string(string_length):
    return exrex.getone('[a-zA-Z0-9$&+,:;=?@#|\'<>.^*()%!-]{' + str(string_length) + '}', 1)

def send_email(body, subject, destination):
    SMTPserver = 'smtp.gmail.com'
    sender = 'server_mail'
    username = 'server_name'
    password = 'server_pw'

    # Typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'

    content = body

    import sys
    from smtplib import SMTP_SSL as SMTP # This invokes the secure SMTP protocol (port 465, uses SSL)
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
        print('Mail failed; %s' % str(exc))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
