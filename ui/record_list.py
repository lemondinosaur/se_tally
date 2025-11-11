"""
记录列表页面，显示所有账目记录
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QTableWidgetItem, QPushButton, QHeaderView, QLabel,
                           QDateEdit, QMessageBox, QAbstractItemView, QFrame,
                           QComboBox, QLineEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from record import RecordType
from record_manager import RecordManager
import datetime
from ui.components import StatsCard, RecordTable, PageHeader
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
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 页面标题
        header = PageHeader("记账列表", "查看和管理您的收支记录")
        main_layout.addWidget(header)
        
        # 日期导航和搜索区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # 日期导航
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)
        
        # 昨天按钮
        self.btn_previous = QPushButton("< 昨天")
        self.btn_previous.setFixedWidth(80)
        
        # 日期选择
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setFixedWidth(150)
        
        # 今天按钮
        self.btn_today = QPushButton("今天")
        self.btn_today.setFixedWidth(80)
        
        # 明天按钮
        self.btn_next = QPushButton("明天 >")
        self.btn_next.setFixedWidth(80)
        
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
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addStretch()
        
        # 添加到控制布局
        control_layout.addLayout(date_layout)
        control_layout.addStretch()
        control_layout.addLayout(search_layout)
        
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
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
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
        
        # 添加所有组件到主布局
        main_layout.addLayout(control_layout)
        main_layout.addLayout(summary_layout)
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
        self.table.doubleClicked.connect(self.edit_selected_record)
    
    def refresh_data(self):
        """刷新数据"""
        # 获取当前日期
        qdate = self.date_edit.date()
        self.current_date = datetime.datetime(qdate.year(), qdate.month(), qdate.day())
        
        # 获取当天的记录
        start_date = self.current_date
        end_date = self.current_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        
        records = self.record_manager.get_all_records(start_date, end_date)
        
        # 更新表格
        self._update_table(records)
        
        # 更新汇总卡片
        self._update_summary_cards()
    
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
        end_date = self.current_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
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
    
    def on_date_changed(self, qdate):
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
        end_date = current_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        
        records = self.record_manager.search_records(
            keyword=keyword,
            start_date=start_date,
            end_date=end_date
        )
        
        # 更新表格
        self._update_table(records)
        
        # 更新汇总卡片
        self._update_summary_cards()
    
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
            self, "确认删除", 
            "确定要删除这条记录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.record_manager.delete_record(record_id)
            if success:
                QMessageBox.information(self, "成功", "记录已删除")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "失败", "删除记录失败")