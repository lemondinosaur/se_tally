from datetime import datetime, timedelta

from record import RecordType

from . import BaseIntegrationTest


class TestCompleteWorkflow(BaseIntegrationTest):
    """测试完整的账目管理流程：添加、查询、更新、删除"""

    def test_full_record_lifecycle(self, record_manager):
        """测试记录的完整生命周期：创建 -> 查询 -> 更新 -> 删除"""
        today = datetime.now()

        # 1. 添加新记录
        record_id = record_manager.add_record(
            amount=150.0,
            category="餐饮",
            description="午餐测试",
            record_type=RecordType.EXPENSE,
            date=today,
        )
        assert record_id is not None
        assert record_id > 0

        # 2. 查询记录
        record = record_manager.get_record(record_id)
        assert record is not None
        assert record.amount == 150.0
        assert record.category == "餐饮"
        assert record.description == "午餐测试"
        assert record.type == RecordType.EXPENSE
        assert record.date.date() == today.date()

        # 3. 更新记录
        success = record_manager.update_record(
            record_id=record_id,
            amount=180.0,
            category="餐饮",
            description="更新后的午餐测试",
            record_type=RecordType.EXPENSE,
            date=today,
        )
        assert success is True

        # 验证更新结果
        updated_record = record_manager.get_record(record_id)
        assert updated_record.amount == 180.0
        assert updated_record.description == "更新后的午餐测试"

        # 4. 搜索记录
        search_results = record_manager.search_records(keyword="午餐")
        assert len(search_results) > 0
        assert any("更新后的午餐测试" in r.description for r in search_results)

        # 5. 删除记录
        delete_success = record_manager.delete_record(record_id)
        assert delete_success is True

        # 6. 验证删除结果
        deleted_record = record_manager.get_record(record_id)
        assert deleted_record is None

    def test_daily_workflow(self, record_manager):
        """测试日常账目管理完整流程"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # 1. 创建多条今日记录
        record_ids = []

        # 今日收入
        income_id = record_manager.add_record(
            amount=200.0,
            category="薪资",
            description="今日工资",
            record_type=RecordType.INCOME,
            date=today,
        )
        record_ids.append(income_id)

        # 今日支出
        expense_id = record_manager.add_record(
            amount=60.0,
            category="餐饮",
            description="今日午餐",
            record_type=RecordType.EXPENSE,
            date=today,
        )
        record_ids.append(expense_id)

        # 2. 验证记录创建
        today_records = record_manager.get_all_records(
            start_date=today.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=today.replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        assert len(today_records) >= 2
        assert any(r.id == income_id for r in today_records)
        assert any(r.id == expense_id for r in today_records)

        # 3. 创建昨日记录
        yesterday_id = record_manager.add_record(
            amount=40.0,
            category="交通",
            description="昨日地铁",
            record_type=RecordType.EXPENSE,
            date=yesterday,
        )
        record_ids.append(yesterday_id)

        # 4. 按日期范围搜索
        date_range_records = record_manager.search_records(
            start_date=yesterday.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=today.replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        assert len(date_range_records) >= 3  # 2条今日记录 + 1条昨日记录

        # 5. 按金额范围搜索
        amount_records = record_manager.search_records(min_amount=50, max_amount=200)
        assert len(amount_records) >= 2  # 150的支出和200的收入

        # 6. 按类型筛选
        expense_records = record_manager.search_records(record_type=RecordType.EXPENSE)
        assert len(expense_records) >= 2  # 60的餐饮和40的交通

        # 7. 删除所有测试记录
        for record_id in record_ids:
            record_manager.delete_record(record_id)

        # 8. 验证所有记录已被删除
        remaining_records = record_manager.get_all_records(
            start_date=yesterday.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=today.replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        assert not any(r.id in record_ids for r in remaining_records)
