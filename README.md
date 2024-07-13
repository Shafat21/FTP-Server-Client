# FTP Client and Server with Tkinter GUI

This project implements an FTP client and server using Python's `socket` and `tkinter` libraries. The client allows users to connect to the server, upload, download, and delete files, while the server handles these requests and manages the file storage.

## Prerequisites

- Python 3.x
- Tkinter (comes pre-installed with Python)
- Azure theme for Tkinter (optional, can be downloaded from [Azure Theme GitHub](https://github.com/rdbende/Azure-ttk-theme))

## Directory Structure

```
FTP/
│
├── client.py
├── server.py
└── serverdata/
    └── (files)
```

- `client.py`: Contains the client-side code.
- `server.py`: Contains the server-side code.
- `serverdata/`: Directory where the server stores the files.

## Usage

### Running the Server

1. Open Split Terminal.
2. Run the server script:
    ```bash
    python server.py
    ```

### Running the Client

1. Open Split Terminal.
2. Run the client script:
    ```bash
    python client.py
    ```
