import sys
import configparser
import argparse
from time import sleep
from getpass import getpass
from proxmoxer import ProxmoxAPI

def init_args():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("-h", "--host", help="The Proxmox host to connect to")

    return parser

def read_config():
    config = configparser.ConfigParser()
    config.read('config.conf')

    return config['DEFAULT']

def host_check(config, args):
    if args.host is not None:
        host = args.host
    elif 'host' in config:
        host = config['host']
        print(f"Using host {host} from config")
    else:
        print("Host must be specified via configuration or argument")
        sys.exit(2)

    return host

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
