import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QLabel, QFrame, QStackedLayout,
    QCheckBox, QTabWidget, QAction, QMenuBar, QMessageBox, QScrollArea, QListWidgetItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon

class BrowserTab(QWidget):
    def __init__(self, main_window, url="https://www.google.com"):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("⟳")
        self.bookmark_btn = QPushButton("☆")
        self.settings_btn = QPushButton("⚙")
        self.store_btn = QPushButton("🧩")

        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.bookmark_btn.clicked.connect(self.bookmark_current_page)
        self.settings_btn.clicked.connect(self.main_window.open_settings_tab)
        self.store_btn.clicked.connect(self.main_window.open_extension_store)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.bookmark_btn)
        nav_layout.addWidget(self.settings_btn)
        nav_layout.addWidget(self.store_btn)

        self.layout.addLayout(nav_layout)
        self.layout.addWidget(self.browser)

        self.browser.urlChanged.connect(self.update_url_bar)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.browser.setUrl(QUrl(url))

    def update_url_bar(self, q):
        self.url_bar.setText(q.toString())

    def bookmark_current_page(self):
        url = self.browser.url().toString()
        self.main_window.add_bookmark(url)

class SettingsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        close_btn = QPushButton("✖ Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close_settings)

        title = QLabel("Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.toggle_sidebar = QCheckBox("Show Sidebar")
        self.toggle_sidebar.setChecked(True)
        self.toggle_sidebar.stateChanged.connect(lambda: main_window.set_sidebar_visible(self.toggle_sidebar.isChecked()))

        self.toggle_top_tabs = QCheckBox("Use Top Tabs Mode Only")
        self.toggle_top_tabs.setChecked(False)
        self.toggle_top_tabs.stateChanged.connect(lambda: main_window.set_top_tabs_mode(self.toggle_top_tabs.isChecked()))

        self.toggle_dark_mode = QCheckBox("Dark Mode")
        self.toggle_dark_mode.setChecked(False)
        self.toggle_dark_mode.stateChanged.connect(lambda: main_window.set_dark_mode(self.toggle_dark_mode.isChecked()))

        layout.addWidget(close_btn)
        layout.addWidget(title)
        layout.addWidget(self.toggle_sidebar)
        layout.addWidget(self.toggle_top_tabs)
        layout.addWidget(self.toggle_dark_mode)

    def close_settings(self):
        self.main_window.return_to_current_tab()

class ExtensionStore(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        close_btn = QPushButton("✖ Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close_store)

        title = QLabel("Extension Store")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for name in ["Ad Blocker", "Dark Reader", "Cookie Cleaner"]:
            ext_frame = QFrame()
            ext_frame.setFrameShape(QFrame.StyledPanel)
            ext_layout = QHBoxLayout(ext_frame)

            icon = QLabel("📦")
            ext_label = QLabel(name)
            install_btn = QPushButton("Install")

            ext_layout.addWidget(icon)
            ext_layout.addWidget(ext_label)
            ext_layout.addStretch()
            ext_layout.addWidget(install_btn)

            scroll_layout.addWidget(ext_frame)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(close_btn)
        layout.addWidget(title)
        layout.addWidget(scroll_area)

    def close_store(self):
        self.main_window.return_to_current_tab()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blacklisted Browser")
        self.setGeometry(100, 100, 1400, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)

        self.toggle_sidebar_btn = QPushButton("⇦")
        self.toggle_sidebar_btn.setFixedWidth(30)
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)

        self.new_tab_btn = QPushButton("+ New Tab")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab("https://www.google.com"))

        self.tab_list = QListWidget()
        self.tab_list.itemClicked.connect(self.switch_tab)

        self.bookmark_label = QLabel("★ Bookmarks")
        self.bookmark_list = QListWidget()
        self.bookmark_list.itemClicked.connect(self.open_bookmark)

        self.sidebar_layout.addWidget(self.new_tab_btn)
        self.sidebar_layout.addWidget(QLabel("🗂 Tabs"))
        self.sidebar_layout.addWidget(self.tab_list)
        self.sidebar_layout.addWidget(self.bookmark_label)
        self.sidebar_layout.addWidget(self.bookmark_list)

        self.content_frame = QFrame()
        self.content_layout = QStackedLayout(self.content_frame)

        self.main_layout.addWidget(self.toggle_sidebar_btn)
        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_frame, stretch=1)

        self.tabs = []
        self.current_tab_index = -1
        self.top_tabs_mode = False

        self.settings_tab = SettingsTab(self)
        self.extension_store = ExtensionStore(self)

        self.content_layout.addWidget(self.settings_tab)
        self.content_layout.addWidget(self.extension_store)

        self.set_dark_mode(False)
        self.add_new_tab("https://www.google.com")
        self.showMaximized()

    def toggle_sidebar(self):
        is_visible = self.sidebar_frame.isVisible()
        self.sidebar_frame.setVisible(not is_visible)
        self.toggle_sidebar_btn.setText("⇨" if is_visible else "⇦")

    def set_sidebar_visible(self, visible):
        self.sidebar_frame.setVisible(visible)
        self.toggle_sidebar_btn.setText("⇨" if not visible else "⇦")

    def set_top_tabs_mode(self, enabled):
        self.top_tabs_mode = enabled
        self.tab_list.setVisible(not enabled)
        self.new_tab_btn.setVisible(not enabled)
        if enabled:
            QMessageBox.information(self, "Top Tabs Mode", "Top Tabs mode enabled. Use the settings menu to manage tabs.")

    def set_dark_mode(self, enabled):
        if enabled:
            self.setStyleSheet("""
                QWidget { background-color: #121212; color: white; }
                QLineEdit, QListWidget, QPushButton { background-color: #1e1e1e; color: white; }
            """)
        else:
            self.setStyleSheet("")

    def add_new_tab(self, url="https://www.google.com"):
        tab = BrowserTab(main_window=self, url=url)
        self.tabs.append(tab)
        self.content_layout.addWidget(tab)
        self.content_layout.setCurrentWidget(tab)
        self.current_tab_index = len(self.tabs) - 1

        if not self.top_tabs_mode:
            item = QListWidgetItem(f"Tab {len(self.tabs)} ✖")
            self.tab_list.addItem(item)
            self.tab_list.setCurrentRow(self.current_tab_index)

    def switch_tab(self, item):
        index = self.tab_list.row(item)
        if "✖" in item.text():
            self.close_tab(index)
        else:
            if 0 <= index < len(self.tabs):
                self.content_layout.setCurrentWidget(self.tabs[index])
                self.current_tab_index = index

    def close_tab(self, index):
        if 0 <= index < len(self.tabs):
            widget = self.tabs.pop(index)
            self.content_layout.removeWidget(widget)
            widget.deleteLater()
            self.tab_list.takeItem(index)
            self.current_tab_index = max(0, len(self.tabs) - 1)
            if self.tabs:
                self.content_layout.setCurrentWidget(self.tabs[self.current_tab_index])

    def return_to_current_tab(self):
        if 0 <= self.current_tab_index < len(self.tabs):
            self.content_layout.setCurrentWidget(self.tabs[self.current_tab_index])

    def add_bookmark(self, url):
        self.bookmark_list.addItem(url)

    def open_bookmark(self, item):
        self.add_new_tab(url=item.text())

    def open_settings_tab(self):
        self.content_layout.setCurrentWidget(self.settings_tab)

    def open_extension_store(self):
        self.content_layout.setCurrentWidget(self.extension_store)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    sys.exit(app.exec_())
