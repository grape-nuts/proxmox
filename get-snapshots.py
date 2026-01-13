#!/usr/bin/python

import shared

def main():
    config = shared.read_config()
    parser = shared.init_args()
    args = parser.parse_args()
    host = shared.host_check(config, args)

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
