"""
统计引擎模块，提供各类财务统计和分析功能
"""

import datetime
from typing import Dict, List, Tuple

from record import Record, RecordType
from record_manager import RecordManager


class StatisticsEngine:
    """统计引擎，提供账目数据的统计分析功能"""

    def __init__(self, record_manager: RecordManager = None):
        """初始化统计引擎

        Args:
            record_manager: 记录管理器实例，如果为None则创建新实例
        """
        self.record_manager = record_manager or RecordManager()

    def get_daily_summary(self, date: datetime.datetime = None) -> Dict[str, float]:
        """获取指定日期的收支汇总

        Args:
            date: 日期，默认为今天

        Returns:
            包含总收入、总支出、结余的字典
        """
        if date is None:
            date = datetime.datetime.now()

        # 设置为当天的开始和结束时间
        start_date = datetime.datetime(date.year, date.month, date.day)
        end_date = (
            start_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        )

        records = self.record_manager.get_all_records(start_date, end_date)
        return self._calculate_summary(records)

    def get_weekly_summary(self, date: datetime.datetime = None) -> Dict[str, float]:
        """获取指定日期所在周的收支汇总

        Args:
            date: 日期，默认为今天

        Returns:
            包含总收入、总支出、结余的字典
        """
        if date is None:
            date = datetime.datetime.now()

        # 获取本周周一的日期
        monday = date - datetime.timedelta(days=date.weekday())
        start_date = datetime.datetime(monday.year, monday.month, monday.day)
        end_date = (
            start_date + datetime.timedelta(days=7) - datetime.timedelta(seconds=1)
        )

        records = self.record_manager.get_all_records(start_date, end_date)
        return self._calculate_summary(records)

    def get_monthly_summary(
        self, year: int = None, month: int = None
    ) -> Dict[str, float]:
        """获取指定年月的收支汇总

        Args:
            year: 年份，默认为当前年
            month: 月份，默认为当前月

        Returns:
            包含总收入、总支出、结余的字典
        """
        if year is None or month is None:
            today = datetime.datetime.now()
            year = today.year
            month = today.month

        # 设置月份的第一天和最后一天
        start_date = datetime.datetime(year, month, 1)
        if month == 12:
            end_date = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(seconds=1)
        else:
            end_date = datetime.datetime(year, month + 1, 1) - datetime.timedelta(
                seconds=1
            )

        records = self.record_manager.get_all_records(start_date, end_date)
        return self._calculate_summary(records)

    def _calculate_summary(self, records: List[Record]) -> Dict[str, float]:
        """计算记录列表的收支汇总

        Args:
            records: 账目记录列表

        Returns:
            包含总收入、总支出、结余的字典
        """
        total_expense = 0.0
        total_income = 0.0

        for record in records:
            if record.type == RecordType.INCOME:
                total_income += record.amount
            else:
                total_expense += record.amount

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
        }

    def get_category_expenses(
        self, start_date: datetime.datetime = None, end_date: datetime.datetime = None
    ) -> Dict[str, float]:
        """获取指定时间段内各分类的支出金额

        Args:
            start_date: 起始日期
            end_date: 结束日期

        Returns:
            分类-金额映射字典
        """
        records = self.record_manager.get_all_records(start_date, end_date)

        category_expenses = {}
        for record in records:
            if record.type == RecordType.EXPENSE:
                if record.category not in category_expenses:
                    category_expenses[record.category] = 0.0
                category_expenses[record.category] += record.amount

        return category_expenses

    def get_top_expenses(
        self,
        limit: int = 3,
        start_date: datetime.datetime = None,
        end_date: datetime.datetime = None,
    ) -> List[Tuple[str, float]]:
        """获取指定时间段内支出最高的分类

        Args:
            limit: 返回数量限制
            start_date: 起始日期
            end_date: 结束日期

        Returns:
            (分类, 金额)元组列表，按金额降序排列
        """
        category_expenses = self.get_category_expenses(start_date, end_date)

        # 按金额排序并取前limit个
        sorted_expenses = sorted(
            category_expenses.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return sorted_expenses

    def get_trend_data(self, period: str = "month", count: int = 6) -> List[Dict]:
        """获取收支趋势数据

        Args:
            period: 周期类型，'day'、'week'或'month'
            count: 返回的周期数量

        Returns:
            趋势数据列表，每个元素包含日期范围和收支金额
        """
        today = datetime.datetime.now()
        trend_data = []

        for i in range(count - 1, -1, -1):
            if period == "day":
                date = today - datetime.timedelta(days=i)
                summary = self.get_daily_summary(date)
                period_str = date.strftime("%m-%d")
            elif period == "week":
                # 计算本周周一
                week_start = today - datetime.timedelta(days=today.weekday(), weeks=i)
                summary = self.get_weekly_summary(week_start)
                end_date = week_start + datetime.timedelta(days=6)
                period_str = (
                    f"{week_start.strftime('%m-%d')}~{end_date.strftime('%m-%d')}"
                )
            else:  # month
                month = today.month - i
                year = today.year
                while month <= 0:
                    month += 12
                    year -= 1

                summary = self.get_monthly_summary(year, month)
                period_str = f"{year}-{month:02d}"

            trend_data.append(
                {
                    "period": period_str,
                    "income": summary["total_income"],
                    "expense": summary["total_expense"],
                }
            )

        return trend_data
