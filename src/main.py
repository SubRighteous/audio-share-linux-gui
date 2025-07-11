import sys
from configparser import ConfigParser

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget , QSystemTrayIcon , QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl , QSharedMemory
from PyQt6.QtGui import QIcon , QAction
import os
from pathlib import Path
from backend import Backend, SettingsBackend , AudioShare , string_to_bool

config_settings = None
secondary_window = None

def get_user_config_path() -> Path:
    config_dir = Path.home() / ".config" / 'audio-share-py'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

# Creates a new Config File with default values
def create_new_config_file():
    
    with open(os.path.join(get_user_config_path() , 'config.ini'), 'w') as configfile:
        Endpoints = AudioShare().getEndpointList()
        Encoding = AudioShare().getEncodingList()
        print(Endpoints)
        print(Encoding)
        config_settings['Server Settings'] = {'serverIP' : f'{AudioShare().get_local_ipv4_address()}', 'serverPort' : '65530' , 'endpoint' : f'{Endpoints[0]['id']}' , 'endpoint_name': f'{Endpoints[0]['name']}', 'encoding' : f'{Encoding[0]['key']}'}
        config_settings['App Settings'] = {'AutoStart' : 'False','KeepLastState' : 'False', 'MinimizeToTray' : 'False' , 'server_laststate' : False}

        # Save in-memory config to ini file
        config_settings.write(configfile)

class LoggingWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"[JS:{level.name}] {message} (line {lineNumber}, source: {sourceID})")


class WebTab(QWebEngineView):
    def __init__(self, backend, html_path):
        super().__init__()
        self.backend = backend

        # Set custom page with JS logging
        self.setPage(LoggingWebEnginePage(self))

        # WebChannel setup
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)
        self.page().setWebChannel(self.channel)

        # Load local HTML file
        self.load(QUrl.fromLocalFile(html_path))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Share Server")
        self.resize(1000, 700)
        # Create a ConfigParser object
        global config_settings
        config_settings = ConfigParser()

        current_dir = os.path.dirname(os.path.abspath(__file__))

        config_file_path = os.path.join(get_user_config_path(), 'config.ini') 

        if os.path.exists(config_file_path):
            config_settings.read(config_file_path)
            print(f"Configuration file '{config_file_path}' found and loaded.")
            # You can now access sections and options from 'config_settings'

            try:
                config_settings['Server Settings']
                config_settings['App Settings']
            except KeyError:
                # Handle the case where the file doesn't have the basic keys
                # Remake the file
                create_new_config_file()

        else:
            # Default Config Creation

            print(f"Configuration file '{config_file_path}' not found.")

            # Handle the case where the file doesn't exist, e.g., create a default one
            create_new_config_file()

        self.backend = Backend(config_settings , get_user_config_path())

        self.settings_backend = SettingsBackend(config_settings , get_user_config_path())
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        index_file = os.path.join(current_dir, "frontend", "index.html")
        settings_file = os.path.join(current_dir, "frontend", "settings.html")

        tab = WebTab(self.backend, index_file)
        self.tabs.addTab(tab, "Server")

        settings_tab = WebTab(self.settings_backend, settings_file)
        self.tabs.addTab(settings_tab, "Settings")

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(current_dir, "assets", "icon.png")))
        self.tray_icon.setToolTip("Audio Share Server")

        # Tray Menu
        tray_menu = QMenu()
        show_action = QAction("Toggle Visibility", self)
        show_action.triggered.connect(self.ToggleVisibility)
        tray_menu.addAction(show_action)

        # Toggle Server
        server_action = QAction("Toggle Server", self)
        server_action.triggered.connect(self.backend.toggleServer)
        tray_menu.addAction(server_action)

        tray_menu.addSeparator()

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Connect tray icon activation
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def closeEvent(self, event):
        global config_settings
        if string_to_bool(config_settings['App Settings']['minimizetotray']):
            event.ignore()
            self.hide()
            # self.tray_icon.showMessage(
            #     "Audio Share Server",
            #     "Application minimized to tray.",
            #     QSystemTrayIcon.MessageIcon.Information,
            #     1500 # milliseconds
            # )
        else:
            super().closeEvent(event)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isHidden():
                self.show()
            else:
                self.hide()

    def ToggleVisibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    shared_memory = QSharedMemory("audioshare_instance")

    if not shared_memory.create(1):
        print("Another instance is already running.")
        sys.exit(0)

    window = MainWindow()
    window.show()

    # Build a full URL path to your local index.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, "frontend", "index.html")
    local_url = QUrl.fromLocalFile(html_file)

    # Set the window icon
    app.setWindowIcon(QIcon(os.path.join(current_dir, "assets", "icon.png")))

    app.aboutToQuit.connect(window.backend.cleanup)

    sys.exit(app.exec())
