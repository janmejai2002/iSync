# InstaSync

InstaSync is a powerful and user-friendly screenshot synchronization tool designed to seamlessly share your screenshots across multiple devices.
This application captures your screenshots and uploads them to a local Flask server, allowing easy access from any device connected to the same network.
Whether you want to share important information, keep a visual record, or sync your screenshots across devices, InstaSync has you covered.

## Features

- **Automatic Screenshot Upload**: Automatically uploads screenshots to the server whenever you take one.
- **User-Friendly GUI**: Intuitive interface for managing your screenshot folder and server settings.
- **Real-Time Access**: Access your screenshots in real-time from any device via the provided local URL.
- **Clipboard Integration**: Copy the upload URL directly to your clipboard for easy access.
- **QR Code** : Scan the QR code generate for your local URL on any device instantly.

## Requirements

Make sure you have the following software installed:

- Python 3.11 or higher
- [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

## Installation

1. **Clone the Repository**:

```
   git clone <repository-url>
   cd InstaSync
```
2. **Create a New Conda Environment**:

```
conda create --name isync python=3.11
conda activate isync
```

3. **Install Required Packages:**
   
```
Use the requirements.txt file to install the necessary packages:
pip install -r requirements.txt
```

4. **Run the Application**:

Start the GUI application with the following command:
```
python main.py
```

5. **Start the Flask Server**:

The Flask server will automatically start when you press the "Start" button in the GUI.


6. **Take a screenshot**
```
Win+Shift+S
```
