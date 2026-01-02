from datetime import datetime, timedelta
from decimal import Decimal, getcontext

import hypothesis
from hypothesis import strategies as st

from record import RecordType

from . import BaseFuzzTest


class TestAmountProcessingFuzz(BaseFuzzTest):
    """模糊测试金额处理功能的健壮性"""

    @hypothesis.given(
        amount=st.floats(
            min_value=0.001,
            max_value=1000000000.0,
            allow_nan=False,
            allow_infinity=False,
        ),
        operation_count=st.integers(min_value=1, max_value=10),
    )
    @hypothesis.settings(max_examples=150, deadline=None)
    def test_amount_precision(self, amount, operation_count):
        """测试金额计算的精度问题"""
        env = None
        try:
            env = self.setup_temp_database()

            # 使用Decimal进行精确计算
            getcontext().prec = 28
            precise_amount = Decimal(str(amount)).quantize(Decimal("0.01"))

            # 创建多条记录
            record_ids = []
            for i in range(operation_count):
                record_id = env["record_manager"].add_record(
                    amount=float(precise_amount),
                    category="测试",
                    description=f"精确金额测试 {i}",
                    record_type=RecordType.EXPENSE,
                    date=datetime.now() + timedelta(days=i),
                )
                record_ids.append(record_id)

            # 验证每条记录的金额
            for record_id in record_ids:
                record = env["record_manager"].get_record(record_id)
                assert abs(record.amount - float(precise_amount)) < 0.001

            # 验证汇总计算
            all_records = env["record_manager"].get_all_records()
            total = sum(r.amount for r in all_records)
            expected_total = float(precise_amount) * len(record_ids)

            # 允许浮点误差
            assert abs(total - expected_total) < 0.01 * len(record_ids)

        finally:
            if env:
                self.cleanup_temp_database(env)

    @hypothesis.given(
        amounts=st.lists(
            st.floats(min_value=0.01, max_value=10000.0), min_size=10, max_size=100
        ),
        category=st.sampled_from(["餐饮", "交通", "购物", "薪资", "兼职", "理财"]),
    )
    @hypothesis.settings(max_examples=100, deadline=None)
    def test_amount_boundaries(self, amounts, category):
        """测试金额边界条件"""
        env = None
        try:
            env = self.setup_temp_database()

            # 测试极端小值
            tiny_amount = 0.001
            tiny_id = env["record_manager"].add_record(
                amount=tiny_amount,
                category=category,
                description="极小金额测试",
                record_type=RecordType.EXPENSE,
                date=datetime.now(),
            )

            tiny_record = env["record_manager"].get_record(tiny_id)
            # 验证极小金额不会丢失
            assert tiny_record.amount > 0

            # 测试大额记录
            large_amount = 999999999.99
            large_id = env["record_manager"].add_record(
                amount=large_amount,
                category=category,
                description="大额记录测试",
                record_type=RecordType.INCOME,
                date=datetime.now(),
            )

            large_record = env["record_manager"].get_record(large_id)
            # 验证大额记录
            assert large_record.amount > 1000000

            # 批量添加记录
            for amount in amounts:
                env["record_manager"].add_record(
                    amount=amount,
                    category=category,
                    description="批量测试",
                    record_type=RecordType.EXPENSE,
                    date=datetime.now(),
                )

            # 验证统计汇总
            summary = env["statistics_engine"].get_daily_summary()
            assert summary["total_expense"] >= 0
            assert summary["total_income"] >= 0

        finally:
            if env:
                self.cleanup_temp_database(env)
