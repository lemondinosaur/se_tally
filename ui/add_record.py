"""
添加账目页面
"""

import datetime

from PyQt5.QtCore import QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from record import RecordType
from record_manager import RecordManager
from ui.components import PageHeader
from utils import format_currency


class AddRecordPage(QWidget):
    """添加账目页面"""

    # 信号：当记录保存成功时发出
    record_saved = pyqtSignal()

    def __init__(self, parent=None):
        """初始化添加账目页面"""
        super().__init__(parent)
        self.record_manager = RecordManager()
        self.current_record_id = None  # 当前编辑的记录ID，None表示添加模式

        # 初始化UI
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # 页面标题
        self.header = PageHeader("编辑账目", "记录您的收入或支出")
        self.header.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #333;"
        )
        self.header.subtitle_label.setStyleSheet(
            "font-size: 16px; color: #666; margin-top: 8px;"
        )
        main_layout.addWidget(self.header)

        # 表单容器
        form_container = QFrame()
        form_container.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
        """
        )

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(20)

        # 表单
        input_form = QFormLayout()
        input_form.setLabelAlignment(Qt.AlignRight)
        input_form.setSpacing(15)
        input_form.setContentsMargins(0, 0, 0, 0)

        # 日期时间
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setFixedHeight(60)
        self.datetime_edit.setStyleSheet("padding: 10px;")

        # 类型
        self.type_combo = QComboBox()
        self.type_combo.addItems([RecordType.INCOME.value, RecordType.EXPENSE.value])
        self.type_combo.setFixedHeight(60)
        self.type_combo.setStyleSheet("padding: 10px;")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)

        # 金额
        amount_layout = QHBoxLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 1000000.00)
        self.amount_spin.setPrefix("￥ ")
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(0.00)
        self.amount_spin.setFixedHeight(60)
        self.amount_spin.setStyleSheet("font-size: 20px; padding: 10px;")
        self.amount_spin.valueChanged.connect(self.on_amount_changed)

        amount_layout.addWidget(self.amount_spin)
        amount_layout.addStretch()

        # 分类
        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(60)
        self.category_combo.setStyleSheet("padding: 10px;")
        # 先添加一些默认分类
        self.update_categories(RecordType.EXPENSE)

        # 备注
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("输入备注信息...")
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setStyleSheet("padding: 10px;")

        # 添加表单项
        input_form.addRow("日期时间:", self.datetime_edit)
        input_form.addRow("类型:", self.type_combo)
        input_form.addRow("金额:", amount_layout)
        input_form.addRow("分类:", self.category_combo)
        input_form.addRow("备注:", self.desc_edit)

        # 预览标签
        self.preview_label = QLabel("今日支出: ￥0.00")
        self.preview_label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #E74C3C;
                margin-top: 10px;
            }
        """
        )
        self.preview_label.setAlignment(Qt.AlignRight)

        # 添加所有组件到表单容器
        form_layout.addLayout(input_form)
        form_layout.addWidget(self.preview_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 20, 0, 0)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setFixedHeight(50)
        self.btn_cancel.setStyleSheet(
            """
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #e9e9e9;
            }
        """
        )

        self.btn_save = QPushButton("添加")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setStyleSheet(
            """
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #3a80d2;
            }
        """
        )

        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_save)

        # 添加所有组件到主布局
        main_layout.addWidget(form_container)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

        # 连接信号
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_save.clicked.connect(self.on_save)

        # 初始更新预览
        self.update_preview()

    def on_type_changed(self, index):
        """类型改变事件"""
        record_type = RecordType.INCOME if index == 0 else RecordType.EXPENSE
        self.update_categories(record_type)
        self.update_preview()

    def on_amount_changed(self, _):
        """金额改变事件"""
        self.update_preview()

    def update_preview(self):
        """更新预览标签"""
        record_type = (
            RecordType.INCOME
            if self.type_combo.currentIndex() == 0
            else RecordType.EXPENSE
        )
        amount = self.amount_spin.value()

        qdatetime = self.datetime_edit.dateTime()
        date = qdatetime.toPyDateTime()

        # 获取当天的汇总
        start_date = datetime.datetime(date.year, date.month, date.day)
        end_date = (
            start_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        )

        records = self.record_manager.get_all_records(start_date, end_date)

        total_expense = 0.0
        total_income = 0.0

        for record in records:
            if record.type == RecordType.EXPENSE:
                total_expense += record.amount
            else:
                total_income += record.amount

        # 加上当前输入的金额
        if record_type == RecordType.INCOME:
            total_income += amount
        else:
            total_expense += amount

        if record_type == RecordType.INCOME:
            preview_text = f"今日收入: {format_currency(total_income)}"
            preview_color = "#2ECC71"
        else:
            preview_text = f"今日支出: {format_currency(total_expense)}"
            preview_color = "#E74C3C"

        self.preview_label.setText(preview_text)
        self.preview_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {preview_color};
                margin-top: 10px;
            }}
        """
        )

    def update_categories(self, record_type):
        """更新分类下拉框"""
        self.category_combo.clear()
        categories = self.record_manager.get_categories(record_type)
        self.category_combo.addItems(categories)
        if categories:
            self.category_combo.setCurrentIndex(0)

    def load_record_data(self, record_id):
        """加载记录数据（编辑模式）"""
        record = self.record_manager.get_record(record_id)
        if not record:
            QMessageBox.warning(self, "错误", "记录不存在")
            return False

        self.current_record_id = record_id

        # 设置UI
        self.datetime_edit.setDateTime(
            QDateTime(
                record.date.year,
                record.date.month,
                record.date.day,
                record.date.hour,
                record.date.minute,
                record.date.second,
            )
        )

        if record.type == RecordType.INCOME:
            self.type_combo.setCurrentText(RecordType.INCOME.value)
        else:
            self.type_combo.setCurrentText(RecordType.EXPENSE.value)

        self.amount_spin.setValue(record.amount)
        self.update_categories(record.type)
        self.category_combo.setCurrentText(record.category)
        self.desc_edit.setPlainText(record.description)

        # 更新标题和按钮文本
        self.header.update_title("编辑账目")
        self.header.update_subtitle("修改现有账目记录")
        self.btn_save.setText("更新")

        # 更新预览
        self.update_preview()

        return True

    def reset_form(self, record_id=None):
        """重置表单，如果是编辑模式则加载数据"""
        # 重置为添加模式
        self.current_record_id = None
        self.header.update_title("添加账目")
        self.header.update_subtitle("记录您的收入或支出")
        self.btn_save.setText("添加")

        # 重置表单数据
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.type_combo.setCurrentIndex(1)  # 默认选择支出
        self.amount_spin.setValue(0.00)
        self.update_categories(RecordType.EXPENSE)
        self.desc_edit.clear()

        # 如果是编辑模式，加载记录数据
        if record_id is not None:
            self.load_record_data(record_id)

    def on_cancel(self):
        """取消操作"""
        self.record_saved.emit()

    def on_save(self):
        """保存记录"""
        # 获取表单数据
        qdatetime = self.datetime_edit.dateTime()
        date_time = qdatetime.toPyDateTime()

        type_str = self.type_combo.currentText()
        record_type = (
            RecordType.INCOME
            if type_str == RecordType.INCOME.value
            else RecordType.EXPENSE
        )

        amount = self.amount_spin.value()
        category = self.category_combo.currentText()
        description = self.desc_edit.toPlainText().strip()

        # 验证
        if amount <= 0:
            QMessageBox.warning(self, "错误", "金额必须大于0")
            return

        if not category:
            QMessageBox.warning(self, "错误", "请选择分类")
            return

        try:
            if self.current_record_id is not None:
                # 更新记录
                success = self.record_manager.update_record(
                    self.current_record_id,
                    amount,
                    category,
                    description,
                    record_type,
                    date_time,
                )
                if success:
                    QMessageBox.information(self, "成功", "记录已更新")
                    self.record_saved.emit()
                else:
                    QMessageBox.warning(self, "失败", "更新记录失败")
            else:
                # 添加新记录
                record_id = self.record_manager.add_record(
                    amount, category, description, record_type, date_time
                )
                if record_id:
                    QMessageBox.information(self, "成功", "记录已添加")
                    self.reset_form()  # 重置表单以便添加下一个记录
                else:
                    QMessageBox.warning(self, "失败", "添加记录失败")
        except Exception as e:  # pylint: disable=broad-exception-caught
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
