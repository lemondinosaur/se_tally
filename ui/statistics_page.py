"""
统计分析页面，展示图表和统计数据
"""

import datetime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from statistics_engine import StatisticsEngine
from ui.components import PageHeader, StatsCard
from utils import (
    create_line_chart,
    create_pie_chart,
    format_currency,
    get_chinese_period_name,
)


class StatisticsPage(QWidget):
    """统计分析页面"""

    def __init__(self, parent=None):
        """初始化统计分析页面"""
        super().__init__(parent)
        self.statistics_engine = StatisticsEngine()
        self.line_canvas = None
        self.pie_canvas = None
        # 创建UI
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # 页面标题
        header = PageHeader("统计分析", "查看您的收支趋势和消费结构")
        header.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #333;"
        )
        header.subtitle_label.setStyleSheet(
            "font-size: 16px; color: #666; margin-top: 8px;"
        )
        main_layout.addWidget(header)

        # 顶部控制区域
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)

        # 周期选择
        period_label = QLabel("统计周期:")
        period_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.period_combo = QComboBox()
        self.period_combo.addItems(["day", "week", "month"])
        self.period_combo.setCurrentText("month")
        self.period_combo.setFixedWidth(130)
        self.period_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 20px;
            }
        """
        )
        self.period_combo.currentTextChanged.connect(self.refresh_data)

        # 刷新按钮
        self.refresh_btn = QPushButton("刷新数据")
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 18px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a80d2;
            }
        """
        )
        self.refresh_btn.clicked.connect(self.refresh_data)

        control_layout.addWidget(period_label)
        control_layout.addWidget(self.period_combo)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_btn)

        # 图表区域
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(20)

        # 汇总卡片
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.total_income_card = StatsCard("总收入", "￥0.00", value_color="#2ECC71")
        self.total_expense_card = StatsCard("总支出", "￥0.00", value_color="#E74C3C")
        self.balance_card = StatsCard("结余", "￥0.00")

        cards_layout.addWidget(self.total_income_card)
        cards_layout.addWidget(self.total_expense_card)
        cards_layout.addWidget(self.balance_card)

        # 创建一个简洁的汇总容器
        summary_container = QWidget()
        summary_container.setStyleSheet(
            """
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #e0e0e0;
            }
        """
        )
        summary_layout = QVBoxLayout(summary_container)
        summary_layout.setContentsMargins(20, 20, 20, 5)
        summary_layout.addWidget(
            QLabel(
                "收支汇总",
                styleSheet="font-size: 22px; font-weight: bold; color: #333;",
            )
        )
        summary_layout.addLayout(cards_layout)

        charts_layout.addWidget(summary_container)

        # 创建图表水平布局 - 调整比例
        chart_row_layout = QHBoxLayout()
        chart_row_layout.setSpacing(25)

        # 饼图区域
        self.pie_frame = QFrame()
        self.pie_frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                font-size: 18px;
            }
        """
        )

        pie_layout = QVBoxLayout(self.pie_frame)
        pie_layout.setContentsMargins(10, 10, 10, 10)

        # 饼图容器标题 - 保留此标题
        self.pie_title = QLabel("支出分类比例")
        self.pie_title.setAlignment(Qt.AlignCenter)
        self.pie_title.setStyleSheet(
            "font-weight: bold; font-size: 20px; padding: 8px; color: #333;"
        )

        pie_layout.addWidget(self.pie_title)

        # 折线图区域
        self.line_frame = QFrame()
        self.line_frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """
        )

        line_layout = QVBoxLayout(self.line_frame)
        line_layout.setContentsMargins(10, 10, 10, 10)

        # 折线图容器标题 - 保留此标题
        self.line_title = QLabel("收支趋势")
        self.line_title.setAlignment(Qt.AlignCenter)
        self.line_title.setStyleSheet(
            "font-weight: bold; font-size: 20px; padding: 8px; color: #333;"
        )

        line_layout.addWidget(self.line_title)

        # 调整饼图与折线图比例
        chart_row_layout.addWidget(self.pie_frame, 3)
        chart_row_layout.addWidget(self.line_frame, 5)

        charts_layout.addLayout(chart_row_layout, 4)

        # 消费排行 - 缩小高度比例
        rank_group = QGroupBox("消费排行 (Top 3)")
        rank_group.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        rank_layout = QVBoxLayout(rank_group)
        rank_layout.setContentsMargins(15, 15, 15, 15)

        self.rank_content = QLabel("暂无消费数据")
        self.rank_content.setAlignment(Qt.AlignCenter)
        self.rank_content.setStyleSheet(
            "font-size: 16px; line-height: 1.6; padding: 5px;"
        )

        rank_layout.addWidget(self.rank_content)

        # 调整消费排行区域高度
        charts_layout.addWidget(rank_group, 1)

        # 添加组件到主布局
        main_layout.addLayout(control_layout)
        main_layout.addLayout(charts_layout, 1)

        self.setLayout(main_layout)

    def refresh_data(self):
        """刷新统计数据和图表"""
        period = self.period_combo.currentText()
        period_name = get_chinese_period_name(period)

        # 更新容器标题，避免重复
        self.pie_title.setText(f"{period_name}支出分类比例")
        self.line_title.setText(f"{period_name}收支趋势")

        # 获取数据
        if period == "day":
            summary = self.statistics_engine.get_daily_summary()
            category_expenses = self.statistics_engine.get_category_expenses()
            trend_data = self.statistics_engine.get_trend_data("day", 7)
        elif period == "week":
            summary = self.statistics_engine.get_weekly_summary()
            category_expenses = self.statistics_engine.get_category_expenses()
            trend_data = self.statistics_engine.get_trend_data("week", 8)
        else:  # month
            summary = self.statistics_engine.get_monthly_summary()
            category_expenses = self.statistics_engine.get_category_expenses()
            trend_data = self.statistics_engine.get_trend_data("month", 6)

        # 更新汇总
        self._update_summary(summary)

        # 更新饼图
        self._update_pie_chart(category_expenses, period_name)

        # 更新折线图
        self._update_line_chart(trend_data, period_name)

        # 更新消费排行
        self._update_rankings(period)

    def _update_summary(self, summary):
        """更新汇总信息"""
        total_income = summary["total_income"]
        total_expense = summary["total_expense"]
        balance = summary["balance"]

        self.total_income_card.update_value(format_currency(total_income), "#2ECC71")
        self.total_expense_card.update_value(format_currency(total_expense), "#E74C3C")

        balance_color = "#2ECC71" if balance >= 0 else "#E74C3C"
        self.balance_card.update_value(format_currency(balance), balance_color)

    def _update_pie_chart(self, category_expenses, period_name):
        """更新饼图，避免标题重复"""
        # 清除旧图表
        for i in reversed(range(self.pie_frame.layout().count())):
            widget = self.pie_frame.layout().itemAt(i).widget()
            if widget and widget != self.pie_title:
                widget.setParent(None)

        # 创建新图表 - 缩小饼图半径，使外部文字不会被截断
        # 第三个参数 False 表示不在图表内部设置标题
        fig = create_pie_chart(
            category_expenses,
            f"{period_name}支出分类比例",
            False,
            figsize=(7, 7),
            radius=0.7,
        )
        self.pie_canvas = FigureCanvas(fig)
        self.pie_canvas.setMinimumHeight(400)
        self.pie_frame.layout().addWidget(self.pie_canvas, 1)

    def _update_line_chart(self, trend_data, period_name):
        """更新折线图，避免标题重复"""
        # 清除旧图表
        for i in reversed(range(self.line_frame.layout().count())):
            widget = self.line_frame.layout().itemAt(i).widget()
            if widget and widget != self.line_title:
                widget.setParent(None)

        # 创建新图表 - 不在图表内部设置标题
        fig = create_line_chart(
            trend_data, f"{period_name}收支趋势", False, figsize=(10, 5)
        )
        self.line_canvas = FigureCanvas(fig)
        self.line_canvas.setMinimumHeight(400)
        self.line_frame.layout().addWidget(self.line_canvas, 1)

    def _update_rankings(self, period):
        """更新消费排行"""
        # 获取消费排行
        if period == "day":
            top_expenses = self.statistics_engine.get_top_expenses(limit=3)
        elif period == "week":
            # 本周第一天
            today = datetime.datetime.now()
            week_start = today - datetime.timedelta(days=today.weekday())
            top_expenses = self.statistics_engine.get_top_expenses(
                limit=3, start_date=week_start
            )
        else:  # month
            today = datetime.datetime.now()
            month_start = datetime.datetime(today.year, today.month, 1)
            top_expenses = self.statistics_engine.get_top_expenses(
                limit=3, start_date=month_start
            )

        # 生成排名内容
        if top_expenses:
            rank_text = (
                "<table style='width: 100%; border-collapse: separate; "
                "border-spacing: 0 15px;'>"
            )
            for i, (category, amount) in enumerate(top_expenses, 1):
                rank_text += (
                    f"<tr>"
                    f"<td style='width: 40px; vertical-align: middle;'>"
                    f"<div style='width: 30px; height: 30px; background-color: #f0f0f0; "
                    f"border-radius: 50%; text-align: center; line-height: 30px; "
                    f"font-weight: bold;'>{i}</div></td>"
                    f"<td style='padding: 0 20px; vertical-align: middle; "
                    f"color: #66CCFF; font-weight: bold; font-size: 20px;'>{category}</td>"
                    f"<td style='vertical-align: middle; color: #E74C3C; "
                    f"font-size: 20px; font-weight: bold;'>{format_currency(amount)}</td>"
                    f"</tr>"
                )
            rank_text += "</table>"
            self.rank_content.setText(rank_text)
            self.rank_content.setStyleSheet(
                "font-size: 24px; padding: 20px; background-color: transparent;"
            )
        else:
            self.rank_content.setText("暂无消费数据")
            self.rank_content.setStyleSheet(
                "font-size: 20px; color: #999; padding: 15px;"
            )
