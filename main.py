#!/usr/bin/python
import logger
import configparser
import IMAPhandler
import MISPhandler
import os

'''
Main class, first loads the config file, starts logging and creates instances for IMAP and MISP handlers
'''


def main():
    """
    Default values for variables
    """

    conf_save_locally = True  # save emails locally after downloading them
    conf_misp_url = ''  # URL addr of MISP instance to connect to
    conf_misp_key = ''  # API key of the MISP instance
    conf_IMAP_server = ''  # Address of IMAP server to connect to
    conf_IMAP_login = ''  # E-mail box login
    conf_IMAP_pass = ''  # E-mail box password
    log = logger.Logger(os.path.join(os.path.dirname(__file__),"log.txt"))
    log.log("MAIN FUNCTION: Loading config file")
    config = configparser.ConfigParser()

    """
    Load values from config file
    """

    try:
        current_path = os.path.dirname(__file__)
        config.read(os.path.join(current_path, 'config.ini'))

        conf_save_locally = config.getboolean('global', 'save_locally')
        conf_misp_url = config.get('misp', 'misp_url')
        conf_misp_key = config.get('misp', 'misp_key')
        conf_IMAP_server = config.get('imap', 'IMAP_server')
        conf_IMAP_login = config.get('imap', 'IMAP_login')
        conf_IMAP_pass = config.get('imap', 'IMAP_pass')

        log.log("MAIN FUNCTION: Config successfully loaded!")

    except FileNotFoundError:
        log.log("MAIN FUNCTION: Config not found, using default values instead!")

    """
    Check if the required values are loaded
    """

    if conf_misp_url == '' or conf_misp_key == '' or conf_IMAP_server == '' or conf_IMAP_login == '' or conf_IMAP_pass == '':
        log.log("MAIN FUNCTION: Config file is missing key information, cannot start! Check config file!")
        return

    """
    Create instances for handlers
    """
    misp_handler = MISPhandler.MISPhandler(conf_misp_url, conf_misp_key, log, True, True, True)
    email_handler = IMAPhandler.IMAPhandler(conf_IMAP_server, conf_IMAP_login, conf_IMAP_pass, log)

    """
    Start the downloading and extraction process
    """
    email_handler.retrieve_emails(conf_save_locally, misp_handler)

    log.log("***MAIN FUNCTION: Run finished, exiting!***")


if __name__ == "__main__":
    main()
