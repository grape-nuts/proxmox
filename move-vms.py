#!/usr/bin/python

import sys
import yaml
import shared

def main():
    config = shared.read_config()
    parser = shared.init_args()
    args = parser.parse_args()
    host = shared.host_check(config, args)

    prox = shared.prox_auth(host)

    file = "./vms.yaml"

    try:
        fileHandle = open(file, "r", encoding="utf-8")
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
            if expectedVM == currentVM['name']:
                if expectedVMs[expectedVM] != currentVM['node']:
                    print(f"Migrating {currentVM['name']}({currentVM['vmid']}) from {currentVM['node']} to {expectedVMs[expectedVM]}...", end='', flush=True)
                    taskid = prox.nodes(currentVM['node']).qemu(currentVM['vmid']).migrate.post(target=expectedVMs[expectedVM], online=1)
                    result = shared.await_task(prox, taskid, currentVM['node'])
                    if result['exitstatus'] == "OK":
                        print("success")
                        count += 1
                    else:
                        print("failed")

    print(f"\nTask complete! Migrated {count} vms")

if __name__ == "__main__":
    main()