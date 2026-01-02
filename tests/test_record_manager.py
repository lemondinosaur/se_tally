# tests/test_record_manager.py
from datetime import datetime

from record import RecordType


def test_add_record(record_manager):
    """测试添加记录功能"""
    today = datetime.now()
    record_id = record_manager.add_record(
        amount=100.0,
        category="餐饮",
        description="测试晚餐",
        record_type=RecordType.EXPENSE,
        date=today,
    )

    assert record_id is not None and record_id > 0

    # 验证记录是否添加成功
    record = record_manager.get_record(record_id)
    assert record is not None
    assert record.amount == 100.0
    assert record.category == "餐饮"
    assert record.description == "测试晚餐"
    assert record.type == RecordType.EXPENSE
    assert record.date.date() == today.date()


def test_get_record(record_manager):
    """测试获取单条记录"""
    # 获取已存在的记录（从fixture中插入的记录）
    record = record_manager.get_record(1)
    assert record is not None
    assert record.id == 1
    assert record.amount == 100.0
    assert record.category == "薪资"
    assert record.description == "本月工资"
    assert record.type == RecordType.INCOME


def test_get_all_records(record_manager):
    """测试获取所有记录"""
    records = record_manager.get_all_records()
    assert len(records) == 7  # 从fixture中插入了7条记录


def test_update_record(record_manager):
    """测试更新记录"""
    # 更新第一条记录
    success = record_manager.update_record(
        record_id=1,
        amount=150.0,
        category="薪资",
        description="更新后的工资",
        record_type=RecordType.INCOME,
        date=datetime.now(),
    )

    assert success is True

    # 验证更新是否成功
    record = record_manager.get_record(1)
    assert record.amount == 150.0
    assert record.description == "更新后的工资"


def test_delete_record(record_manager):
    """测试删除记录"""
    # 先获取记录数量
    before_count = len(record_manager.get_all_records())

    # 删除记录
    success = record_manager.delete_record(1)
    assert success is True

    # 验证删除是否成功
    after_count = len(record_manager.get_all_records())
    assert after_count == before_count - 1

    # 验证记录是否不存在
    record = record_manager.get_record(1)
    assert record is None


def test_search_records_by_keyword(record_manager):
    """测试按关键词搜索记录"""
    # 搜索包含"工资"的记录
    records = record_manager.search_records(keyword="工资")
    assert len(records) == 1
    assert records[0].description == "本月工资"

    # 搜索包含"餐"的记录
    records = record_manager.search_records(keyword="餐")
    assert len(records) == 1
    assert records[0].category == "餐饮"


def test_search_records_by_date_range(record_manager):
    """测试按日期范围搜索记录"""
    today = datetime.now()

    # 获取今天的记录
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    records = record_manager.search_records(start_date=today_start, end_date=today_end)
    assert len(records) == 2  # 今日有2条记录（薪资、餐饮）

    # 验证记录日期
    for record in records:
        assert record.date.date() == today.date()


def test_search_records_by_amount_range(record_manager):
    """测试按金额范围搜索记录"""
    # 获取金额在50-100之间的记录
    records = record_manager.search_records(min_amount=50, max_amount=100)
    assert len(records) == 3  # 修正：应该有3条记录（薪资100.0、餐饮50.0、购物80.0）

    # 验证金额范围
    for record in records:
        assert 50 <= record.amount <= 100


def test_search_records_by_type(record_manager):
    """测试按类型搜索记录"""
    # 获取收入记录
    income_records = record_manager.search_records(record_type=RecordType.INCOME)
    assert len(income_records) == 3

    # 获取支出记录
    expense_records = record_manager.search_records(record_type=RecordType.EXPENSE)
    assert len(expense_records) == 4

    # 验证记录类型
    for record in income_records:
        assert record.type == RecordType.INCOME
    for record in expense_records:
        assert record.type == RecordType.EXPENSE


def test_get_categories(record_manager):
    """测试获取分类列表"""
    # 获取所有收入分类
    income_categories = record_manager.get_categories(RecordType.INCOME)
    assert len(income_categories) >= 3
    assert "薪资" in income_categories
    assert "兼职" in income_categories
    assert "理财" in income_categories

    # 获取所有支出分类
    expense_categories = record_manager.get_categories(RecordType.EXPENSE)
    assert len(expense_categories) >= 4
    assert "餐饮" in expense_categories
    assert "交通" in expense_categories
    assert "购物" in expense_categories
    assert "医疗" in expense_categories
