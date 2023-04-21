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

    def process_email(self, email):
        attachments = email.attachments
        mail = mailparser.parse_from_bytes(email.obj.as_bytes())
        # print(email.headers)

        headers = {
            'Accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': str(self.key),
        }

        if attachments:
            print("")
            # TODO

        else:
            email_date = str(email.date)[0:10]
            email_uid = email.uid
            email_ipsrc = 'None'
            email_domain = 'None'
            email_dst = email.to[0]
            email_src = email.from_
            email_subject = email.subject
            email_body = email.text

            print("*** RECEIVED *** : " + str(mail.received[0]))

            if 'from' in mail.received[0]:
                email_ipsrc = str(mail.received[0]['from']).split(' ')[1]
                email_domain = str(mail.received[0]['from']).split(' ')[0]
                # print("*** From *** : " + str(mail.received[0]['from']))
                # print("IP addr:" + email_ipsrc)
                # print("Domain:" + email_domain)

            # Blacklist checks - sender IP address, sender domain, sender e-mail address

            if self.IP_filter:
                for i in open("IPblacklist.txt", "r"):
                    print("Checking IP blacklist : " + str(i) + " / " + email_ipsrc)
                    if i == email_ipsrc:
                        return

            if self.domain_filter:
                for i in open("domainblacklist.txt", "r"):
                    if i == email_domain:
                        return

            if self.address_filter:
                for i in open("addressblacklist.txt", "r"):
                    if i == email_src:
                        return

            # Processing e-mail without attachments
            self.logger.log("MISP HANDLER: Processing e-mail without attachments")
            properties = {
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

            y = json.dumps(properties)
            data = y.replace('\n', '').replace('\r', '').encode()
            response = requests.post('https://185.227.111.227/events', headers=headers, data=data, verify=False)
            print(response)
