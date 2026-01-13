#!/usr/bin/python

import yaml
import shared

def main():
    config = shared.read_config()
    parser = shared.init_args()
    args = parser.parse_args()
    host = shared.host_check(config, args)

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
    with open(fileName, 'w', encoding="utf-8") as file:
        yaml.dump(nodes, file)

    print(f"Wrote {vmCount} vms on {nodeCount} hosts to {fileName}.")

if __name__ == "__main__":
    main()