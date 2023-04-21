import os

import imap_tools
from imap_tools import MailBox, MailMessage
import email
import datetime


class IMAPhandler:
    def __init__(self, IMAP_server, IMAP_login, IMAP_password, logger):
        self.server = IMAP_server
        self.login = IMAP_login
        self.password = IMAP_password
        self.logger = logger
        self.email_number = 0

    def retrieve_emails(self, save_locally, misp_handler):
        cwd = os.getcwd() + "/downloads/"
        self.logger.log("IMAP HANDLER: Retrieving emails!")

        with MailBox(self.server).login(self.login, self.password, 'INBOX') as mailbox:
            for message in mailbox.fetch():
                ###
                # LEN NA TESTOVANIE
                ###

                #if self.email_number == 1:
                #    return 0

                self.email_number = self.email_number + 1
                self.logger.log("IMAP HANDLER: Fetching message #" + str(self.email_number))
                attachments = message.attachments

                # Save the e-mail into a unique folder if the option is allowed
                if save_locally:
                    current_path = os.path.join(
                        cwd + str(datetime.datetime.now().date()) + "#" + str(self.email_number))
                    os.mkdir(current_path)

                #####
                # Cases 2, 3, 4 - the received e-mail contains an attachment
                #####

                print("##### MESSAGE NUMBER " + str(self.email_number))

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
                                filepath = os.path.join(cwd, filename)
                                open(filepath, "wb").write(att.payload)

                            # process_email(att)

                        else:
                            if len(att.filename) >= 4:
                                attachment_type = att.filename
                                attachment_type = attachment_type[-4:]

                                if attachment_type == ".eml":
                                    self.logger.log("IMAP HANDLER: This is an EML message!")

                                    # In case the attachment has a very long title, shorten it to properly save it
                                    if len(att.filename) > 10:
                                        if save_locally:
                                            filepath = os.path.join(cwd,
                                                                    str(self.email_number) + "_attachment_" + str(
                                                                        attachment_counter) + ".eml")
                                            open(filepath, "wb").write(att.payload)

                                        # process_email(att)

                                    else:
                                        if save_locally:
                                            filepath = os.path.join(cwd, att.filename)
                                            open(filepath, "wb").write(att.payload)

                                        # process_email(att)

                                else:
                                    self.logger.log("IMAP HANDLER: This attachment is not EML!")
                                    misp_handler.process_email(message)

                            else:
                                self.logger.log("IMAP HANDLER: This attachment is not EML!")
                                print("Saving attachment and email.")
                                misp_handler.process_email(message)

                                if save_locally:
                                    final_file_path = os.path.join(current_path, str(self.email_number) + ".eml")
                                    open(final_file_path, "wb").write(message.obj.as_bytes())
                                    att_path = os.path.join(current_path, "Attachments", att.filename)
                                    open(att_path, "wb").write(att.payload)



                #####
                # Case 1 - the email does not contain an attachment and was sent directly
                #####
                else:
                    self.logger.log("IMAP HANDLER: This message doesn't have an attachment.")

                    if save_locally:
                        final_file_path = os.path.join(current_path, str(self.email_number) + ".eml")
                        open(final_file_path, "wb").write(message.obj.as_bytes())

                    misp_handler.process_email(message)
