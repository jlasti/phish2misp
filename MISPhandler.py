from imap_tools import MailBox, MailMessage
import requests
import json
import mailparser
import hashlib
import os


class MISPhandler:
    def __init__(self, misp_url, misp_key, misp_event_name, logger, IP_filter, domain_filter, address_filter):
        self.url = misp_url
        self.key = misp_key
        self.event_name = misp_event_name
        self.logger = logger
        self.IP_filter = IP_filter
        self.domain_filter = domain_filter
        self.address_filter = address_filter
        self.logger.log("MISP HANDLER: MISP handler instance successfully invoked!")

    def process_forwarded_email(self, email):
        self.logger.log("MISP HANDLER: I am processing a forwarded email!")
        json_file = self.generate_json(email, "forwarded")

        if json_file == "Blocked":
            self.logger.log("MISP HANDLER: This e-mail was blacklisted and not added to MISP.")
            return

        attachments = email.attachments
        if attachments:
            final_json = self.add_json_attachments(json_file, email)
            self.post_json_to_misp(final_json)

        else:
            self.post_json_to_misp(json_file)

    def process_eml(self, eml):
        self.logger.log("MISP HANDLER: I am processing an .EML email!")
        email = MailMessage.from_bytes(eml.payload)
        json_file = self.generate_json(email, "eml")

        if json_file == "Blocked":
            self.logger.log("MISP HANDLER: This e-mail was blacklisted and not added to MISP.")
            return

        attachments = email.attachments
        if attachments:
            final_json = self.add_json_attachments(json_file, email)
            self.post_json_to_misp(final_json)

        else:
            self.post_json_to_misp(json_file)

    def add_json_attachments(self, json_file, email):
        self.logger.log("MISP HANDLER: This e-mail has attachments, I am adding them into the MISP event.")
        attachments = email.attachments
        new_json = json_file

        for att in attachments:
            md5 = hashlib.md5()
            payload = att.payload
            md5.update(payload)

            append = {"type": "md5",
                      "category": "Payload delivery",
                      "to_ids": False,
                      "distribution": "0",
                      "comment": "md5 hash of the attachment",
                      "value": md5.hexdigest()
                      }

            new_json['Event']['Attribute'].append(append)
            self.logger.log("MISP HANDLER: Attachment added!")

        self.logger.log("MISP HANDLER: All attachments have been added, returning the final JSON.")
        return new_json

    def post_json_to_misp(self, json_file):
        self.logger.log("MISP HANDLER: Posting the final JSON to MISP!")
        headers = {
            'Accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': str(self.key),
        }

        y = json.dumps(json_file)
        data = y.replace('\n', '').replace('\r', '').encode()
        response = requests.post(self.url, headers=headers, data=data, verify=False)
        self.logger.log("MISP HANDLER: Event posted to MISP, response from MISP is:")
        self.logger.log(str(response))

    def generate_json(self, email, option):
        self.logger.log("MISP HANDLER: Generating a JSON request for this E-mail!")
        mail = mailparser.parse_from_bytes(email.obj.as_bytes())

        email_date = str(email.date)[0:10]
        email_uid = email.uid
        email_subject = email.subject
        email_body = email.text
        email_ipsrc = 'None'
        email_domain = 'None'
        email_src = email.from_

        if 'from' in mail.received[0]:
            if ' ' in mail.received[0]['from']:
                email_ipsrc = str(mail.received[0]['from']).split(' ')[1]
                email_domain = str(mail.received[0]['from']).split(' ')[0]

        if self.IP_filter:
            for i in open(os.path.join(os.path.dirname(__file__), "ipblacklist.txt"), "r"):
                if i == email_ipsrc:
                    self.logger.log("MISP HANDLER: This e-mails sender IP is blacklisted! IP: " + str(i))
                    return "Blocked"

        if self.domain_filter:
            for i in open(os.path.join(os.path.dirname(__file__), "domainblacklist.txt"), "r"):
                if i == email_domain:
                    self.logger.log("MISP HANDLER: This e-mails sender domain is blacklisted! Domain: " + str(i))
                    return "Blocked"

        if self.address_filter:
            for i in open(os.path.join(os.path.dirname(__file__), "addressblacklist.txt"), "r"):
                if i == email_src:
                    self.logger.log("MISP HANDLER: This e-mails sender address is blacklisted! Address: " + str(i))
                    return "Blocked"

        if option == "eml":
            final_json = {
                "Event":
                    {
                        "date": email_date,
                        "threat_level_id": "4",
                        "info": self.event_name,
                        "published": False,
                        "analysis": "0",
                        "distribution": "0",
                        "Attribute":
                            [{"type": "email",
                              "category": "Network activity",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "Email message submitted to system",
                              "value": email_uid
                              },
                             {"type": "ip-src",
                              "category": "Network activity",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "E-mail source IP address",
                              "value": email_ipsrc
                              },
                             {"type": "domain",
                              "category": "Network activity",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "Sender domain of the email.",
                              "value": email_domain
                              },
                             {"type": "email-src",
                              "category": "Network activity",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "E-mail source address",
                              "value": email_src
                              },
                             {"type": "email-subject",
                              "category": "Payload delivery",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "E-mail subject",
                              "value": email_subject
                              },
                             {"type": "email-body",
                              "category": "Payload delivery",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "E-mail body",
                              "value": email_body
                              },
                             ]
                    }
            }

            self.logger.log("MISP HANDLER: JSON generated, returning a JSON for EML!")
            return final_json

        else:
            final_json = {
                "Event":
                    {
                        "date": email_date,
                        "threat_level_id": "4",
                        "info": self.event_name,
                        "published": False,
                        "analysis": "0",
                        "distribution": "0",
                        "Attribute":
                            [{"type": "email",
                              "category": "Network activity",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "Email message without attachments",
                              "value": email_uid
                              },
                             {"type": "email-subject",
                              "category": "Payload delivery",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "E-mail subject",
                              "value": email_subject
                              },
                             {"type": "email-body",
                              "category": "Payload delivery",
                              "to_ids": False,
                              "distribution": "0",
                              "comment": "E-mail body",
                              "value": email_body
                              },
                             ]
                    }
            }

            self.logger.log("MISP HANDLER: JSON generated, returning a JSON for a forwarded email!")
            return final_json
