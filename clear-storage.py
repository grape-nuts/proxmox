import sys
import getopt
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
        opts, args = getopt.getopt(sys.argv[1:], "h:s:d:", ["host=", "source=", "destination="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    host = None
    source = None
    destination = None
    for opt, arg in opts:
        if (opt in ("-h", "--host")):
            host = arg
        elif (opt in ("-s", "--source")):
            source = arg
        elif (opt in ("-d", "--destination")):
            destination = arg
        else:
            assert False, "Unhandled option"

    if (host == None):
        print("Host is required")
        sys.exit(2)

    if (source == None):
        print("Source datastore is required")
        sys.exit(2)

    if (destination == None):
        print("Destination datastore is required")
        sys.exit(2)

    node = host.split(".", 1)[0]
    vmid = []
    vmNode = []

    username = input("user@realm: ")
    passw = getpass()

    try:
        prox = ProxmoxAPI(host, user=username, password=passw)
    except:
        print("Error connecting to proxmox host " + host + " as user " + username)
        sys.exit()

    #if (source != exist):
        #exit gracefully

    #if (destination != exist):
        #exit gracefully
        
    # Get the list of vmids that have a disk image on the source datastore
    for image in prox.nodes(node).storage(source).content.get():
        vmid.append("{0}".format(image['vmid']))

    # TODO: check for snapshots on any of the vmids, and stop if one is found

    # Remove duplicates from the list and sort
    vmid = [*set(vmid)]
    vmid.sort()

    # Get the node that each vmid belongs to
    for vm in prox.cluster.resources.get(type="vm"):
        for id in vmid:
            if (id == str(vm['vmid'])):
                vmNode.append("{0}".format(vm['node']))

    # Loop through the vmids, get their config from the corresponding node, get the list of disks from the config,
    # and if the disk is on the source datastore, move it to the destination datastore
    count = 0
    for vm in vmid:
        config = prox.nodes(vmNode[count]).qemu(vm).config.get()
        disks = []
        for i in range(0, 30):
            scsiStr = 'scsi' + str(i)
            if (scsiStr in config):
                disks.append(["{0}".format(config[scsiStr]), scsiStr])
        for disk in disks:
            diskStorageID = disk[0].split(":", 1)[0]
            if (diskStorageID == source):
                print("Moving " + disk[0] + " for VM " + vm + " to " + destination + "... ", end="", flush=True)
                taskid = prox.nodes(vmNode[count]).qemu(vm).move_disk.post(disk=disk[1], storage=destination, delete=1)
                # We have to wait for each task to complete, otherwise vmids with multiple disks being moved will fail
                await_task(prox, taskid, vmNode[count])
                print("complete!")
        count += 1
        #sleep(1.0)

if __name__ == "__main__":
    main()