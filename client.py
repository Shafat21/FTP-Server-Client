import socket
import threading
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk

class FTPClient:
    def __init__(self, master):
        self.master = master
        self.master.title("FTP Client")
        self.master.geometry("600x500")

        # Load the Forest theme
        self.master.tk.call('source', 'forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')

        # First Row: IP and Port
        self.ip_label = ttk.Label(self.master, text="Server IP:")
        self.ip_label.grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = ttk.Entry(self.master)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.port_label = ttk.Label(self.master, text="Port:")
        self.port_label.grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = ttk.Entry(self.master)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Second Row: Connect and Disconnect buttons
        self.connect_button = ttk.Button(self.master, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=1, column=0, columnspan=2, pady=10, sticky=EW)
        
        self.disconnect_button = ttk.Button(self.master, text="Disconnect", command=self.disconnect_from_server, state=DISABLED)
        self.disconnect_button.grid(row=1, column=2, columnspan=2, pady=10, sticky=EW)

        # Third Row: Files List and Upload button
        self.files_frame = ttk.Frame(self.master)
        self.files_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        self.files_label = ttk.Label(self.files_frame, text="Files:")
        self.files_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_list = ttk.Frame(self.files_frame)
        self.file_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.upload_button = ttk.Button(self.files_frame, text="Upload File", command=self.browse_file)
        self.upload_button.grid(row=2, column=0, pady=10, sticky=EW)

        # Fourth Row: Log Area
        self.log_frame = ttk.Frame(self.master)
        self.log_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.log_label = ttk.Label(self.log_frame, text="Log:")
        self.log_label.grid(row=0, column=0, padx=5, pady=5)

        self.log_text = Text(self.log_frame, height=10, width=70)
        self.log_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Make the GUI responsive
        for i in range(4):
            self.master.columnconfigure(i, weight=1)
        self.master.rowconfigure(2, weight=1)
        self.master.rowconfigure(3, weight=1)

        self.files_frame.columnconfigure(0, weight=1)
        self.files_frame.rowconfigure(1, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(1, weight=1)

        self.client_socket = None

    def toggle_connection(self):
        if self.connect_button.config('text')[-1] == 'Connect':
            self.connect_to_server()
        else:
            self.disconnect_from_server()

    def connect_to_server(self):
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.log_text.insert(END, f"Connected to server at {ip}:{port}\n")
            self.connect_button.config(text="Disconnect", state=NORMAL)
            self.disconnect_button.config(state=DISABLED)
            self.update_file_list()
            self.auto_refresh()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def disconnect_from_server(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.log_text.insert(END, "Disconnected from server\n")
            self.connect_button.config(text="Connect", state=NORMAL)
            self.disconnect_button.config(state=DISABLED)
        for widget in self.file_list.winfo_children():
            widget.destroy()

    def auto_refresh(self):
        if self.client_socket:
            self.update_file_list()
            self.master.after(5000, self.auto_refresh)

    def update_file_list(self):
        def task():
            for widget in self.file_list.winfo_children():
                widget.destroy()
            try:
                self.client_socket.sendall(b'LIST')
                files_data = self.client_socket.recv(4096).decode()
                files = files_data.split('\n')
                for file in files:
                    if file:
                        self.add_file_row(file)
            except Exception as e:
                self.log_text.insert(END, f"Error updating file list: {e}\n")
        threading.Thread(target=task).start()

    def add_file_row(self, filename):
        row_frame = ttk.Frame(self.file_list)
        row_frame.pack(fill="x", pady=2)

        file_label = ttk.Label(row_frame, text=filename, anchor="w")
        file_label.pack(side="left", padx=10)

        download_button = ttk.Button(row_frame, text="Download", command=lambda: self.download_file(filename))
        download_button.pack(side="right", padx=5)

        delete_button = ttk.Button(row_frame, text="Delete", command=lambda: self.delete_file(filename))
        delete_button.pack(side="right", padx=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_file(file_path)

    def upload_file(self, file_path):
        def task():
            if file_path:
                file_name = os.path.basename(file_path)
                try:
                    self.client_socket.sendall(f"UPLOAD {file_name}".encode('utf-8'))
                    with open(file_path, 'rb') as f:
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            self.client_socket.sendall(data)
                    self.client_socket.sendall(b'')
                    response = self.client_socket.recv(1024).decode('utf-8')
                    if response == 'OK':
                        self.log_text.insert(END, f"Upload Successful: {file_name}\n")
                    else:
                        self.log_text.insert(END, f"Upload Failed: {file_name}\n")
                    self.update_file_list()
                except Exception as e:
                    self.log_text.insert(END, f"Network Error: Failed to upload file: {e}\n")
        threading.Thread(target=task).start()

    def download_file(self, filename):
        def task():
            try:
                self.client_socket.sendall(f"GET {filename}".encode('utf-8'))
                response = self.client_socket.recv(1024).decode('utf-8')
                if response == 'OK':
                    file_extension = os.path.splitext(filename)[1]
                    file_types = [(f"{file_extension} files", f"*{file_extension}"), ("All files", "*.*")]
                    save_path = filedialog.asksaveasfilename(defaultextension=file_extension, filetypes=file_types, initialfile=filename)
                    if save_path:
                        with open(save_path, 'wb') as f:
                            while True:
                                data = self.client_socket.recv(1024)
                                if not data:
                                    break
                                f.write(data)
                        self.log_text.insert(END, f"Download Successful: {filename}\n")
                    self.update_file_list()
                else:
                    self.log_text.insert(END, "Download Failed: Could not download the file\n")
            except Exception as e:
                self.log_text.insert(END, f"Network Error: Failed to download file: {e}\n")
        threading.Thread(target=task).start()

    def delete_file(self, filename):
        def task():
            try:
                self.client_socket.sendall(f"DEL {filename}".encode('utf-8'))
                response = self.client_socket.recv(1024)
                if response == b'OK':
                    self.log_text.insert(END, f"Delete Successful: {filename}\n")
                    self.update_file_list()
                else:
                    self.log_text.insert(END, "Delete Failed: Could not delete the file\n")
            except Exception as e:
                self.log_text.insert(END, f"Network Error: Failed to delete file: {e}\n")
        threading.Thread(target=task).start()

root = ThemedTk(theme="forest-dark")
app = FTPClient(root)
root.mainloop()
