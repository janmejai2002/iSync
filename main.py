import os
import time
import shutil
import threading
import requests
from tkinter import Tk, StringVar, messagebox
from tkinter import ttk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket
import uuid
import qrcode
from PIL import Image, ImageTk
import pyperclip
import webbrowser
import subprocess


DEFAULT_FOLDER_NAME = 'screenshots'
def copy_to_clipboard():
    pyperclip.copy(address_label.cget("text"))  # Copy the URL from the label
    update_status("URL copied to clipboard!")

def open_in_browser():
    url = address_label.cget("text")
    webbrowser.open(url)  # Open the URL in the default browser

def get_local_ip():
    try:
        # Create a socket and connect to an external address to find the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to an external DNS server
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"Error retrieving local IP address: {e}")
        ip_address = "127.0.0.1"  # Fallback to localhost if there's an error
    finally:
        s.close()
    return ip_address
local_ip = get_local_ip()
port = 5000
flask_process = None
class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, output_folder):
        super().__init__()
        self.output_folder = output_folder
        self.screenshot_count = 0

    def on_created(self, event):
        if event.is_directory:
            return None
        if event.src_path.endswith('.png'):
            self.screenshot_count += 1

            # Add a delay to ensure the file is fully written and accessible
            time.sleep(0.5)

            try:
                unique_filename = f"{uuid.uuid4()}.png"
                destination = os.path.join(self.output_folder, unique_filename)
                shutil.copy2(event.src_path, destination)
                # print(f"Copied to: {destination}")

                self.send_screenshot_to_server(destination)

            except PermissionError as e:
                print(f"PermissionError: {e}")
            except Exception as e:
                print(f"Failed to copy: {e}")


    def send_screenshot_to_server(self, file_path):        
        url = f"http://{local_ip}:{port}/upload_image"
        with open(file_path, 'rb') as img_file:
            files = {'image': img_file}
            try:
                response = requests.post(url, files=files)
                if response.status_code == 200:
                    print(f"Screenshot sent to server: {response.json()['image_url']}")
                    
                else:
                    print(f"Failed to send screenshot to server: {response.status_code}")
            except Exception as e:
                print(f"Error sending screenshot to server: {e}")


class ScreenshotMonitor:
    def __init__(self, folder_name):
        self.folder_name = folder_name
        username_ = os.getlogin()
        self.path = fr"C:\Users\{username_}\AppData\Local\Packages\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\TempState\ScreenClip"
        self.event_handler = ScreenshotHandler(folder_name)
        self.observer = Observer()

    def start_monitoring(self):
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        self.observer.start()
        local_ip = get_local_ip()
        self.display_server_address(local_ip)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
        self.display_server_address(local_ip)

    def stop_monitoring(self):
        self.observer.stop()
        self.observer.join()


    def display_server_address(self, local_ip):
        server_address = f"http://{local_ip}:{port}/"
        address_label.config(text=server_address)
        self.generate_qr_code(server_address)

    def generate_qr_code(self, data):
        qr = qrcode.make(data)
        qr.save("qr_code.png")
        qr_image = Image.open("qr_code.png")
        qr_image = qr_image.resize((150, 150), Image.LANCZOS)
        qr_image = ImageTk.PhotoImage(qr_image)

        qr_code_label.config(image=qr_image)
        qr_code_label.image = qr_image  # K


monitoring_active = False

def start_monitoring():
    global monitoring_active, monitor, flask_process
    folder_name = folder_name_var.get()
    
    if monitoring_active:
        # Stop monitoring
        monitor.stop_monitoring()
        if flask_process:
            flask_process.kill()
            flask_process = None

        start_button.config(text="Start")  # Change text back to Start
        update_status("Monitoring Stopped")
        copy_button.pack_forget()  # Hide buttons when stopping
        open_button.pack_forget()
        monitoring_active = False  # Update monitoring state


    else:
        # Check if folder name is valid
        if not folder_name:
            messagebox.showerror("Error", "Please enter a folder name.")
            return

        # Create the output folder if it doesn't exist
        output_folder = os.path.join(os.getcwd(), folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # Start monitoring in a separate thread
        
        monitor = ScreenshotMonitor(output_folder)
        monitoring_thread = threading.Thread(target=monitor.start_monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()

        flask_process=subprocess.Popen(['python', 'app.py'],
                                        creationflags=subprocess.CREATE_NO_WINDOW,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        
        start_button.config(text="Stop")  # Change text to Stop
        update_status("Monitoring Started")
        monitoring_active = True  # Update monitoring state
        copy_button.pack(pady=(5, 5))
        open_button.pack(pady=(5, 20))

def on_closing():
    if monitoring_active:
        monitor.stop_monitoring()
        if flask_process:
            flask_process.kill()
    root.destroy()

def stop_monitoring():
    monitor.stop_monitoring()
    start_button.config(state="normal")
    start_button.config(text="Start")  # Change text back to Start
    update_status("Monitoring Stopped")

# Update status label function
def update_status(message):
    status_label.config(text=message)

# GUI Setup
root = Tk()
root.title("InstaSync")
root.geometry("550x550")
root.configure(bg="#2E2E2E")
root.protocol("WM_DELETE_WINDOW", on_closing)
# Style Configuration
style = ttk.Style()
style.configure("TLabel", background="#2E2E2E", foreground="#FFFFFF", font=("Helvetica", 22))
style.configure("TEntry", fieldbackground="#3E3E3E", foreground="#000000", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12))

# Button Style Configuration
style.map("TButton", 
          background=[('!disabled', '#4B4B4B'), ('disabled', '#888888'), ('active', '#6BBE45')],
          foreground=[('!disabled', '#000000'), ('disabled', '#000000'), ('active', '#FFFFFF')])

folder_name_var = StringVar(value=DEFAULT_FOLDER_NAME)

label = ttk.Label(root, text="Folder Name:")
label.pack(pady=(20, 5))

entry = ttk.Entry(root, textvariable=folder_name_var, width=30)
entry.pack(pady=(0, 15))

# Add label to display server address
address_label = ttk.Label(root, text="", font=("Helvetica", 12))
address_label.pack(pady=(5, 10))
# Button to copy URL to clipboard
# Button to copy URL to clipboard
copy_button = ttk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
# Keep the button hidden initially
copy_button.pack_forget()

# Button to open URL in the default browser
open_button = ttk.Button(root, text="Open in Browser", command=open_in_browser)
# Keep the button hidden initially
open_button.pack_forget()

# Add label for QR code
qr_code_label = ttk.Label(root)
qr_code_label.pack(pady=(10, 20))

start_button = ttk.Button(root, text="Start", command=start_monitoring)
start_button.pack(pady=(0, 5))

# Status Label
status_label = ttk.Label(root, text="", background="#2E2E2E", foreground="#FFFFFF", font=("Helvetica", 16))
status_label.pack(pady=(20, 5))




default_folder_path = os.path.join(os.getcwd(), DEFAULT_FOLDER_NAME)

root.mainloop()
