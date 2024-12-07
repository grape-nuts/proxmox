from time import sleep

def await_task(proxmox_api, taskid, node):
    data = {"status": ""}
    while data['status'] != "stopped":
        sleep(1.0) # Looping with no governor causes RemoteDisconnected() errors
        data = proxmox_api.nodes(node).tasks(taskid).status.get()
    return data
