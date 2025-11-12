"""
公共UI组件模块
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PageHeader(QWidget):
    """页面标题栏组件"""

    def __init__(self, title: str, subtitle: str = None, parent=None):
        """初始化页面标题栏

        Args:
            title: 主标题
            subtitle: 副标题，可选
            parent: 父组件
        """
        super().__init__(parent)

        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 15)

        # 主标题
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        """
        )

        # 副标题
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setStyleSheet(
                """
                QLabel {
                    font-size: 14px;
                    color: #666;
                    margin-top: 5px;
                }
            """
            )
            layout.addWidget(self.subtitle_label)

        # 添加组件
        layout.addWidget(self.title_label)
        self.setLayout(layout)

    def update_title(self, title: str):
        """更新标题"""
        self.title_label.setText(title)

    def update_subtitle(self, subtitle: str):
        """更新副标题"""
        if hasattr(self, "subtitle_label"):
            self.subtitle_label.setText(subtitle)


class StatsCard(QWidget):
    """统计卡片组件"""

    def __init__(
        self,
        title: str,
        value: str,
        icon: str = None,
        value_color: str = "#333",
        parent=None,
    ):
        """初始化统计卡片

        Args:
            title: 卡片标题
            value: 数值
            icon: 图标，可选
            value_color: 数值颜色
            parent: 父组件
        """
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.value_color = value_color

        # 设置样式
        self.setStyleSheet(
            """
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """
        )

        # 设置最小高度
        self.setMinimumHeight(120)

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 20px; color: #666;")

        # 数值
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.value_color};
                margin-top: 5px;
            }}
        """
        )

        # 添加组件
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        self.setLayout(layout)

    def update_value(self, value: str, color: str = None):
        """更新数值"""
        self.value = value
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 24px;
                    font-weight: bold;
                    color: {color};
                    margin-top: 5px;
                }}
            """
            )


class RecordTable(QTableWidget):
    """记录表格组件"""

    def __init__(self, parent=None):
        """初始化记录表格"""
        super().__init__(parent)

        # 设置表格属性
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["ID", "时间", "类型", "分类", "金额", "备注"])

        # 隐藏ID列
        self.setColumnHidden(0, True)

        # 设置表头样式
        header = self.horizontalHeader()
        header.setStyleSheet(
            """
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                font-size: 22px;
                font-weight: bold;
                color: #333;
            }
        """
        )

        # 设置列宽
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 时间
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 分类
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 金额
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # 备注

        # 设置表格样式
        self.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #f0f0f0;
                font-size: 20px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1a73e8;
            }
        """
        )

        # 禁止编辑
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选择行为
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置交替行颜色
        self.setAlternatingRowColors(True)
        # 设置行高
        self.verticalHeader().setDefaultSectionSize(40)
        # 隐藏垂直表头
        self.verticalHeader().setVisible(False)

    def add_record(self, record):
        """添加记录到表格"""
        row_position = self.rowCount()
        self.insertRow(row_position)

        # 设置各项内容
        self.setItem(row_position, 0, QTableWidgetItem(str(record.id)))

        # 时间
        time_item = QTableWidgetItem(record.date.strftime("%H:%M"))
        self.setItem(row_position, 1, time_item)

        # 类型
        type_item = QTableWidgetItem(record.type.value)
        if record.type == "income":
            type_item.setForeground(QColor("#2ECC71"))
        else:
            type_item.setForeground(QColor("#E74C3C"))
        self.setItem(row_position, 2, type_item)

        # 分类
        self.setItem(row_position, 3, QTableWidgetItem(record.category))

        # 金额
        amount_item = QTableWidgetItem(f"{record.amount:.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if record.type == "income":
            amount_item.setForeground(QColor("#2ECC71"))
        else:
            amount_item.setForeground(QColor("#E74C3C"))
        self.setItem(row_position, 4, amount_item)

        # 备注
        self.setItem(row_position, 5, QTableWidgetItem(record.description))


class ScrollableWidget(QScrollArea):
    """可滚动的容器组件"""

    def __init__(self, widget=None, parent=None):
        """初始化可滚动容器

        Args:
            widget: 要放入的组件
            parent: 父组件
        """
        super().__init__(parent)

        # 设置滚动区域属性
        self.setWidgetResizable(True)
        self.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )

        # 设置内部组件
        if widget:
            self.set_widget(widget)

    def set_widget(self, widget):
        """设置滚动区域内的组件"""
        widget.setStyleSheet("background-color: transparent;")
        self.setWidget(widget)
