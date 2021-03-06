import email
import email.mime
import email.mime.text
import logging
import smtplib

from config import config

class Message(object):
	def __init__(self, book_id, from_addr, from_name, text):
		self.from_addr = from_addr
		self.from_name = from_name
		self.text = text
		self.book_id = book_id

	def __str__(self):
		return (
			"Message for book {book_id} "
			"from {from_name} <{from_addr}>: {text}".format(
				book_id=self.book_id,
				from_name=self.from_name,
				from_addr=self.from_addr,
				text=self.text
			)
		)

	def send(self):
		try:
			msg = email.mime.text.MIMEText(str(self))
			msg["From"] = email.utils.formataddr((
				config.bug_report.from_name, 
				config.bug_report.from_addr
			))
			msg["To"] = email.utils.formataddr((
				config.bug_report.to_name, 
				config.bug_report.to_addr
			))
			msg["Subject"] = "[dancebooks-bibtex] Error reports".format(id=id)
			recipients = [config.bug_report.to_addr]

			smtp = smtplib.SMTP(config.smtp.host, config.smtp.port)
			if config.smtp.user and config.smtp.password:
				smtp.login(config.smtp.user, config.smtp.password)
			smtp.sendmail(config.smtp.email, recipients, msg.as_string())
	
		except Exception as ex:
			logging.exception("Messenger: exception occured. {ex}".format(
				ex=ex
			))
