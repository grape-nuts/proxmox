# proxmox
A set of proxmox scripts to simplify and automate repetitive tasks.

clear-storage.py: performs a storage migration to move all VM disks from one datastore to another.

clear-vms.py: performs a live migration to clear a host of all running VMs. Attempts to migrate to targets based on CPU or memory availability

record-vms.py: records the current location of all VMs to a yaml file

move-vms.py: reads a yaml file and live migrates VMs to match the locations in the file

get-snapshots.py: Looks through all VMs and outputs any snapshots associated with them
