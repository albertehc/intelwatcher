from configparser import ConfigParser

class create_config:
    def __init__(self, config_path):
        config_file = ConfigParser()
        config_file.read(config_path)

        self.bbox = config_file.get("Config", "bbox")
        self.cookie_wh = config_file.getboolean("Config", "cookie_webhooks")
        self.wh_url = config_file.get("Config", "webhook_url")
        self.workers = config_file.getint("Config", "workers")

        self.scan_type = config_file.get("DB", "scanner").lower()
        self.db_name_scan = config_file.get("DB", "scanner_db_name")
        self.db_name_portal = config_file.get("DB", "portal_db_name")

        self.db_host = config_file.get("DB", "host")
        self.db_port = config_file.getint("DB", "port")
        self.db_user = config_file.get("DB", "user")
        self.db_password = config_file.get("DB", "password")

        with open("cookie.txt", encoding="utf-8") as cookie:
            self.cookie = cookie.read()