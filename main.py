import os
import logger
import configparser
import IMAPhandler
import MISPhandler
import imap_tools
from imap_tools import MailBox, MailMessage


###
# Main class, first loads the config file and then proceeds accordingly.
###

def main():
    ###
    # Initialize variables loaded from the config file, create logger, create MISP and IMAP handlers
    ###

    conf_save_locally = True  # save emails locally after downloading them
    conf_misp_url = ''  # URL addr of MISP instance to connect to
    conf_misp_key = ''  # API key of the MISP instance
    conf_IMAP_server = ''  # Address of IMAP server to connect to
    conf_IMAP_login = ''  # E-mail box login
    conf_IMAP_pass = ''  # E-mail box password
    log = logger.Logger("log.txt")
    log.log("MAIN FUNCTION: Loading config file")
    config = configparser.ConfigParser()

    try:
        config.read('config.ini')

        conf_save_locally = config.getboolean('global', 'save_locally')
        conf_misp_url = config.get('misp', 'misp_url')
        conf_misp_key = config.get('misp', 'misp_key')
        conf_IMAP_server = config.get('imap', 'IMAP_server')
        conf_IMAP_login = config.get('imap', 'IMAP_login')
        conf_IMAP_pass = config.get('imap', 'IMAP_pass')

        log.log("MAIN FUNCTION: Config successfully loaded!")

    except FileNotFoundError:
        log.log("MAIN FUNCTION: Config not found, using default values instead!")

    misp_handler = MISPhandler.MISPhandler(conf_misp_url, conf_misp_key, log, True, True, True)
    email_handler = IMAPhandler.IMAPhandler(conf_IMAP_server, conf_IMAP_login, conf_IMAP_pass, log)

    email_handler.retrieve_emails(conf_save_locally, misp_handler)


if __name__ == "__main__":
    main()
