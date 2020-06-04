import argparse
#import json
#import math
import sys
#import datetime
import requests
import time

#from configparser import ConfigParser
from pymysql import connect

from util.ingress import IntelMap, MapTiles
from util.config import create_config
from util.queries import create_queries

def connect_db(config):
    mydb = connect(host = config.db_host, user = config.db_user, password = config.db_password, database = config.db_name_scan, port = config.db_port, autocommit = True)
    cursor = mydb.cursor()
    queries = create_queries(config, cursor)

    return queries

def update_wp(wp_type, points):
    updated = 0
    print(f"Found {len(points)} {wp_type}s")
    for wp in points:
        portal_details = scraper.get_portal_details(wp[0])
        if portal_details is not None:
            try:
                queries.update_point(wp_type, portal_details.get("result")[portal_name], portal_details.get("result")[portal_url], wp[0])
                updated += 1
                print(f"Updated {wp_type} {portal_details.get('result')[portal_name]}")
            except Exception as e:
                print(f"Could not update {wp_type} {wp[0]}")
                print(e)
        else:
            print(f"Couldn't get Portal info for {wp_type} {wp[0]}")
            
    print(f"Updated {updated} {wp_type}s")
    print("")

def scrape_all():
    zoom = 15
    bbox = list(config.bbox.split(';'))
    tiles = []
    for cord in bbox:
        bbox_cord = list(map(float, cord.split(',')))
        bbox_cord.append(zoom)
        mTiles = MapTiles(bbox_cord)
        tiles = tiles + mTiles.getTiles()
    total_tiles = len(tiles)
    print(f"Total tiles to scrape: {total_tiles} - Starting now")

    timed_out_items = []
    portals = []
    portal_ids = []
    tiles_data = []
    for idx, tile in enumerate(tiles):
        iitc_xtile = int(tile[0])
        iitc_ytile = int(tile[1])
        
        iitc_tile_name  = f"{zoom}_{iitc_xtile}_{iitc_ytile}_0_8_100"
        current_tile = idx + 1
        print(f"[{current_tile}/{total_tiles}]")
        try:
            tiles_data.append(scraper.get_entities([iitc_tile_name]))
        except Exception as e:
            print(f"Something went wrong with tile {iitc_tile_name}")
            print(e)
    for tile_data in tiles_data:
        try:
            if "result" in tile_data:
                for data in tile_data["result"]["map"]:
                    if "error" in tile_data["result"]["map"][data]:
                        timed_out_items.append(data)
                    else:
                        for entry in tile_data["result"]["map"][data]["gameEntities"]:
                            #print(entry)
                            if entry[2][0] == "p":
                                portal_ids.append(entry[0])
                                portals.append(entry[2])
                                #print(entry[0])
        except Exception as e:
            print("Something went wrong when parsing Portals")
            print(e)
    
    queries = connect_db(config)
    updated_portals = 0
    for idx, val in enumerate(portal_ids):
        lat = (portals[idx][2])/1e6
        lon = (portals[idx][3])/1e6
        p_name = portals[idx][portal_name]
        p_url = portals[idx][portal_url]
        updated_ts = int(time.time())
        try:
            queries.update_portal(val, p_name, p_url, lat, lon, updated_ts)
            updated_portals += 1
        except Exception as e:
            print(f"Failed putting Portal {p_name} ({val}) in your DB")
            print(e)

    print(f"Done. Put {updated_portals} Portals in your DB.")

if __name__ == "__main__":
    print("Initializing...")
    portal_name = 8
    portal_url = 7

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--update", action='store_true', help="Updates all Gyms and Stops using Portal info")
    parser.add_argument("-c", "--config", default="config.ini", help="Config file to use")
    args = parser.parse_args()
    config_path = args.config

    config = create_config(config_path)
    

    scraper = IntelMap(config.cookie)

    if not scraper.getCookieStatus():
        print("There's something wrong with your Cookie! Try getting a new one")
        if config.cookie_wh:
            data = {
                "username": "Cookie Alarm",
                "avatar_url": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/237/cookie_1f36a.png",
                "embeds": [{
                    "description": ":cookie: Your Intel Cookie probably ran out! Please get a new one or check your account.",
                    "color": 16073282
                }]
            }
            result = requests.post(config.wh_url, json=data)
            print(result)
        sys.exit(1)
    else:
        print("Cookie works!")

    print("Got everything. Starting to scrape now.")

    if args.update:
        queries = connect_db(config)
        gyms = queries.get_empty_gyms()
        stops = queries.get_empty_stops()
        update_wp("Gym", gyms)
        update_wp("Stop", stops)
        sys.exit()

    scrape_all()