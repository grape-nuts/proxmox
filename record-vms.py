#!/usr/bin/python

import sys
import getopt
import yaml
from proxmoxer import ProxmoxAPI
from getpass import getpass

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
    
    nodes = {}
    nodeCount = 0
    vmCount = 0
    for node in prox.nodes.get():
        vms = prox.nodes(node['node']).qemu.get()
        nodes[node['node']] = []
        nodeCount += 1
        for vm in vms:
            nodes[node['node']].append(vm['name'])
            vmCount += 1

    fileName = 'vms.yaml'
    with open(fileName, 'w') as file:
        yaml.dump(nodes, file)

    print("Wrote {0} vms on {1} hosts to {2}.".format(vmCount, nodeCount, fileName))

if __name__ == "__main__":
    main()