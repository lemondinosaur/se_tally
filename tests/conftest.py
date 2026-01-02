# tests/conftest.py
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

from data_storage import DataStorage


@pytest.fixture
def test_db():
    """创建临时测试数据库"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_account_book.db")

    storage = DataStorage(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取今天的日期
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # 插入测试记录 - 确保数据按时间分布
    test_records = [
        # 今日记录
        (
            100.0,
            "薪资",
            "本月工资",
            "income",
            today.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 今日收入
        (
            50.0,
            "餐饮",
            "午餐",
            "expense",
            today.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 今日支出
        # 昨日记录
        (
            30.0,
            "交通",
            "地铁费",
            "expense",
            yesterday.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 昨日支出
        # 上周记录
        (
            200.0,
            "兼职",
            "周末兼职",
            "income",
            last_week.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 上周收入
        (
            80.0,
            "购物",
            "衣服",
            "expense",
            last_week.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 上周支出
        # 上月记录
        (
            150.0,
            "理财",
            "基金收益",
            "income",
            last_month.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 上月收入
        (
            120.0,
            "医疗",
            "药费",
            "expense",
            last_month.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),  # 上月支出
    ]

    for record in test_records:
        cursor.execute(
            """
        INSERT INTO records (amount, category, description, type, date)
        VALUES (?, ?, ?, ?, ?)
        """,
            record,
        )

    conn.commit()
    conn.close()

    yield storage

    # 测试结束后清理
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


@pytest.fixture
def record_manager(test_db):
    """创建测试用的RecordManager"""
    from record_manager import RecordManager

    return RecordManager(test_db)
