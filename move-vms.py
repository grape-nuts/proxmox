#!/usr/bin/python

import sys
import getopt
import yaml
from proxmoxer import ProxmoxAPI
from getpass import getpass
import shared

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
                    print("Migrating {0}({1}) from {2} to {3}...".format(currentVM['name'], currentVM['vmid'], currentVM['node'], expectedVMs[expectedVM]), end='', flush=True)
                    taskid = prox.nodes(currentVM['node']).qemu(currentVM['vmid']).migrate.post(target=expectedVMs[expectedVM], online=1)
                    result = shared.await_task(prox, taskid, currentVM['node'])
                    if (result['exitstatus'] == "OK"):
                        print("success")
                        count += 1
                    else:
                        print("failed")

    print("\nTask complete! Migrated {0} vms".format(count))

if __name__ == "__main__":
    main()