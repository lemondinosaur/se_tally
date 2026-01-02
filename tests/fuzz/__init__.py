import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta

import hypothesis
import pytest
from hypothesis import strategies as st

from data_storage import DataStorage
from record import Record, RecordType
from record_manager import RecordManager
from statistics_engine import StatisticsEngine


class BaseFuzzTest:
    """模糊测试基础类，提供共享功能"""

    @staticmethod
    def setup_temp_database():
        """创建临时数据库环境"""
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "fuzz_test.db")

        # 创建数据库
        storage = DataStorage(db_path)

        return {
            "storage": storage,
            "record_manager": RecordManager(storage),
            "statistics_engine": StatisticsEngine(RecordManager(storage)),
            "temp_dir": temp_dir,
            "db_path": db_path,
        }

    @staticmethod
    def cleanup_temp_database(env):
        """清理临时数据库环境"""
        try:
            if os.path.exists(env["temp_dir"]):
                shutil.rmtree(env["temp_dir"])
        except:
            pass

    @staticmethod
    @hypothesis.given(
        amount=st.floats(min_value=0.01, max_value=1000000.0),
        is_income=st.booleans(),
        days_offset=st.integers(min_value=-365, max_value=365),
    )
    @hypothesis.settings(max_examples=100, deadline=None)
    def test_common_operations(self, amount, is_income, days_offset):
        """测试通用操作模式"""
        env = None
        try:
            env = self.setup_temp_database()

            # 创建测试记录
            record_type = RecordType.INCOME if is_income else RecordType.EXPENSE
            record_date = datetime.now() + timedelta(days=days_offset)

            record_id = env["record_manager"].add_record(
                amount=amount,
                category="测试分类",
                description="模糊测试记录",
                record_type=record_type,
                date=record_date,
            )

            assert record_id is not None

            # 搜索记录
            search_results = env["record_manager"].search_records(
                min_amount=amount - 1, max_amount=amount + 1
            )
            assert len(search_results) >= 1

        finally:
            if env:
                self.cleanup_temp_database(env)
