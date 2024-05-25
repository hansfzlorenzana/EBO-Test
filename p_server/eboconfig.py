class MirrorFTP(object):
    enabled = False

    # Not required if enabled = False
    user = "ebo"
    password = "anlliG0HoQ8ZNVh"

    host = "72.14.177.84"

class EBOFTP(object):
    enabled = False

    # Not required if enabled = False
    user = 'fmdoepu9s27b'
    password = 'r52y3!pZK'

class TripodFTP(object):
    enabled = False

    # Not required if enabled = False
    user = 'na'
    password = 'na'

class LocalOutput(object):
    enabled = False

    # Not required if enabled = False
    parent_path = "/tmp"

class Email(object):
    enabled = True

    # Not required if enabled = False
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "maxims.program@gmail.com"
    smtp_password = "email alerts not working anymore, which is OK"
