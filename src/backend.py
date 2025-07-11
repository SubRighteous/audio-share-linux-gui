import subprocess
import socket
import re
import os
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QThread


def string_to_bool(s):
    s_lower = s.lower()
    if s_lower in ('true', 'True', '1'):
        return True
    elif s_lower in ('false', 'False', '0'):
        return False
    else:
        # Handle cases where the string doesn't match expected "true" or "false" values
        # You might raise an error, return None, or return bool(s) as a fallback
        raise ValueError(f"Cannot convert '{s}' to a boolean.")

# Gets Information from 'as-cmd'
class AudioShare():
    def getEndpointList(self):

        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Get the list of device endpoints
        command = [f'{current_dir}/as-cmd' , "-l"]

        _stop_requested = False
        _process = subprocess.run(
            command,
            capture_output=True, 
            text=True
        )
        output = _process.stdout
        
        endpoints = []
        print(output)
        for line in output.splitlines():
            print(line)
            match = re.search(r'(\*?)\s*id:\s*(\d+)\s+name:\s*(.+)', line)
            if match:
                is_active = match.group(1) == "*"
                endpoint_id = int(match.group(2))
                endpoint_name = match.group(3).strip()
                endpoints.append({
                    'id': endpoint_id,
                    'name': endpoint_name,
                    'active': is_active
                })

        return endpoints

    def get_endpoint_id_from_name(self, name):
        endpoint_list = self.getEndpointList()
        endpoint_id = None
        print(endpoint_list)
        for ep in endpoint_list:
            print(ep['name'])
            if name == ep['name']:
                endpoint_id = ep['id']

        return endpoint_id
        
    
    def getEncodingList(self):

        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Get the list of encoding
        command = [current_dir + "/as-cmd" , "--list-encoding"]

        _stop_requested = False
        _process = subprocess.run(
            command,
            capture_output=True, 
            text=True
        )
        output = _process.stdout
        
        encoding = []

        for line in output.splitlines():
            match = re.search(r'^\s*(\w+)\s{2,}(.*)$', line)
            if match:
                encoding_key = match.group(1)
                description = match.group(2)
                encoding.append({
                    'key': encoding_key,
                    'description' : description
                })
        
        return encoding

    def get_local_ipv4_address(self):
        """
        Retrieves the local IPv4 address of the machine.
        """
        try:
            # Connect to an external address; doesn't have to succeed
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # Doesn't actually send data; just used to get the right interface
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
            return ip_address
        except socket.error as e:
            print(f"Error getting IP address: {e}")
            return None

    


class ServerThread(QThread):
    logOutput = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, command: list[str]):
        super().__init__()
        self.command = command
        self._process = None
        self._stop_requested = False

    def run(self):
        try:
            self._stop_requested = False
            print(self.command)
            self._process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in self._process.stdout:
                if self._stop_requested:
                    break
                self.logOutput.emit(line.strip())

            self._process.wait()

        except Exception as e:
            self.logOutput.emit(f"[Error] {e}")
        finally:
            if self._process and self._process.poll() is None:
                self._process.terminate()
            self._process = None
            self.finished.emit()

    def stop(self):
        self._stop_requested = True
        if self._process and self._process.poll() is None:
            self._process.terminate()


class Backend(QObject):
    ServerRunning = False

    serverThread = None

    serverAddress = None
    serverPort = None

    audio_endpoint_id = None
    audio_endpoint_name = None
    audio_encoding = None

    def __init__(self , config_file , config_file_dir):
        super().__init__()
        self.config_settings = config_file
        self.config_file_dir = config_file_dir

        if config_file is not None:
            self.setEncoding(config_file['Server Settings']['encoding'])
            
            self.setServerIp(config_file['Server Settings']['serverip'])
            self.setServerPort(config_file['Server Settings']['serverport'])

            self.audio_endpoint_name = config_file['Server Settings']['endpoint_name']

            if AudioShare().get_endpoint_id_from_name(self.audio_endpoint_name) == config_file['Server Settings']['endpoint']:
                self.setEndpoint(config_file['Server Settings']['endpoint'])
            else:
                print(self.audio_endpoint_name)
                print(AudioShare().get_endpoint_id_from_name(self.audio_endpoint_name))
                self.setEndpoint(AudioShare().get_endpoint_id_from_name(self.audio_endpoint_name))
            
            
    @pyqtSlot(result='QVariant')
    def getEndpointList(self):

        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Get the list of device endpoints
        command = [current_dir + "/as-cmd" , "-l"]

        _stop_requested = False
        _process = subprocess.run(
            command,
            capture_output=True, 
            text=True
        )
        output = _process.stdout
        
        endpoints = []

        for line in output.splitlines():
            match = re.search(r'(\*?)\s*id:\s*(\d+)\s+name:\s*(.+)', line)
            if match:
                is_active = match.group(1) == "*"
                endpoint_id = int(match.group(2))
                endpoint_name = match.group(3).strip()
                endpoints.append({
                    'id': endpoint_id,
                    'name': endpoint_name,
                    'active': is_active
                })

        return endpoints

    @pyqtSlot(result='QVariant')
    def getEncodingList(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Get the list of encoding
        command = [current_dir + "/as-cmd" , "--list-encoding"]

        _stop_requested = False
        _process = subprocess.run(
            command,
            capture_output=True, 
            text=True
        )
        output = _process.stdout
        
        encoding = []

        for line in output.splitlines():
            match = re.search(r'^\s*(\w+)\s{2,}(.*)$', line)
            if match:
                encoding_key = match.group(1)
                description = match.group(2)
                encoding.append({
                    'key': encoding_key,
                    'description' : description
                })
        
        return encoding

    def is_endpoint_exist(self, target_endpoint):
        
        for d in self.getEndpointList():
            
            if target_endpoint == d['id']:
                return True
            
        return False

    def is_encoding_supported(self, target_encoding):
        
        for encode in self.getEncodingList():
            if target_encoding == encode['key']:
                return True
        return False

    serverStatusChanged = pyqtSignal(bool)
    serverlogOutput = pyqtSignal(str)

    @pyqtSlot(result='QVariant')
    def get_local_ipv4_address(self):
        """
        Retrieves the local IPv4 address of the machine.
        """
        try:
            return AudioShare().get_local_ipv4_address()
        except socket.error as e:
            print(f"Error getting IP address: {e}")
            return None

    @pyqtSlot(result='QVariant')
    def getServerAddress(self):
        # If we don't have a set server address from the config file then default to the system local ipv4
        if self.serverAddress is None:
            return self.get_local_ipv4_address()
        else:
            return self.serverAddress

    @pyqtSlot(int)
    def setEndpoint(self, endpoint_id):
        print("Setting Endpoint to " + str(endpoint_id))
        
        self.audio_endpoint_id = int(endpoint_id)

    @pyqtSlot(result=int)
    def getEndpoint(self):
        return int(self.audio_endpoint_id)

    @pyqtSlot(str)
    def setEncoding(self, encode_key):
        print("Setting Encoding to " + str(encode_key))
        self.audio_encoding = str(encode_key)

    @pyqtSlot(str)
    def setEncodingName(self, encoding_name):
        print("Setting Encoding Name to " + str(encoding_name))
        self.audio_endpoint_name = str(encoding_name)

    @pyqtSlot(result=str)
    def getEncoding(self):
        return str(self.audio_encoding)

    @pyqtSlot(str, result=str)
    def setServerIp(self, serverIp):
        print("Server Ip: " + str(serverIp))
        self.serverAddress = serverIp

    @pyqtSlot(str, result=str)
    def setServerPort(self, serverPort):
        print("Server Port: " + str(serverPort))
        self.serverPort = serverPort

    # Stops and restarts the server
    @pyqtSlot()
    def resetServer(self):
        if self.ServerRunning:
            self.cleanup()
            self.toggleServer()
    
    @pyqtSlot()
    def toggleServer(self):
        if self.ServerRunning is False:
            print("Starting the server")
            self.setServerRunning(True)
            
            # Example command for starting the server "./as-cmd --bind=192.168.1.77:39999"
            if self.serverAddress is None or self.serverPort is None:
                self.serverThread = ServerThread(["./as-cmd", "--bind"])
            else:
                
                if self.is_endpoint_exist(self.audio_endpoint_id) is False and self.is_encoding_supported(self.audio_encoding) is False:
                    if len(str(self.serverAddress)) == 0 and len(str(self.serverPort)) > 0:
                        self.serverThread = ServerThread(["./as-cmd", "--bind=" + str(self.get_local_ipv4_address()) + ":" + str(self.serverPort)])
                    elif len(str(self.serverAddress)) > 0 and len(str(self.serverPort)) == 0:
                            self.serverThread = ServerThread(["./as-cmd", "--bind=" + str(self.serverAddress)])
                    elif len(str(self.serverAddress)) == 0 and len(str(self.serverPort)) == 0:
                        self.serverThread = ServerThread(["./as-cmd", "--bind"])
                    else:
                        self.serverThread = ServerThread(["./as-cmd", "--bind=" + str(self.serverAddress) + ":" + str(self.serverPort)])
                else:
                    #self.serverThread = ServerThread(["./as-cmd" , "-b", "-e" , str(self.audio_endpoint_id)])
                    if len(str(self.serverAddress)) == 0 and len(str(self.serverPort)) > 0:
                        self.serverThread = ServerThread(["./as-cmd" , "--bind=" + str(self.get_local_ipv4_address()) + ":" + str(self.serverPort) , "-e" , str(self.audio_endpoint_id) , '--encoding' , str(self.audio_encoding)])
                    elif len(str(self.serverAddress)) > 0 and len(str(self.serverPort)) == 0:
                        self.serverThread = ServerThread(["./as-cmd", "--bind=" + str(self.serverAddress)] , "-e" , str(self.audio_endpoint_id) , '--encoding' , str(self.audio_encoding))
                    elif len(str(self.serverAddress)) == 0 and len(str(self.serverPort)) == 0:
                        self.serverThread = ServerThread(["./as-cmd", "--bind" , "-e" , str(self.audio_endpoint_id) , '--encoding' , str(self.audio_encoding)])
                    else:
                        self.serverThread = ServerThread(["./as-cmd", "--bind=" + str(self.serverAddress) + ":" + str(self.serverPort) , "-e" , str(self.audio_endpoint_id) , '--encoding' , str(self.audio_encoding)])
            
            #self.serverThread.logOutput.connect(lambda msg: print("LOG:", msg))
            #self.serverThread.finished.connect(lambda: print("Server thread finished"))

            self.serverThread.logOutput.connect(lambda msg: self.serverlogOutput.emit(msg))
            self.serverThread.finished.connect(lambda: self.serverlogOutput.emit("Server Closed"))

            self.serverThread.start()

            self.saveSettings()
            
        else:
            print("Closing the server")
            self.setServerRunning(False)
            self.serverThread.stop()
            self.serverThread.wait()  # Wait for clean shutdown
            

    def cleanup(self):
        
        # We don't need to save every time, just when the value is different
        if self.config_settings['App Settings']['server_laststate'] == str(self.ServerRunning):
            pass
        else:
            # Save wether the server was running or not
            print("Saving server state to config.ini")
            with open(os.path.join(self.config_file_dir ,'config.ini'), 'w') as config_file:
                self.config_settings.set('App Settings', 'server_laststate' , str(self.ServerRunning))

                self.config_settings.write(config_file)

        if self.serverThread is not None:

            print("Closing the server")
            self.setServerRunning(False)
            self.serverThread.stop()
            self.serverThread.wait()  # Wait for clean shutdown

    @pyqtProperty(bool, notify=serverStatusChanged)
    def isServerRunning(self):
        return self.ServerRunning

    def setServerRunning(self, status: bool):
        if self.ServerRunning != status:
            self.ServerRunning = status
            self.serverStatusChanged.emit(status)

    @pyqtSlot()
    def PageIsDoneLoading(self):
        if string_to_bool(self.config_settings['App Settings']['autostart']) is True:
            self.toggleServer()
        elif string_to_bool(self.config_settings['App Settings']['keeplaststate']) is True:
            if string_to_bool(self.config_settings['App Settings']['server_laststate']) is True:
                self.toggleServer()
            else:
                pass

    @pyqtSlot()
    def saveSettings(self):
        if self.config_settings['Server Settings']['serverip'] == str(self.serverAddress) and self.config_settings['Server Settings']['serverport'] == str(self.serverPort) and self.config_settings['Server Settings']['endpoint'] == str(self.audio_endpoint_id) and self.config_settings['Server Settings']['encoding'] == str(self.audio_encoding) and self.config_settings['Server Settings']['endpoint_name'] == str(self.audio_endpoint_name):
            return

        print("Saving settings to config.ini")
        with open(os.path.join(self.config_file_dir ,'config.ini'), 'w') as config_file:
            self.config_settings.set('Server Settings' , 'serverip' , str(self.serverAddress))
            self.config_settings.set('Server Settings', 'serverport' , str(self.serverPort))
            self.config_settings.set('Server Settings', 'endpoint' , str(self.audio_endpoint_id))
            self.config_settings.set('Server Settings', 'endpoint_name', f'{str(self.audio_endpoint_name)}')
            self.config_settings.set('Server Settings', 'encoding' , str(self.audio_encoding))

            self.config_settings.write(config_file)

class ApplcationSettings():
    MinimizeToTray = False
    AutoStart = False
    KeepLastState = False

    def __init__(self):
        super().__init__()

class SettingsBackend(QObject):

    settings = ApplcationSettings()

    def __init__(self , config_file , config_file_dir):
        super().__init__()
        self.config_settings = config_file
        self.config_file_dir = config_file_dir
        if config_file is not None:
            self.setAutoStart(config_file['App Settings']['autostart'])
            self.setMinimizeToTray(config_file['App Settings']['minimizetotray'])
            self.setKeepLastState(config_file['App Settings']['keeplaststate'])
            
        
    @pyqtSlot(bool)
    def setAutoStart(self, state : bool):
        self.settings.AutoStart = state
        print("AutoStart set " + str(self.settings.AutoStart))

    @pyqtSlot(bool)
    def setMinimizeToTray(self, state : bool):
        self.settings.MinimizeToTray = state
        print("MinimizeToTray set " + str(self.settings.MinimizeToTray))
        self.saveSettings()
    
    @pyqtSlot(bool)
    def setKeepLastState(self, state : bool):
        self.settings.KeepLastState = state
        print("KeepLastState set " + str(self.settings.KeepLastState))

    @pyqtSlot(result=bool)
    def getAutoStart(self):
        return string_to_bool(self.settings.AutoStart)

    @pyqtSlot(result=bool)
    def getMinimizeToTray(self):
        return string_to_bool(self.settings.MinimizeToTray)

    @pyqtSlot(result=bool)
    def getKeepLastState(self):
        return string_to_bool(self.settings.KeepLastState)

    @pyqtSlot()
    def saveSettings(self):
        if self.config_settings['App Settings']['autostart'] == str(self.settings.AutoStart) and self.config_settings['App Settings']['keeplaststate'] == str(self.settings.KeepLastState) and self.config_settings['App Settings']['minimizetotray'] == str(self.settings.MinimizeToTray):
            return

        print("Saving settings to config.ini")
        with open(os.path.join(self.config_file_dir ,'config.ini'), 'w') as config_file:

            self.config_settings.set('App Settings', 'autostart' , str(self.settings.AutoStart))
            self.config_settings.set('App Settings', 'keeplaststate' , str(self.settings.KeepLastState))
            self.config_settings.set('App Settings', 'minimizetotray' , str(self.settings.MinimizeToTray))

            self.config_settings.write(config_file)
