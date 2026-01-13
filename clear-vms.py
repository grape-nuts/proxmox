#!/usr/bin/python

import shared

def main():
    config = shared.read_config()
    parser = shared.init_args()
    parser.add_argument("-t", "--target", help="Specify a target host")
    parser.add_argument("-m", "--mode", default="memory", help="Specify mode [cpu, memory]")
    args = parser.parse_args()
    host = shared.host_check(config, args)

    target = args.target
    mode = args.mode

    if target is None:
        target = host.split(".", 1)[0]

    if mode == 'cpu':
        nodeIndex = 'cpu'
    nodeIndex = 'mem'

    prox = shared.prox_auth(host)

    nodes = prox.nodes.get()
    for i, node in enumerate(nodes):
        if node['node'] == target:
            nodes.pop(i)

    lowNode = nodes[0]

    count = 0
    print(f"\n\nMigrating the following VMs from host {target} using {mode} guidelines:")
    # Get the list of vmids on the target node
    for vm in prox.nodes(target).qemu.get():
        config = prox.nodes(target).qemu(vm['vmid']).config.get()
        for node in nodes:
            if node[nodeIndex] < lowNode[nodeIndex]:
                lowNode = node
        print(f"{config['name']}({vm['vmid']}) to host {lowNode['node']}...", end='', flush=True)
        taskid = prox.nodes(target).qemu(vm['vmid']).migrate.post(target=lowNode['node'], online=1)
        result = shared.await_task(prox, taskid, target)
        if result['exitstatus'] == "OK":
            print("success")
            count += 1
        else:
            print("failed")

    print (f"\nTask complete! Migrated {count} vms")

if __name__ == "__main__":
    main()
