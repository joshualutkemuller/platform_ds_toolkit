from email.message import EmailMessage

def send_email(subj, body, to, sender): m=EmailMessage(); m['Subject']=subj; m.set_content(body); return m
