#!/usr/bin/python

import sys
import getopt
import yaml
from time import sleep
from proxmoxer import ProxmoxAPI
from getpass import getpass

def await_task(proxmox_api, taskid, node):
    data = {"status": ""}
    while (data['status'] != "stopped"):
        sleep(1.0) # Looping with no governor causes RemoteDisconnected() errors
        data = proxmox_api.nodes(node).tasks(taskid).status.get()
    return data

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:", ["host="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    host = None
    for opt, arg in opts:
        if (opt in ("-h", "--host")):
            host = arg

    if (host == None):
        print("Host is required")
        sys.exit(2)

    username = input("user@realm: ")
    passw = getpass()

    try:
        prox = ProxmoxAPI(host, user=username, password=passw)
    except:
        print("Error connecting to proxmox host {0} as user {1}".format(host, username))
        sys.exit()

    file = "./vms.yaml"

    try:
        fileHandle = open(file, "r")
        nodes = yaml.safe_load(fileHandle)
        fileHandle.close()
    except FileNotFoundError:
        print("File not found")
        sys.exit(2)

    currentVMs = prox.cluster.resources.get(type='vm')

    expectedVMs = {}
    for node in nodes:
        for vm in nodes[node]:
            expectedVMs[vm] = node

    count = 0
    for currentVM in currentVMs:
        for expectedVM in expectedVMs:
            if (expectedVM == currentVM['name']):
                if (expectedVMs[expectedVM] != currentVM['node']):
                    print("Migrating {0}({1}) from {2} to {3}".format(currentVM['name'], currentVM['vmid'], currentVM['node'], expectedVMs[expectedVM]))
                    taskid = prox.nodes(currentVM['node']).qemu(currentVM['vmid']).migrate.post(target=expectedVMs[expectedVM], online=1)
                    result = await_task(prox, taskid, currentVM['node'])
                    if (result['exitstatus'] == "OK"):
                        print("Migrated {0} successfully".format(currentVM['name']))
                        count += 1

    print("\nTask complete! Migrated {0} vms".format(count))

if __name__ == "__main__":
    main()