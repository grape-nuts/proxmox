#!/usr/bin/python

import sys
import getopt
from enum import Enum
from time import sleep
from proxmoxer import ProxmoxAPI
from getpass import getpass

def await_task(proxmox_api, taskid, node):
    data = {"status": ""}
    while (data['status'] != "stopped"):
        sleep(1.0) # Looping with no governor causes RemoteDisconnected() errors
        data = proxmox_api.nodes(node).tasks(taskid).status.get()
    return data

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:t:m:", ["host=", "target=", "mode="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    host = None
    target = None
    mode = 'memory'
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
        print("Host is required")
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

    username = input("user@realm: ")
    passw = getpass()

    try:
        prox = ProxmoxAPI(host, user=username, password=passw)
    except:
        print("Error connecting to proxmox host {0} as user {1}".format(host, username))
        sys.exit()

    nodes = prox.nodes.get()
    for i, node in enumerate(nodes):
        if (node['node'] == target):
           nodes.pop(i) 

    lowNode = nodes[0]

    print("\n\nMigrating the following VMs from host {0} using {1} guidelines:".format(target, mode))
    # Get the list of vmids on the target node
    for vm in prox.nodes(target).qemu.get():
        config = prox.nodes(target).qemu(vm['vmid']).config.get()
        for node in nodes:
            if (node[nodeIndex] < lowNode[nodeIndex]):
                lowNode = node
        print("{0}-{1} to host {2}...".format(vm['vmid'], config['name'], lowNode['node']), end='', flush=True)
        taskid = prox.nodes(target).qemu(vm['vmid']).migrate.post(target=lowNode['node'], online=1)
        result = await_task(prox, taskid, target)
        if (result['exitstatus'] == "OK"):
            print("success")
        else:
            print("failed")

if __name__ == "__main__":
    main()