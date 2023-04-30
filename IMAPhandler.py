import os
from imap_tools import MailBox, MailMessage
import datetime


class IMAPhandler:
    def __init__(self, IMAP_server, IMAP_login, IMAP_password, logger):
        self.server = IMAP_server
        self.login = IMAP_login
        self.password = IMAP_password
        self.logger = logger
        self.email_number = 0
        self.logger.log("IMAP HANDLER: IMAP handler instance successfully invoked!")

    def retrieve_emails(self, save_locally, misp_handler):
        cwd = os.getcwd() + "/downloads/"
        self.logger.log("IMAP HANDLER: Retrieving emails!")

        with MailBox(self.server).login(self.login, self.password, 'INBOX') as mailbox:
            for message in mailbox.fetch():
                self.email_number = self.email_number + 1
                self.logger.log("IMAP HANDLER: Fetching message #" + str(self.email_number))
                attachments = message.attachments

                # Save the e-mail into a unique folder if the option is allowed
                if save_locally:
                    temp = str(datetime.datetime.now().today()).replace(":","_")
                    current_path = os.path.join(
                        cwd + temp + "#" + str(self.email_number))
                    os.mkdir(current_path)
                    self.logger.log("IMAP HANDLER: Saved email #" + str(self.email_number) + " locally.")

                if attachments:
                    self.logger.log("IMAP HANDLER: This message does have " + str(len(attachments)) + " attachments.")
                    attachment_counter = 0

                    for att in message.attachments:
                        attachment_counter = attachment_counter + 1
                        filename = att.filename
                        self.logger.log("IMAP HANDLER: Attachment #" + str(attachment_counter) + " filename is: " + filename)

                        # Outlook apparently has a bug where the attached .eml message has no filename.
                        # In that case, a filename will be generated from email number and attachment number to save it.
                        if att.filename == '':
                            self.logger.log("IMAP HANDLER: This is an EML message sent from Outlook!")

                            if save_locally:
                                filename = str(self.email_number) + "_attachment_" + str(attachment_counter) + ".eml"
                                filepath = os.path.join(current_path, filename)
                                open(filepath, "wb").write(att.payload)
                                self.logger.log("IMAP HANDLER: Saved the attachment " + str(attachment_counter) + " locally!")

                            misp_handler.process_eml(att)

                        else:
                            if len(att.filename) >= 4:
                                attachment_type = att.filename
                                attachment_type = attachment_type[-4:]

                                if attachment_type == ".eml":
                                    self.logger.log("IMAP HANDLER: This is an EML message!")

                                    # In case the attachment has a very long title, shorten it to properly save it
                                    if len(att.filename) > 10:
                                        if save_locally:
                                            filepath = os.path.join(current_path,
                                                                    str(self.email_number) + "_attachment_" + str(
                                                                        attachment_counter) + ".eml")
                                            open(filepath, "wb").write(att.payload)
                                            self.logger.log("IMAP HANDLER: Saved the attachment " + str(
                                                attachment_counter) + " locally!")

                                        misp_handler.process_eml(att)

                                    else:
                                        if save_locally:
                                            filepath = os.path.join(current_path, att.filename)
                                            open(filepath, "wb").write(att.payload)
                                            self.logger.log("IMAP HANDLER: Saved the attachment " + str(
                                                attachment_counter) + " locally!")

                                        misp_handler.process_eml(att)

                                else:
                                    self.logger.log("IMAP HANDLER: This attachment is not EML!")
                                    misp_handler.process_forwarded_email(message)

                                    if save_locally:
                                        final_file_path = os.path.join(current_path, str(self.email_number) + ".eml")
                                        open(final_file_path, "wb").write(message.obj.as_bytes())

                                        att_path = os.path.join(current_path, "att_" + att.filename)
                                        open(att_path, "wb").write(att.payload)
                                        self.logger.log("IMAP HANDLER: Saved the attachment " + str(
                                            attachment_counter) + " locally!")

                            else:
                                self.logger.log("IMAP HANDLER: This attachment is not EML!")
                                misp_handler.process_forwarded_email(message)

                                if save_locally:
                                    final_file_path = os.path.join(current_path, str(self.email_number) + ".eml")
                                    open(final_file_path, "wb").write(message.obj.as_bytes())

                                    att_path = os.path.join(current_path, "att_" + att.filename)
                                    open(att_path, "wb").write(att.payload)
                                    self.logger.log(
                                        "IMAP HANDLER: Saved the attachment " + str(attachment_counter) + " locally!")

                else:
                    self.logger.log("IMAP HANDLER: This message doesn't have an attachment.")

                    if save_locally:
                        final_file_path = os.path.join(current_path, str(self.email_number) + ".eml")
                        open(final_file_path, "wb").write(message.obj.as_bytes())
                        self.logger.log("IMAP HANDLER: Saved the attachment e-mail locally!")

                    misp_handler.process_forwarded_email(message)
