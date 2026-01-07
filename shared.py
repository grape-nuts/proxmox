import sys
import configparser
from time import sleep
from getpass import getpass
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

def prox_auth(host):
    config = read_config()

    if 'tokenName' in config and 'tokenUser' in config and 'tokenValue' in config:
        print(f"Using API token {config['tokenUser']}!{config['tokenName']} from config")
        try:
            prox = ProxmoxAPI(host, user=config['tokenUser'], token_name=config['tokenName'], token_value=config['tokenValue'])
        except RuntimeError:
            print(f"Error connection to proxmox host {host} with token {config['tokenName']}")
    else:
        username = input("user@realm: ")
        passw = getpass()
        try:
            prox = ProxmoxAPI(host, user=username, password=passw)
        except RuntimeError:
            print(f"Error connecting to proxmox host {host} as user {username}")
            sys.exit()

    return prox
