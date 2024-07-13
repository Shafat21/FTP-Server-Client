import os
import socket
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

def handle_client(conn, addr, log_area, info_label, client_addresses, file_list):
    client_addresses.append(addr)
    info_label.config(text=f"{len(client_addresses)}")
    log_area.insert(END, f"[NEW CONNECTION]: {addr} connected\n")
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            command, _, param = data.partition(' ')
            
            if command == 'LIST':
                files = '\n'.join(os.listdir('serverdata'))
                conn.sendall(files.encode('utf-8'))
            elif command == 'GET':
                file_path = os.path.join('serverdata', param)
                if os.path.isfile(file_path):
                    conn.sendall(b'OK')
                    with open(file_path, 'rb') as file:
                        while True:
                            bytes_read = file.read(1024)
                            if not bytes_read:
                                break
                            conn.sendall(bytes_read)
                    log_area.insert(END, f"Sent {param} to {addr}\n")
                else:
                    conn.sendall(b'ERROR')
            elif command == 'UPLOAD':
                file_path = os.path.join('serverdata', param)
                with open(file_path, 'wb') as f:
                    while True:
                        bytes_read = conn.recv(1024)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                log_area.insert(END, f"Received {param} from {addr}\n")
                conn.sendall(b'OK')  # Send confirmation after upload
                update_file_list(file_list)
            elif command == 'DEL':
                file_path = os.path.join('serverdata', param)
                try:
                    os.remove(file_path)
                    conn.sendall(b'OK')
                    log_area.insert(END, f"Deleted {param}\n")
                    update_file_list(file_list)
                except FileNotFoundError:
                    conn.sendall(b'ERROR')
                except Exception as e:
                    log_area.insert(END, f"Failed to delete {param}: {e}\n")
                    conn.sendall(b'ERROR')
    finally:
        client_addresses.remove(addr)
        info_label.config(text=f"Connected Devices: {len(client_addresses)}")
        log_area.insert(END, f"[DISCONNECTED]: {addr}\n")
        conn.close()

def start_server(ip, port, log_area, info_label, client_addresses, file_list):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((ip, int(port)))
        server_socket.listen(5)
        log_area.insert(END, f"[STARTING]: Server is starting\n")
        log_area.insert(END, f"[LISTENING]: Server is listening on {ip} : {port}\n")
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr, log_area, info_label, client_addresses, file_list))
            thread.start()
    except socket.error as e:
        log_area.insert(END, f"[ERROR]: {e}\n")
    finally:
        server_socket.close()

def update_file_list(file_list):
    files = os.listdir('serverdata')
    for widget in file_list.winfo_children():
        widget.destroy()
    for file in files:
        file_frame = ttk.Frame(file_list)
        file_frame.pack(fill=X, padx=5, pady=2)
        file_label = ttk.Label(file_frame, text=file, anchor="w")
        file_label.pack(side=LEFT, fill=X, expand=True)
        delete_button = ttk.Button(file_frame, text="Delete", command=lambda f=file: delete_file(f, file_list))
        delete_button.pack(side=RIGHT)

def delete_file(filename, file_list):
    os.remove(os.path.join('serverdata', filename))
    update_file_list(file_list)

client_addresses = []

def create_server_gui():
    root = Tk()
    root.title("FTP Server")
    root.geometry("600x400")

    # Apply Azure theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    # Add style to the widgets
    style = ttk.Style()
    style.configure('TLabel', background='#333', foreground='#FFF')
    style.configure('TButton', background='#555', foreground='#FFF')
    style.configure('TEntry', background='#555', foreground='#FFF')

    ttk.Label(root, text="IP Address:").pack(pady=(10,0))
    ip_entry = ttk.Entry(root)
    ip_entry.pack()

    ttk.Label(root, text="Port:").pack(pady=(10,0))
    port_entry = ttk.Entry(root)
    port_entry.pack()

    def start_server_thread():
        ip = ip_entry.get()
        port = port_entry.get()
        try:
            socket.inet_aton(ip)  # Validate IP
            if not (0 <= int(port) <= 65535):  # Validate Port
                raise ValueError("Port number out of range")
            threading.Thread(target=start_server, args=(ip, port, log_area, info_label, client_addresses, file_list)).start()
        except socket.error:
            log_area.insert(END, "[ERROR]: Invalid IP address\n")
        except ValueError as ve:
            log_area.insert(END, f"[ERROR]: {ve}\n")

    start_button = ttk.Button(root, text="Start Server", style="Toggle.TButton", command=start_server_thread)
    start_button.pack(pady=10)

    stop_button = ttk.Button(root, text="Stop Server", style="Toggle.TButton", command=root.quit)
    stop_button.pack(pady=10)

    info_label = ttk.Label(root, text="Connected Devices: 0")
    info_label.pack()

    file_list = ttk.Frame(root)
    file_list.pack(fill=BOTH, expand=True, padx=10, pady=10)

    log_area = ScrolledText(root, height=10, bg="#333", fg="#FFF")
    log_area.pack(fill=BOTH, expand=True)

    root.mainloop()
    
create_server_gui()
