import socket
import json
import time
import threading
import tkinter as tk
from tkinter import ttk

# Network settings
GROUP = "239.1.1.1"
PORT = 50000

# Change these for each device
NODE_ID = "node2"
SERVICES = ["printer", "chat"]

nodes = {}
running = True


# Create UDP socket
sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
    socket.IPPROTO_UDP
)

sock.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

sock.bind(("0.0.0.0", PORT))

# Join multicast group
mreq = socket.inet_aton(GROUP) + socket.inet_aton("0.0.0.0")

sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq
)


# Send heartbeat
def send_heartbeat():
    while running:

        message = {
            "id": NODE_ID,
            "services": SERVICES,
            "time": time.time()
        }

        data = json.dumps(message).encode()

        sock.sendto(
            data,
            (GROUP, PORT)
        )

        time.sleep(2)


# Receive heartbeat
def receive_heartbeat():
    while running:

        data, address = sock.recvfrom(1024)

        message = json.loads(data.decode())

        if message["id"] != NODE_ID:

            nodes[message["id"]] = {
                "ip": address[0],
                "services": message["services"],
                "time": time.time()
            }


# Start sending and receiving
threading.Thread(
    target=send_heartbeat,
    daemon=True
).start()

threading.Thread(
    target=receive_heartbeat,
    daemon=True
).start()


# Create GUI
root = tk.Tk()
root.title("LAN Device Discovery")
root.geometry("700x400")

title = tk.Label(
    root,
    text="LAN Device Discovery Board",
    font=("Arial", 18, "bold")
)

title.pack(pady=10)


# Create table
columns = ("ID", "IP", "Services", "Status")

table = ttk.Treeview(
    root,
    columns=columns,
    show="headings"
)

for column in columns:
    table.heading(column, text=column)

table.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# Update table
def update_table():

    for item in table.get_children():
        table.delete(item)

    current_time = time.time()

    for node_id in list(nodes):

        if current_time - nodes[node_id]["time"] > 5:
            del nodes[node_id]
            continue

        table.insert(
            "",
            "end",
            values=(
                node_id,
                nodes[node_id]["ip"],
                ", ".join(nodes[node_id]["services"]),
                "ONLINE"
            )
        )

    root.after(1000, update_table)


update_table()

root.mainloop()