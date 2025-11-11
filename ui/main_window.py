"""
主窗口实现，包含页面切换和底部导航栏
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from data_storage import DataStorage
from ui.add_record import AddRecordPage
from ui.record_list import RecordListPage
from ui.statistics_page import StatisticsPage


class MainWindow(QMainWindow):
    """主窗口类，包含页面切换功能"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        self.setWindowTitle("简约记账本")
        self.setMinimumSize(1000, 700)

        # 初始化数据存储
        self.data_storage = DataStorage()

        # 创建页面堆栈
        self.stacked_widget = QStackedWidget()

        # 创建页面
        self.record_list_page = RecordListPage()
        self.add_record_page = AddRecordPage()
        self.statistics_page = StatisticsPage()

        # 添加页面到堆栈
        self.stacked_widget.addWidget(self.record_list_page)
        self.stacked_widget.addWidget(self.add_record_page)
        self.stacked_widget.addWidget(self.statistics_page)

        # 创建底部导航栏
        self.nav_bar = self._create_navigation_bar()

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stacked_widget, 1)
        main_layout.addWidget(self.nav_bar)

        # 创建中央部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 默认显示记录列表页
        self.show_record_list()

        # 连接信号
        self.record_list_page.record_added.connect(lambda: self.show_add_record())
        self.record_list_page.record_updated.connect(self.show_add_record)
        self.add_record_page.record_saved.connect(self.show_record_list)

    def _create_navigation_bar(self) -> QFrame:
        """创建底部导航栏

        Returns:
            导航栏QFrame
        """
        nav_frame = QFrame()
        nav_frame.setFixedHeight(60)
        nav_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 25px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:checked {
                background-color: #4a90e2;
                color: white;
            }
        """
        )

        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(20, 5, 20, 5)
        nav_layout.setSpacing(30)

        # 创建导航按钮
        self.btn_record_list = QPushButton("记账\n列表")
        self.btn_add_record = QPushButton("+\n添加")
        self.btn_statistics = QPushButton("统计\n分析")
        self.btn_export = QPushButton("导出\n数据")

        # 设置按钮选中状态
        self.btn_record_list.setCheckable(True)
        self.btn_add_record.setCheckable(True)
        self.btn_statistics.setCheckable(True)
        self.btn_export.setCheckable(True)

        # 默认选中记录列表按钮
        self.btn_record_list.setChecked(True)

        # 添加按钮到布局
        nav_layout.addWidget(self.btn_record_list, 1, Qt.AlignCenter)
        nav_layout.addWidget(self.btn_add_record, 1, Qt.AlignCenter)
        nav_layout.addWidget(self.btn_statistics, 1, Qt.AlignCenter)
        nav_layout.addWidget(self.btn_export, 1, Qt.AlignCenter)

        # 连接按钮点击事件
        self.btn_record_list.clicked.connect(self.show_record_list)
        self.btn_add_record.clicked.connect(lambda: self.show_add_record())
        self.btn_statistics.clicked.connect(self.show_statistics)
        self.btn_export.clicked.connect(self.export_data)

        return nav_frame

    def show_record_list(self):
        """显示记录列表页面"""
        self.stacked_widget.setCurrentWidget(self.record_list_page)
        self.btn_record_list.setChecked(True)
        self.btn_add_record.setChecked(False)
        self.btn_statistics.setChecked(False)
        self.btn_export.setChecked(False)
        self.record_list_page.refresh_data()

    def show_add_record(self, record_id=None):
        """显示添加账目页面

        Args:
            record_id: 如果提供，则为编辑模式
        """
        # 重置页面，如果是编辑模式则加载数据
        self.add_record_page.reset_form(record_id)

        self.stacked_widget.setCurrentWidget(self.add_record_page)
        self.btn_record_list.setChecked(False)
        self.btn_add_record.setChecked(True)
        self.btn_statistics.setChecked(False)
        self.btn_export.setChecked(False)

    def show_statistics(self):
        """显示统计分析页面"""
        self.stacked_widget.setCurrentWidget(self.statistics_page)
        self.btn_record_list.setChecked(False)
        self.btn_add_record.setChecked(False)
        self.btn_statistics.setChecked(True)
        self.btn_export.setChecked(False)
        self.statistics_page.refresh_data()

    def export_data(self):
        """导出数据"""
        # 获取保存文件路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "", "CSV 文件 (*.csv)"
        )

        if file_path:
            if not file_path.endswith(".csv"):
                file_path += ".csv"

            try:
                self.data_storage.export_to_csv(file_path)
                # 显示成功消息
                QMessageBox.information(self, "成功", f"数据已成功导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
