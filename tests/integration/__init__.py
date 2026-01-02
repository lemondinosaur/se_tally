from datetime import datetime, timedelta

import pytest

from record import RecordType


class BaseIntegrationTest:
    """集成测试基础类，提供共享功能"""

    @staticmethod
    def create_test_records(record_manager, count=5, base_date=None):
        """创建测试记录用于集成测试
        Args:
            record_manager: 记录管理器
            count: 要创建的记录数量
            base_date: 基准日期，如果不提供则使用当前日期
        """
        if base_date is None:
            base_date = datetime.now()

        records = []
        today = base_date

        # 创建收入记录
        for i in range(count // 2):
            date = today - timedelta(days=i * 2)  # 每隔一天创建记录
            record_id = record_manager.add_record(
                amount=200.0 * (i + 1),
                category="薪资",
                description=f"测试工资 {i + 1}",
                record_type=RecordType.INCOME,
                date=date,
            )
            records.append(record_manager.get_record(record_id))

        # 创建支出记录
        for i in range(count // 2, count):
            date = today - timedelta(days=(i - count // 2) * 2)  # 每隔一天创建记录
            category = "餐饮" if i % 2 == 0 else "购物"
            record_id = record_manager.add_record(
                amount=100.0 * (i + 1),
                category=category,
                description=f"测试消费 {i + 1}",
                record_type=RecordType.EXPENSE,
                date=date,
            )
            records.append(record_manager.get_record(record_id))

        return records
