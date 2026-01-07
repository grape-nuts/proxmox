#!/usr/bin/python

import sys
import getopt
import yaml
import shared

def main():
    config = shared.read_config()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:", ["host="])
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