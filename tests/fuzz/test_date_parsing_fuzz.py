from datetime import datetime

import hypothesis
from hypothesis import strategies as st

from . import BaseFuzzTest


class TestDateParsingFuzz(BaseFuzzTest):
    """模糊测试日期解析功能的健壮性"""

    @hypothesis.given(
        date_str=st.text(alphabet="0123456789-: .", min_size=10, max_size=30)
    )
    @hypothesis.settings(
        max_examples=200,
        deadline=None,
        suppress_health_check=[hypothesis.HealthCheck.too_slow],
    )
    def test_date_parsing_robustness(self, date_str):
        """测试日期解析对各种格式输入的健壮性"""
        env = None
        try:
            env = self.setup_temp_database()

            # 测试直接调用_parse_datetime方法
            parsed_date = env["storage"]._parse_datetime(date_str)

            # 验证返回的是datetime对象
            assert isinstance(parsed_date, datetime)

        except Exception as e:
            # 允许ValueError，这是正常处理无效日期的方式
            if not isinstance(e, (ValueError, TypeError)):
                raise
        finally:
            if env:
                self.cleanup_temp_database(env)

    @hypothesis.given(
        year=st.integers(min_value=1900, max_value=2100),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=31),
        hour=st.integers(min_value=0, max_value=23),
        minute=st.integers(min_value=0, max_value=59),
        second=st.integers(min_value=0, max_value=59),
        microsecond=st.integers(min_value=0, max_value=999999),
        use_microsecond=st.booleans(),
    )
    @hypothesis.settings(max_examples=100, deadline=None)
    def test_valid_date_formats(
        self, year, month, day, hour, minute, second, microsecond, use_microsecond
    ):
        """测试各种有效日期格式的解析"""
        env = None
        try:
            env = self.setup_temp_database()

            # 验证日期有效性
            try:
                valid_date = datetime(
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    microsecond if use_microsecond else 0,
                )
            except ValueError:
                # 无效日期组合（如2月30日）跳过
                return

            # 测试不同格式的日期字符串
            formats = [
                valid_date.strftime("%Y-%m-%d %H:%M:%S"),
                valid_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
                valid_date.strftime("%Y/%m/%d %H:%M:%S"),
                valid_date.strftime("%d-%m-%Y %H:%M:%S"),
                valid_date.strftime("%m/%d/%Y %I:%M:%S %p"),
            ]

            for date_str in formats:
                parsed_date = env["storage"]._parse_datetime(date_str)

                # 验证解析结果
                assert parsed_date.year == valid_date.year
                assert parsed_date.month == valid_date.month
                assert parsed_date.day == valid_date.day
                assert parsed_date.hour == valid_date.hour
                assert parsed_date.minute == valid_date.minute
                assert parsed_date.second == valid_date.second

                if use_microsecond:
                    # 微秒可能有舍入误差
                    assert abs(parsed_date.microsecond - valid_date.microsecond) < 1000

        finally:
            if env:
                self.cleanup_temp_database(env)
