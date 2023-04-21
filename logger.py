import datetime


class Logger:
    def __init__(self, path):
        self.logfile = open(path, "a")
        self.log("***NEW START***")

    def log(self, text):
        self.logfile.write(str(datetime.datetime.now()) + " - " + text + "\n")

    def close_log(self):
        self.logfile.close()
