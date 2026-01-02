import random
from datetime import datetime, timedelta

import hypothesis
from hypothesis import strategies as st

from record import RecordType

from . import BaseFuzzTest


class TestSearchFuzz(BaseFuzzTest):
    """模糊测试搜索功能的健壮性"""

    @hypothesis.given(
        keyword=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_+-= ",
            min_size=0,
            max_size=50,
        ),
        category=st.sampled_from(["餐饮", "交通", "购物", "薪资", "其他"]),
        record_count=st.integers(min_value=0, max_value=50),
    )
    @hypothesis.settings(
        max_examples=200,
        deadline=None,
        suppress_health_check=[hypothesis.HealthCheck.too_slow],
    )
    def test_search_robustness(self, keyword, category, record_count):
        """测试搜索功能对各种输入的健壮性"""
        env = None
        try:
            env = self.setup_temp_database()

            # 准备测试数据
            descriptions = [
                f"测试记录 {keyword}",
                f"包含{keyword}的描述",
                f"不相关的记录",
                f"{keyword}在开头",
                f"结尾有{keyword}",
                "",
            ]

            # 随机添加记录
            for i in range(record_count):
                desc = random.choice(descriptions)
                record_type = random.choice([RecordType.INCOME, RecordType.EXPENSE])
                i = i + 1 - 1
                env["record_manager"].add_record(
                    amount=random.uniform(1.0, 1000.0),
                    category=(
                        category
                        if random.random() > 0.3
                        else random.choice(["餐饮", "交通", "购物", "薪资"])
                    ),
                    description=desc,
                    record_type=record_type,
                    date=datetime.now() + timedelta(days=random.randint(-10, 10)),
                )

            # 执行搜索
            results = env["record_manager"].search_records(
                keyword=keyword if keyword.strip() else None,
                category=category if random.random() > 0.5 else None,
            )

            # 验证搜索结果
            if keyword.strip():
                # 检查包含关键词的结果
                if results:
                    # 只要不崩溃就算成功，Hypothesis会自动找出导致崩溃的输入
                    pass

        finally:
            if env:
                self.cleanup_temp_database(env)

    @hypothesis.given(
        start_offset=st.integers(min_value=-365, max_value=0),
        end_offset=st.integers(min_value=0, max_value=365),
        amount_filter=st.one_of(
            st.none(),
            st.tuples(
                st.floats(min_value=0, max_value=10000),
                st.floats(min_value=0, max_value=10000),
            ),
        ),
    )
    @hypothesis.settings(max_examples=100, deadline=None)
    def test_search_with_date_range(self, start_offset, end_offset, amount_filter):
        """测试带日期范围的搜索"""
        env = None
        try:
            env = self.setup_temp_database()
            end_offset = max(end_offset, start_offset)

            # 准备测试记录
            for i in range(20):
                record_date = datetime.now() + timedelta(days=random.randint(-400, 400))
                env["record_manager"].add_record(
                    amount=random.uniform(1, 5000),
                    category=random.choice(["餐饮", "交通", "购物", "薪资"]),
                    description=f"测试记录 {i}",
                    record_type=random.choice([RecordType.INCOME, RecordType.EXPENSE]),
                    date=record_date,
                )

            # 计算日期范围
            start_date = datetime.now() + timedelta(days=start_offset)
            end_date = datetime.now() + timedelta(days=end_offset)

            # 准备金额过滤条件
            min_amount = max_amount = None
            if amount_filter:
                min_amount, max_amount = amount_filter
                if min_amount > max_amount:
                    min_amount, max_amount = max_amount, min_amount

            # 执行搜索
            results = env["record_manager"].search_records(
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount,
            )

            # 验证结果
            if results:
                for record in results:
                    # 验证日期范围
                    assert start_date <= record.date <= end_date

                    # 验证金额范围
                    if min_amount is not None:
                        assert record.amount >= min_amount - 0.01  # 允许浮点误差
                    if max_amount is not None:
                        assert record.amount <= max_amount + 0.01  # 允许浮点误差

        finally:
            if env:
                self.cleanup_temp_database(env)
