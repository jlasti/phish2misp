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
        json_file = self.generate_json_forwarded(email)

        attachments = email.attachments
        if attachments:
            final_json = self.add_json_attachments(json_file, email)
            self.post_json_to_misp(final_json)

        else:
            self.post_json_to_misp(json_file)

    def process_eml(self, email):
        json_file = self.generate_json_eml(email)

        attachments = email.attachments
        if attachments:
            final_json = self.add_json_attachments(json_file, email)
            self.post_json_to_misp(final_json)

        else:
            self.post_json_to_misp(json_file)

    def generate_json_eml(self, email):

        return

    def generate_json_forwarded(self, email):

        return

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
