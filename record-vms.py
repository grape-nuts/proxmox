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
        print("Using host {0} from config".format(host))
    for opt, arg in opts:
        if (opt in ("-h", "--host")):
            host = arg

    if (host == None):
        print("Host is required via -h or config file")
        sys.exit(2)

    prox = shared.prox_auth(host)

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