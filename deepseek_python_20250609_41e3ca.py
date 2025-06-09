from bot.core import TradingBot
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

def main():
    bot = TradingBot()
    app = QApplication(sys.argv)
    window = MainWindow(bot)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()