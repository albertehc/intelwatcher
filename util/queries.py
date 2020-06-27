from pymysql import connect
from datetime import datetime, timedelta 

class create_queries():
    def __init__(self, config, cursor):
        self.cursor = cursor
        self.portal = config.db_name_portal
        self.schema = config.scan_type
        self.ingress = config.db_name_portal
    
    def update_point(self, wp_type, name, url, wp_id):
        name = str(name).replace("'", "\\'")
        if wp_type == "Stop":
            if self.schema == "mad":
                self.cursor.execute(f"UPDATE pokestop SET name = '{name}', image = '{url}' WHERE pokestop_id = '{wp_id}';")
            elif self.schema == "rdm":
                self.cursor.execute(f"UPDATE pokestop SET name = '{name}', url = '{url}' WHERE id = '{wp_id}';")
        elif wp_type == "Gym":
            if self.schema == "mad":
                self.cursor.execute(f"UPDATE gymdetails SET name = '{name}', url = '{url}' WHERE gym_id = '{wp_id}';")
            elif self.schema == "rdm":
                self.cursor.execute(f"UPDATE gym SET name = '{name}', url = '{url}' WHERE id = '{wp_id}';")

    def update_portal(self, e_id, name, url, lat, lon, updated):
        name = str(name).replace("'", "\\'")
        self.cursor.execute(f"INSERT INTO {self.ingress}.ingress_portals(external_id, name, url, lat, lon, updated, imported) VALUES('{e_id}', '{name}', '{url}', {lat}, {lon}, {updated}, {updated}) ON DUPLICATE KEY UPDATE updated = {updated}, name = '{name}', url = '{url}', lat = {lat}, lon = {lon}")

    def get_empty_gyms(self):
        if self.schema == "mad":
            self.cursor.execute(f"SELECT gym.gym_id FROM gym LEFT JOIN gymdetails on gym.gym_id = gymdetails.gym_id;")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id FROM gym;")
        gyms = self.cursor.fetchall()
        return gyms

    def get_empty_stops(self):
        if self.schema == "mad":
            self.cursor.execute(f"SELECT pokestop_id FROM pokestop;")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id FROM pokestop;")
        stops = self.cursor.fetchall()
        return stops
