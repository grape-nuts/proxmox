#!/usr/bin/python

import sys
import getopt
import yaml
from pprint import pprint
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

    prox = shared.prox_auth(host, username, passw)
    
    encumberedVMs = {}

    flag = False
    for node in prox.nodes.get():
        vms = prox.nodes(node['node']).qemu.get()
        for vm in vms:
            snapCount = 0
            snapshot = []
            snaps = prox.nodes(node['node']).qemu(vm['vmid']).snapshot.get()
            for snap in snaps:
                if (snap['name'] != 'current'):
                    snapshot.append(snap)
                    snapCount += 1
            if (snapCount > 0):
                flag = True
                encumberedVMs[vm['name']] = []
                encumberedVMs[vm['name']].append(snapshot)

    if (flag == True):
        for vm in encumberedVMs:
            print("{0}:".format(vm))
            for snapshot in encumberedVMs[vm]:
                for snaps in snapshot:
                    print("  " + snaps['name'])
    else:
        print("No snapshots found")

if __name__ == "__main__":
    main()