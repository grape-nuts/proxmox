#!/usr/bin/python

import shared

def main():
    config = shared.read_config()
    parser = shared.init_args()
    parser.add_argument("-s", "--source", required=True, help="Source datastore")
    parser.add_argument("-d", "--destination", required=True, help="Destination datastore")
    args = parser.parse_args()
    host = shared.host_check(config, args)

    source = args.source
    destination = args.destination

    diskBus = ['scsi', 'efidisk', 'sata']
    node = host.split(".", 1)[0]
    vmid = []
    vmNode = []

    prox = shared.prox_auth(host)

    #if (source != exist):
        #exit gracefully

    #if (destination != exist):
        #exit gracefully

    # Get the list of vmids that have a disk image on the source datastore
    for image in prox.nodes(node).storage(source).content.get():
        vmid.append(f"{image['vmid']}")

    #TODO: check for snapshots on any of the vmids, and stop if one is found

    # Remove duplicates from the list and sort
    vmid = [*set(vmid)]
    vmid.sort()

    # Get the node that each vmid belongs to
    for vm in prox.cluster.resources.get(type="vm"):
        for iden in vmid:
            if iden == str(vm['vmid']):
                vmNode.append(f"{vm['node']}")

    # Loop through the vmids, get their config from the corresponding node, get the
    # list of disks from the config, and if the disk is on the source datastore,
    # move it to the destination datastore
    count = 0
    for vm in vmid:
        config = prox.nodes(vmNode[count]).qemu(vm).config.get()
        disks = []
        for busType in diskBus:
            for i in range(0, 30):
                diskStr = busType + str(i)
                if diskStr in config:
                    disks.append([f"{config[diskStr]}", diskStr])
        for disk in disks:
            diskStorageID = disk[0].split(":", 1)[0]
            if diskStorageID == source:
                print(f"Moving {disk[0]} for VM {vm} to {destination}... ", end="", flush=True)
                taskid = prox.nodes(vmNode[count]).qemu(vm).move_disk.post(disk=disk[1], storage=destination, delete=1)
                # We have to wait for each task to complete, otherwise vmids with multiple disks being moved will fail
                shared.await_task(prox, taskid, vmNode[count])
                print("complete!")
        count += 1
        #sleep(1.0)

if __name__ == "__main__":
    main()
