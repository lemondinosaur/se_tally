"""
记录列表页面，显示所有账目记录
"""

import datetime

from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from record import RecordType
from record_manager import RecordManager
from ui.components import PageHeader, RecordTable, StatsCard
from utils import format_currency


class RecordListPage(QWidget):
    """记录列表页面"""

    # 信号：当记录被添加或更新时发出
    record_added = pyqtSignal()
    record_updated = pyqtSignal(int)  # 传递记录ID

    def __init__(self, parent=None):
        """初始化记录列表页面"""
        super().__init__(parent)
        self.record_manager = RecordManager()
        self.current_date = datetime.datetime.now()

        # 创建UI
        self._init_ui()

        # 加载数据
        self.refresh_data()

    def _init_ui(self):
        """初始化UI组件"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # 页面标题
        header = PageHeader("记账列表", "查看和管理您的收支记录")
        header.subtitle_label.setStyleSheet(
            "font-size: 16px; color: #666; margin-top: 8px;"
        )
        header.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #333;"
        )
        main_layout.addWidget(header)

        # 日期导航和搜索区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(20)

        # 日期导航
        date_layout = QHBoxLayout()
        date_layout.setSpacing(15)

        # 昨天按钮
        self.btn_previous = QPushButton("< 昨天")
        self.btn_previous.setFixedWidth(90)

        # 日期选择
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setFixedWidth(150)

        # 今天按钮
        self.btn_today = QPushButton("今天")
        self.btn_today.setFixedWidth(90)

        # 明天按钮
        self.btn_next = QPushButton("明天 >")
        self.btn_next.setFixedWidth(90)

        # 添加到日期布局
        date_layout.addWidget(self.btn_previous)
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.btn_today)
        date_layout.addWidget(self.btn_next)

        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索备注或分类...")
        self.search_input.setFixedWidth(200)

        self.btn_search = QPushButton("搜索")
        self.btn_search.setFixedWidth(80)
        self.btn_search.setStyleSheet(
            """
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """
        )

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addStretch()

        # 添加到控制布局
        control_layout.addLayout(date_layout)
        control_layout.addStretch()
        control_layout.addLayout(search_layout)

        # 高级筛选区域
        filter_group = QGroupBox("高级筛选")
        filter_group.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        filter_layout = QFormLayout()
        filter_layout.setSpacing(15)

        # 日期范围
        date_range_layout = QHBoxLayout()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setFixedWidth(150)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setFixedWidth(150)

        date_range_layout.addWidget(QLabel("从:"))
        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(QLabel("到:"))
        date_range_layout.addWidget(self.end_date_edit)
        date_range_layout.addStretch()

        filter_layout.addRow("日期范围:", date_range_layout)

        # 金额范围
        amount_layout = QHBoxLayout()

        self.min_amount = QLineEdit()
        self.min_amount.setPlaceholderText("最小金额")
        self.min_amount.setFixedWidth(120)

        self.max_amount = QLineEdit()
        self.max_amount.setPlaceholderText("最大金额")
        self.max_amount.setFixedWidth(120)

        amount_layout.addWidget(self.min_amount)
        amount_layout.addWidget(self.max_amount)
        amount_layout.addStretch()

        filter_layout.addRow("金额范围:", amount_layout)

        # 类型筛选
        self.type_filter = QComboBox()
        self.type_filter.addItems(
            ["全部", RecordType.INCOME.value, RecordType.EXPENSE.value]
        )
        self.type_filter.setFixedWidth(120)

        filter_layout.addRow("类型:", self.type_filter)

        # 应用筛选按钮
        self.btn_apply_filter = QPushButton("应用筛选")
        self.btn_apply_filter.setStyleSheet(
            """
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """
        )

        filter_layout.addRow("", self.btn_apply_filter)

        filter_group.setLayout(filter_layout)

        # 汇总卡片
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)

        self.income_card = StatsCard("今日收入", "￥0.00", value_color="#2ECC71")
        self.expense_card = StatsCard("今日支出", "￥0.00", value_color="#E74C3C")
        self.balance_card = StatsCard("今日结余", "￥0.00")

        summary_layout.addWidget(self.income_card)
        summary_layout.addWidget(self.expense_card)
        summary_layout.addWidget(self.balance_card)

        # 表格
        self.table = RecordTable()

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        self.btn_add = QPushButton("+ 添加账目")
        self.btn_add.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.btn_add.setFixedHeight(45)

        self.btn_edit = QPushButton("修改")
        self.btn_edit.setFixedWidth(80)
        self.btn_edit.setFixedHeight(45)

        self.btn_delete = QPushButton("删除")
        self.btn_delete.setFixedWidth(80)
        self.btn_delete.setFixedHeight(45)
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white;")

        button_layout.addWidget(self.btn_add)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)

        # 搜索结果状态
        self.status_label = QLabel("当前显示今天的所有记录")
        self.status_label.setStyleSheet("font-size: 20px; color: #666; padding: 5px;")

        # 添加所有组件到主布局
        main_layout.addLayout(control_layout)
        main_layout.addLayout(summary_layout)
        main_layout.addWidget(filter_group)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.table, 1)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # 连接信号和槽
        self.btn_previous.clicked.connect(self.show_previous_day)
        self.btn_next.clicked.connect(self.show_next_day)
        self.btn_today.clicked.connect(self.show_today)
        self.date_edit.dateChanged.connect(self.on_date_changed)
        self.btn_search.clicked.connect(self.search_records)
        self.search_input.returnPressed.connect(self.search_records)
        self.btn_add.clicked.connect(self.record_added.emit)
        self.btn_edit.clicked.connect(self.edit_selected_record)
        self.btn_delete.clicked.connect(self.delete_selected_record)
        self.btn_apply_filter.clicked.connect(self.apply_advanced_filter)
        self.table.doubleClicked.connect(self.edit_selected_record)

    def refresh_data(self):
        """刷新数据"""
        # 获取当前日期
        qdate = self.date_edit.date()
        self.current_date = datetime.datetime(qdate.year(), qdate.month(), qdate.day())

        # 获取当天的记录
        start_date = self.current_date
        end_date = (
            self.current_date
            + datetime.timedelta(days=1)
            - datetime.timedelta(seconds=1)
        )

        records = self.record_manager.get_all_records(start_date, end_date)

        # 更新表格
        self._update_table(records)

        # 更新汇总卡片
        self._update_summary_cards()

        # 更新状态
        self.status_label.setText(
            f"当前显示 {self.current_date.strftime('%Y-%m-%d')} 的 {len(records)} 条记录"
        )
        self.status_label.setStyleSheet("font-size: 20px; color: #666; padding: 5px;")

    def _update_table(self, records):
        """更新表格数据"""
        self.table.setRowCount(0)  # 清空表格

        for record in records:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # ID
            self.table.setItem(row_position, 0, QTableWidgetItem(str(record.id)))

            # 时间
            time_str = record.date.strftime("%H:%M")
            time_item = QTableWidgetItem(time_str)
            self.table.setItem(row_position, 1, time_item)

            # 类型
            type_str = record.type.value
            type_item = QTableWidgetItem(type_str)
            if record.type == RecordType.INCOME:
                type_item.setForeground(QBrush(QColor("#2ECC71")))
            else:
                type_item.setForeground(QBrush(QColor("#E74C3C")))
            self.table.setItem(row_position, 2, type_item)

            # 分类
            category_item = QTableWidgetItem(record.category)
            self.table.setItem(row_position, 3, category_item)

            # 金额
            amount_str = f"{record.amount:.2f}"
            amount_item = QTableWidgetItem(amount_str)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if record.type == RecordType.INCOME:
                amount_item.setForeground(QBrush(QColor("#2ECC71")))
            else:
                amount_item.setForeground(QBrush(QColor("#E74C3C")))
            self.table.setItem(row_position, 4, amount_item)

            # 备注
            desc_item = QTableWidgetItem(record.description)
            self.table.setItem(row_position, 5, desc_item)

    def _update_summary_cards(self):
        """更新汇总卡片"""
        # 获取当天汇总
        start_date = self.current_date
        end_date = (
            self.current_date
            + datetime.timedelta(days=1)
            - datetime.timedelta(seconds=1)
        )
        records = self.record_manager.get_all_records(start_date, end_date)

        total_income = 0.0
        total_expense = 0.0

        for record in records:
            if record.type == RecordType.INCOME:
                total_income += record.amount
            else:
                total_expense += record.amount

        balance = total_income - total_expense

        # 更新卡片
        self.income_card.update_value(format_currency(total_income), "#2ECC71")
        self.expense_card.update_value(format_currency(total_expense), "#E74C3C")

        balance_color = "#2ECC71" if balance >= 0 else "#E74C3C"
        self.balance_card.update_value(format_currency(balance), balance_color)

    def show_previous_day(self):
        """显示前一天"""
        current_date = self.date_edit.date()
        previous_date = current_date.addDays(-1)
        self.date_edit.setDate(previous_date)

    def show_next_day(self):
        """显示后一天"""
        current_date = self.date_edit.date()
        next_date = current_date.addDays(1)
        self.date_edit.setDate(next_date)

    def show_today(self):
        """显示今天"""
        self.date_edit.setDate(QDate.currentDate())

    def on_date_changed(self, _):
        """日期改变事件"""
        self.refresh_data()

    def search_records(self):
        """搜索记录"""
        keyword = self.search_input.text().strip()
        if not keyword:
            self.refresh_data()
            return

        qdate = self.date_edit.date()
        current_date = datetime.datetime(qdate.year(), qdate.month(), qdate.day())

        # 搜索当天的记录
        start_date = current_date
        end_date = (
            current_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        )

        records = self.record_manager.search_records(
            keyword=keyword, start_date=start_date, end_date=end_date
        )

        # 更新表格
        self._update_table(records)

        # 更新汇总卡片
        self._update_summary_cards()

        # 更新状态
        if records:
            self.status_label.setText(f"找到 {len(records)} 条包含 '{keyword}' 的记录")
        else:
            self.status_label.setText(f"没有找到包含 '{keyword}' 的记录")

    def apply_advanced_filter(self):
        """应用高级筛选"""
        # 获取日期范围
        end_qdate = self.end_date_edit.date()
        start_qdate = self.start_date_edit.date()

        start_date = datetime.datetime(
            start_qdate.year(), start_qdate.month(), start_qdate.day()
        )
        end_date = (
            datetime.datetime(end_qdate.year(), end_qdate.month(), end_qdate.day())
            + datetime.timedelta(days=1)
            - datetime.timedelta(seconds=1)
        )

        # 获取金额范围
        min_amount = None
        max_amount = None

        if self.min_amount.text().strip():
            try:
                min_amount = float(self.min_amount.text().strip())
            except ValueError:
                QMessageBox.warning(self, "错误", "最小金额格式不正确")
                return

        if self.max_amount.text().strip():
            try:
                max_amount = float(self.max_amount.text().strip())
            except ValueError:
                QMessageBox.warning(self, "错误", "最大金额格式不正确")
                return

        # 获取类型筛选
        record_type = None
        type_str = self.type_filter.currentText()
        if type_str == RecordType.INCOME.value:
            record_type = RecordType.INCOME
        elif type_str == RecordType.EXPENSE.value:
            record_type = RecordType.EXPENSE

        # 应用筛选
        records = self.record_manager.search_records(
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            record_type=record_type,
        )

        # 更新表格
        self._update_table(records)

        # 更新汇总卡片
        self._update_summary_cards()

        # 更新状态
        date_range = (
            f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        )
        if records:
            status = f"筛选结果: {len(records)} 条记录 ({date_range}"
            if min_amount is not None or max_amount is not None:
                amount_range = []
                if min_amount is not None:
                    amount_range.append(f"≥￥{min_amount}")
                if max_amount is not None:
                    amount_range.append(f"≤￥{max_amount}")
                status += f", 金额: {' '.join(amount_range)}"
            if record_type:
                status += f", 类型: {record_type.value}"
            status += ")"
            self.status_label.setText(status)
        else:
            self.status_label.setText(f"没有找到符合条件的记录 ({date_range})")

    def get_selected_record_id(self):
        """获取选中的记录ID"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择一条记录")
            return None

        row = selected_items[0].row()
        record_id = int(self.table.item(row, 0).text())
        return record_id

    def edit_selected_record(self):
        """编辑选中的记录"""
        record_id = self.get_selected_record_id()
        if record_id is None:
            return

        # 发射信号，主窗口会处理
        self.record_updated.emit(record_id)

    def delete_selected_record(self):
        """删除选中的记录"""
        record_id = self.get_selected_record_id()
        if record_id is None:
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            success = self.record_manager.delete_record(record_id)
            if success:
                QMessageBox.information(self, "成功", "记录已删除")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "失败", "删除记录失败")
