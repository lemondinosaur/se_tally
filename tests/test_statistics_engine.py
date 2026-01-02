# tests/test_statistics_engine.py
from datetime import datetime, timedelta

from statistics_engine import StatisticsEngine


def test_get_daily_summary(record_manager):
    """测试获取当日汇总"""
    engine = StatisticsEngine(record_manager)

    # 获取今天的汇总
    today = datetime.now()

    summary = engine.get_daily_summary(today)

    # 今天应该有2条记录
    assert summary["total_income"] == 100.0  # 薪资
    assert summary["total_expense"] == 50.0  # 餐饮
    assert summary["balance"] == 50.0


def test_get_weekly_summary(record_manager):
    """测试获取本周汇总"""
    engine = StatisticsEngine(record_manager)

    # 获取本周的汇总
    today = datetime.now()
    summary = engine.get_weekly_summary(today)

    # 本周应该包含今日记录和部分上周记录
    assert summary["total_income"] >= 100.0  # 薪资 + 可能的兼职
    assert summary["total_expense"] >= 50.0  # 餐饮 + 可能的购物


def test_get_monthly_summary(record_manager):
    """测试获取本月汇总"""
    engine = StatisticsEngine(record_manager)

    # 获取本月的汇总
    today = datetime.now()
    summary = engine.get_monthly_summary(today.year, today.month)

    # 本月应该包含所有记录，除非是月初测试
    assert summary["total_income"] > 0
    assert summary["total_expense"] > 0
    assert isinstance(summary["balance"], float)


def test_get_category_expenses(record_manager):
    """测试获取分类支出"""
    engine = StatisticsEngine(record_manager)

    # 获取今日的支出分类
    today = datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    category_expenses = engine.get_category_expenses(
        start_date=today_start, end_date=today_end
    )

    # 今天应该只有餐饮支出
    assert "餐饮" in category_expenses
    assert len(category_expenses) == 1
    assert category_expenses["餐饮"] == 50.0


def test_get_top_expenses(record_manager):
    """测试获取支出最高的分类"""
    engine = StatisticsEngine(record_manager)

    # 获取支出最高的3个分类
    today = datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    top_expenses = engine.get_top_expenses(
        limit=3, start_date=today_start, end_date=today_end
    )

    # 今天应该只有1条支出记录
    assert len(top_expenses) == 1
    assert top_expenses[0][0] == "餐饮"
    assert top_expenses[0][1] == 50.0


def test_get_trend_data_day(record_manager):
    """测试获取日趋势数据"""
    engine = StatisticsEngine(record_manager)

    # 获取7天的趋势数据
    trend_data = engine.get_trend_data(period="day", count=7)

    assert len(trend_data) == 7
    for data in trend_data:
        assert "period" in data
        assert "income" in data
        assert "expense" in data


def test_get_trend_data_week(record_manager):
    """测试获取周趋势数据"""
    engine = StatisticsEngine(record_manager)

    # 获取8周的趋势数据
    trend_data = engine.get_trend_data(period="week", count=8)

    assert len(trend_data) == 8
    for data in trend_data:
        assert "period" in data
        assert "income" in data
        assert "expense" in data


def test_get_trend_data_month(record_manager):
    """测试获取月趋势数据"""
    engine = StatisticsEngine(record_manager)

    # 获取6个月的趋势数据
    trend_data = engine.get_trend_data(period="month", count=6)

    assert len(trend_data) == 6
    for data in trend_data:
        assert "period" in data
        assert "income" in data
        assert "expense" in data


def test_calculate_summary(record_manager):
    """测试计算汇总"""
    engine = StatisticsEngine(record_manager)

    # 获取今天的所有记录
    today = datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    records = record_manager.get_all_records(start_date=today_start, end_date=today_end)

    # 计算汇总
    summary = engine._calculate_summary(records)

    # 验证计算结果
    assert summary["total_income"] == 100.0
    assert summary["total_expense"] == 50.0
    assert summary["balance"] == 50.0


def test_empty_summary(record_manager):
    """测试空记录的汇总"""
    engine = StatisticsEngine(record_manager)

    # 创建一个没有记录的时间段
    future_date = datetime.now() + timedelta(days=365)
    records = record_manager.get_all_records(
        start_date=future_date, end_date=future_date + timedelta(days=1)
    )

    # 计算汇总
    summary = engine._calculate_summary(records)

    # 验证空记录的汇总结果
    assert summary["total_income"] == 0.0
    assert summary["total_expense"] == 0.0
    assert summary["balance"] == 0.0
