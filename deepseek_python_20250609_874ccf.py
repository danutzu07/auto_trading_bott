from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar
)
from .dashboard import DashboardTab
from .charts import ChartsTab
from .settings import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.setWindowTitle("Auto Trading Bot")
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
        
    def init_ui(self):
        # Crează widget-ul central și layout-ul principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Crează interfața cu tab-uri
        self.tabs = QTabWidget()
        
        # Adaugă tab-uri
        self.dashboard_tab = DashboardTab(self.bot)
        self.charts_tab = ChartsTab(self.bot)
        self.settings_tab = SettingsTab(self.bot)
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.charts_tab, "Charts")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        main_layout.addWidget(self.tabs)
        
        # Adaugă bara de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Conectează semnale
        self.dashboard_tab.start_bot_signal.connect(self.start_bot)
        self.dashboard_tab.stop_bot_signal.connect(self.stop_bot)
        
    def start_bot(self):
        self.bot.running = True
        self.status_bar.showMessage("Bot is running...")
        
    def stop_bot(self):
        self.bot.running = False
        self.status_bar.showMessage("Bot stopped")