import sys
import configparser
from time import sleep
from proxmoxer import ProxmoxAPI

def read_config():
    config = configparser.ConfigParser()
    config.read('config.conf')

    return config['DEFAULT']

def await_task(proxmox_api, taskid, node):
    data = {"status": ""}
    while data['status'] != "stopped":
        sleep(1.0) # Looping with no governor causes RemoteDisconnected() errors
        data = proxmox_api.nodes(node).tasks(taskid).status.get()
    return data

def prox_auth(host, username, passw):
    try:
        prox = ProxmoxAPI(host, user=username, password=passw)
    except Exception:
        print("Error connecting to proxmox host {0} as user {1}".format(host, username))
        sys.exit()

    return prox
