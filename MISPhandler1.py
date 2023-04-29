import base64
import os
from imap_tools import MailBox, MailMessage
import requests
import json
import mailparser


class MISPhandler:
    def __init__(self, misp_url, misp_key, logger, IP_filter, domain_filter, address_filter):
        self.url = misp_url
        self.key = misp_key
        self.logger = logger
        self.IP_filter = IP_filter
        self.domain_filter = domain_filter
        self.address_filter = address_filter

    # Function to process a retrieved e-mail and submit it to MISP as well as the attachments
    # First, we determine whether the e-mail contains an attachment.
    # If it does not contain an attachment, we take the data of interest from the e-mail header, generate a JSON and
    # submit it to MISP. If the e-mail does contain an attachment, we repeat the same process, but we also submit the
    # attachments afterwards.

    def process_forwarded_email(self, email):
        json_file = self.generate_json(email, "forwarded")

        if json_file == "Blocked":
            return

        attachments = email.attachments
        if attachments:
            final_json = self.add_json_attachments(json_file, email)
            self.post_json_to_misp(final_json)

        else:
            self.post_json_to_misp(json_file)

    def process_eml(self, email):
        json_file = self.generate_json(email, "eml")

        if json_file == "Blocked":
            return

        attachments = email.attachments
        if attachments:
            final_json = self.add_json_attachments(json_file, email)
            self.post_json_to_misp(final_json)

        else:
            self.post_json_to_misp(json_file)

    def generate_json(self, email, option):
        mail = mailparser.parse_from_bytes(email.obj.as_bytes())

        email_date = str(email.date)[0:10]
        email_uid = email.uid
        email_subject = email.subject
        email_body = email.text
        email_ipsrc = 'None'
        email_domain = 'None'
        email_src = email.from_

        if 'from' in mail.received[0]:
            email_ipsrc = str(mail.received[0]['from']).split(' ')[1]
            email_domain = str(mail.received[0]['from']).split(' ')[0]

        if self.IP_filter:
            for i in open("IPblacklist.txt", "r"):
                print("Checking IP blacklist : " + str(i) + " / " + email_ipsrc)
                if i == email_ipsrc:
                    return "Blocked"

        if self.domain_filter:
            for i in open("domainblacklist.txt", "r"):
                if i == email_domain:
                    return "Blocked"

        if self.address_filter:
            for i in open("addressblacklist.txt", "r"):
                if i == email_src:
                    return "Blocked"

        if option == "eml":
            final_json = {
                "Event":
                    {
                        "date": email_date,
                        "threat_level_id": "4",
                        "info": "Email submitted to MISP",
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

        else:
            final_json = {
                "Event":
                    {
                        "date": email_date,
                        "threat_level_id": "4",
                        "info": "Email submitted to MISP",
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

        return final_json

    def add_json_attachments(self, json_file, email):

        return

    def post_json_to_misp(self, json_file):
        headers = {
            'Accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': str(self.key),
        }

        y = json.dumps(json_file)
        data = y.replace('\n', '').replace('\r', '').encode()
        response = requests.post(self.url, headers=headers, data=data, verify=False)
        print(response)
