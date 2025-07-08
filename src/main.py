import sys
from configparser import ConfigParser

from PyQt6.QtWidgets import QApplication ,QMainWindow, QWidget, QVBoxLayout , QTabWidget , QSystemTrayIcon , QMenu, QStyle
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QSize , Qt
from PyQt6.QtGui import QIcon , QAction
import os
from backend import Backend, SettingsBackend , Finder

config_settings = None
secondary_window = None

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

        

class SettingsWindow(QMainWindow):
    def __init__(self, url , settings_channel):
        super().__init__()
        self.setWindowTitle("App Settings")
        self.resize(800, 600)

        self.web_view = QWebEngineView()

        page = type("TempPage", (QWebEnginePage,), {
            "javaScriptConsoleMessage": lambda self, level, msg, line, src: print(
                f"[JS {level.name}] {msg} (line {line}, source {src})")
        })(self.web_view)

        channel = QWebChannel()
        channel.registerObject('backend', settings_channel)
        page.setWebChannel(channel)
        self.web_view.setPage(page)
    
        #print(url)
        self.web_view.load(url)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.web_view)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        # Just hide the window instead of closing, optional
        #print("Secondary window closed (but app stays running)")
        self.hide()
        event.accept()
        

# def main():

#     backend = Backend()
#     print(backend.getEndpointList())
#     backend.request_applicationSettings.connect(ApplcationSettings)

#     # Create a ConfigParser object
#     global config_settings
#     config_settings = ConfigParser()


#     config_file_path = 'config.ini'  # Replace with your actual file path

#     if os.path.exists(config_file_path):
#         config_settings.read(config_file_path)
#         print(f"Configuration file '{config_file_path}' found and loaded.")
#         # You can now access sections and options from 'config_settings'

#     else:
#         # Default Config Creation

#         print(f"Configuration file '{config_file_path}' not found.")
#         # Handle the case where the file doesn't exist, e.g., create a default one
#         with open('config.ini', 'w') as configfile:
#             config_settings['Server Settings'] = {'serverIP' : f'{backend.get_local_ipv4_address()}', 'serverPort' : '65530'}
#             config_settings['App Settings'] = {'AutoStart' : 'False','KeepLastState' : 'False', 'MinimizeToTray' : 'False'}
#             # Save in-memory config to ini file
#             config_settings.write(configfile)

#     app = QApplication(sys.argv)

#     app.setApplicationName("Audio-Share PyQT")
    
#     webview = QWebEngineView()

#     webview.setPage(type("TempPage", (QWebEnginePage,), {
#         "javaScriptConsoleMessage": lambda self, level, msg, line, src: print(
#             f"[JS {level.name}] {msg} (line {line}, source {src})")
#     })(webview))

#     # Set up the backend bridge
#     channel = QWebChannel()
    
#     channel.registerObject('backend', backend)
#     webview.page().setWebChannel(channel)

#     # Build a full URL path to your local index.html
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     html_file = os.path.join(current_dir, "frontend", "index.html")
#     local_url = QUrl.fromLocalFile(html_file)

#     # Set the window icon
#     app.setWindowIcon(QIcon(os.path.join(current_dir, "assets", "icon.png")))

#     webview.load(local_url)
#     webview.setWindowTitle("Audio Share Server")
#     webview.resize(800, 600)
#     webview.show()

#     webview.setMinimumSize(QSize(650, 500))

#     app.aboutToQuit.connect(backend.cleanup)

#     sys.exit(app.exec())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Share Server")
        self.resize(1000, 700)
        # Create a ConfigParser object
        global config_settings
        config_settings = ConfigParser()

        config_file_path = 'config.ini'  # Replace with your actual file path

        if os.path.exists(config_file_path):
            config_settings.read(config_file_path)
            print(f"Configuration file '{config_file_path}' found and loaded.")
            # You can now access sections and options from 'config_settings'

            try:
                ServerSettings = config_settings['Server Settings']
                AppSettings = config_settings['App Settings']
            except KeyError:
                # Handle the case where the file doesn't have the basic keys
                # Remake the file
                with open('config.ini', 'w') as configfile:
                    Endpoints = Finder().getEndpointList()
                    Encoding = Finder().getEncodingList()
                    config_settings['Server Settings'] = {'serverIP' : f'{Finder().get_local_ipv4_address()}', 'serverPort' : '65530' , 'endpoint' : f'{Endpoints[0]['id']}' , 'encoding' : f'{Encoding[0]['key']}'}
                    config_settings['App Settings'] = {'AutoStart' : 'False','KeepLastState' : 'False', 'MinimizeToTray' : 'False'}
                    # Save in-memory config to ini file
                    config_settings.write(configfile)

        else:
            # Default Config Creation

            print(f"Configuration file '{config_file_path}' not found.")
            # Handle the case where the file doesn't exist, e.g., create a default one
            with open('config.ini', 'w') as configfile:
                Endpoints = Finder().getEndpointList()
                Encoding = Finder().getEncodingList()
                config_settings['Server Settings'] = {'serverIP' : f'{Finder().backend.get_local_ipv4_address()}', 'serverPort' : '65530' , 'endpoint' : f'{Endpoints[0]['id']}' , 'encoding' : f'{Encoding[0]['key']}'}
                config_settings['App Settings'] = {'AutoStart' : 'False','KeepLastState' : 'False', 'MinimizeToTray' : 'False'}
                # Save in-memory config to ini file
                config_settings.write(configfile)

        self.backend = Backend(config_settings)

        self.settings_backend = SettingsBackend(config_settings)
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
    #main()

    app = QApplication(sys.argv)
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
