#!/usr/bin/python

import sys
import getopt
import shared

def main():
    config = shared.read_config()

    try:
        opts = getopt.getopt(sys.argv[1:], "h:", ["host="])[0]
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    host = None
    if 'host' in config:
        host = config['host']
        print(f"Using host {host} from config")
    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = arg

    if host is None:
        print("Host is required via -h or config file")
        sys.exit(2)

    prox = shared.prox_auth(host)

    encumberedVMs = {}

    flag = False
    for node in prox.nodes.get():
        vms = prox.nodes(node['node']).qemu.get()
        for vm in vms:
            snapCount = 0
            snapshot = []
            snaps = prox.nodes(node['node']).qemu(vm['vmid']).snapshot.get()
            for snap in snaps:
                if snap['name'] != 'current':
                    snapshot.append(snap)
                    snapCount += 1
            if snapCount > 0:
                flag = True
                encumberedVMs[vm['name']] = []
                encumberedVMs[vm['name']].append(snapshot)

    if flag:
        for vm in encumberedVMs:
            print(f"{vm}:")
            for snapshot in encumberedVMs[vm]:
                for snaps in snapshot:
                    print(f"  {snaps['name']}")
    else:
        print("No snapshots found")

if __name__ == "__main__":
    main()
