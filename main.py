"""
程序主入口，初始化应用并启动主窗口
"""

import argparse
import os
import platform
import sys

import matplotlib.pyplot as plt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


def configure_matplotlib_fonts():
    """配置Matplotlib字体支持中文和货币符号"""
    system = platform.system()

    font_name = None
    if system == "Windows":
        font_name = "Microsoft YaHei"
    elif system == "Darwin":  # macOS
        font_name = "Heiti TC"
    else:  # Linux
        font_name = "WenQuanYi Zen Hei"

    plt.rcParams["font.sans-serif"] = [
        font_name,
        "SimHei",
        "Arial Unicode MS",
        "sans-serif",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def setup_environment():
    """设置运行环境"""
    # 确保存在数据目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # 设置matplotlib字体
    configure_matplotlib_fonts()

    # 设置环境变量，确保PyQt5使用正确的插件路径
    if hasattr(sys, "frozen"):  # 打包后的应用
        app_path = sys._MEIPASS
        os.environ["QT_PLUGIN_PATH"] = os.path.join(app_path, "PyQt5", "Qt", "plugins")
    else:
        pass


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="简约记账本")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--reset", action="store_true", help="重置数据库")
    return parser.parse_args()


def set_application_style(app):
    """设置应用全局样式"""
    # 设置全局字体
    font = (
        QFont("Microsoft YaHei", 10)
        if sys.platform.startswith("win")
        else QFont("PingFang SC", 10)
    )
    app.setFont(font)

    # 设置应用样式表
    app.setStyleSheet(
        """
        QMainWindow {
            background-color: #f0f2f5;
        }
        QWidget {
            font-family: "Microsoft YaHei", "PingFang SC", "SimSun", "Arial", sans-serif;
        }
        QPushButton {
            border-radius: 4px;
        }
        QTableWidget {
            background-color: white;
            border: none;
            gridline-color: #f0f0f0;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        QLineEdit, QComboBox, QDateTimeEdit {
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
        }
    """
    )


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()

    # 设置环境
    setup_environment()

    # 重置数据库（如果需要）
    if args.reset:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "data", "account_book.db")
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"数据库已重置: {db_path}")

    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用样式
    set_application_style(app)

    # 创建主窗口
    window = MainWindow()

    # 设置窗口图标
    icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))

    window.show()

    # 启动应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
