from email.mime.text import MIMEText
from subprocess import Popen, PIPE

msg = MIMEText("Here is the body of my message")
msg["From"] = "iotn@iotn.com"
msg["To"] = "ompatil94@gmail.com"
msg["Subject"] = "This is the subject."
p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
p.communicate(msg.as_string())
print "Done"