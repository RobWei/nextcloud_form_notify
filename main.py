import nextcloud_forms
import json
import sqlite3
import sys
from datetime import datetime
from dateutil import tz
import smtplib, ssl
from email.mime.text import MIMEText
from email.header    import Header


exec(open("{}/config.py".format(sys.path[0])).read())

def sendMail(mail_facts):
    with smtplib.SMTP(global_params["smtp_server_host"]) as server:
        server.starttls()
        server.login(global_params["smtp_server_user"], global_params["smtp_server_password"])
        msg = MIMEText(message.format(**mail_facts), 'plain', 'utf-8')
        msg['Subject'] = Header(global_params["mail_betreff"].format(**mail_facts), 'utf-8')
        msg['From'] = global_params["mail_from"]
        msg['To'] = global_params["mail_from"]

        msg_eltern = MIMEText(message_eltern.format(**mail_facts), 'plain', 'utf-8')
        msg_eltern['Subject'] = Header(global_params["mail_betreff_eltern"].format(**mail_facts), 'utf-8')
        msg_eltern['From'] = "Sommerlager <sommerlager@dpsg-ostbevern.de>" 
        msg_eltern['To'] = mail_facts["email"]
        if global_params["dry_run"]:
            print(msg['From'],msg['To'], msg.as_string())
            print(msg_eltern['From'],msg_eltern['To'], msg_eltern.as_string())
        else:
            server.sendmail(msg['From'],msg['To'], msg.as_string())
            server.sendmail(msg_eltern['From'],msg_eltern['To'], msg_eltern.as_string())


form = nextcloud_forms.nextcloud_form(nextcloud_url=global_params["nextcloud_url"], nextcloud_user=global_params["nextcloud_user"], nextcloud_password=global_params["nextcloud_password"])

if global_params["form_id"] not in form.get_owned_forms_hash_list():
    print("Could not find Form with hash: {}".format(global_params["form_id"]))
    exit()

connection = sqlite3.connect("{}/{}.db".format(sys.path[0],global_params["simple_ferienlager_name"]))
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS anmeldung (vorname TEXT, nachname TEXT, uid TEXT)")

for submission in form.get_submissions(global_params["form_id"])["json"]["ocs"]["data"]["submissions"]:
    register_facts = {}
    register_facts["uid"] = submission["userId"]
    register_facts["timestamp"] = datetime.utcfromtimestamp(int(submission['timestamp'])).astimezone(tz.gettz('Europe/Berlin')).strftime('%d.%m.%Y %H:%M:%S')
    for answer in submission["answers"]:
        if answer["questionId"] == global_params["form_field_kind_vorname_id"]:
            register_facts["vorname"] = answer["text"]
        elif answer["questionId"] == global_params["form_field_kind_nachname_id"]:
            register_facts["nachname"] = answer["text"]
        elif answer["questionId"] == global_params["form_field_kind_geburtstag_id"]:
            register_facts["geburtstag"] = answer["text"]
        elif answer["questionId"] == global_params["form_field_kind_gruppename_id"]:
            register_facts["gruppenname"] = answer["text"]
        elif answer["questionId"] == global_params["form_field_kind_notiz_id"]:
            register_facts["notiz"] = answer["text"]
        elif answer["questionId"] == global_params["form_field_eltern_email_id"]:
            register_facts["email"] = answer["text"]
    if (["vorname", "nachname", "geburtstag", "gruppenname", "notiz", "email", "timestamp", "uid"] - register_facts.keys()):
        print("Fehlende Parameter: {}".format(', '.join(["vorname", "nachname", "geburtstag", "gruppenname", "notiz", "email", "timestamp", "uid"] - register_facts.keys())))
    else:
        rows = cursor.execute("SELECT * FROM anmeldung WHERE uid = ?",(register_facts["uid"],),).fetchall()
        if(len(rows) == 0):
            print("Anmeldung nicht in Anmeldetabelle gefunden. Erstelle...")
            cursor.execute("INSERT INTO anmeldung VALUES (?, ?, ?)",(register_facts["vorname"], register_facts["nachname"], register_facts["uid"],))
            connection.commit()
            rows = cursor.execute("SELECT * FROM anmeldung WHERE uid = ?",(register_facts["uid"],),).fetchall()
            if(len(rows) == 1):
                print("Anmeldung erstellt! Sende E-Mails..")
                sendMail(register_facts)
            else:
                print("Anmeldung konnte nicht in Datenbank eingetragen werden. Sende KEINE E-Mail!")
