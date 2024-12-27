#!/usr/bin/python

import sys
import getopt
import shared

def main():
    config = shared.read_config()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:t:m:", ["host=", "target=", "mode="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    host = None
    target = None
    mode = 'memory'
    if 'host' in config:
        host = config['host']
        print("Using host {0} from config".format(host))
    for opt, arg in opts:
        if (opt in ("-h", "--host")):
            host = arg
        elif (opt in ("-t", "--target")):
            target = arg
        elif (opt in ("-m", "--mode")):
            mode = arg
        else:
            print("Unknown option {0}".format(opt))
            sys.exit()

    if (host == None):
        print("Host is required via -h or config file")
        sys.exit(2)
    if (target == None):
        target = host.split(".", 1)[0]
    if (mode == 'memory'):
        nodeIndex = 'mem'
    elif (mode == 'cpu'):
        nodeIndex = 'cpu'
    else:
        print("Mode option must be either 'memory' or 'cpu'")
        sys.exit()

    prox = shared.prox_auth(host)

    nodes = prox.nodes.get()
    for i, node in enumerate(nodes):
        if (node['node'] == target):
           nodes.pop(i) 

    lowNode = nodes[0]

    count = 0
    print("\n\nMigrating the following VMs from host {0} using {1} guidelines:".format(target, mode))
    # Get the list of vmids on the target node
    for vm in prox.nodes(target).qemu.get():
        config = prox.nodes(target).qemu(vm['vmid']).config.get()
        for node in nodes:
            if (node[nodeIndex] < lowNode[nodeIndex]):
                lowNode = node
        print("{0}({1}) to host {2}...".format(config['name'], vm['vmid'], lowNode['node']), end='', flush=True)
        taskid = prox.nodes(target).qemu(vm['vmid']).migrate.post(target=lowNode['node'], online=1)
        result = shared.await_task(prox, taskid, target)
        if (result['exitstatus'] == "OK"):
            print("success")
            count += 1
        else:
            print("failed")

    print ("\nTask complete! Migrated {0} vms".format(count))

if __name__ == "__main__":
    main()