import csv
import os
import random
import shutil
import tempfile
from datetime import datetime, timedelta

import hypothesis
import pytest
from hypothesis import strategies as st

from record import RecordType

from . import BaseFuzzTest


class TestExportFuzz(BaseFuzzTest):
    """模糊测试数据导出功能的健壮性"""

    @hypothesis.given(
        record_count=st.integers(min_value=0, max_value=200),
        special_chars=st.text(
            alphabet="!@#$%^&*()_+-=[]{}|;:,.<>/?\\'\"", min_size=0, max_size=20
        ),
        contains_null=st.booleans(),
    )
    @hypothesis.settings(max_examples=100, deadline=None)
    def test_csv_export_robustness(self, record_count, special_chars, contains_null):
        """测试CSV导出对特殊字符和边界条件的处理"""
        env = None
        temp_dir = None
        export_path = None

        try:
            env = self.setup_temp_database()
            temp_dir = tempfile.mkdtemp()
            export_path = os.path.join(temp_dir, "fuzz_export.csv")

            # 创建包含特殊字符的记录
            for i in range(record_count):
                category = f"分类{special_chars}{i}"
                description = f"描述{special_chars}{i}"

                if contains_null and i == 0:
                    # 包含空值
                    category = ""
                    description = ""

                env["record_manager"].add_record(
                    amount=random.uniform(1.0, 10000.0),
                    category=category,
                    description=description,
                    record_type=random.choice([RecordType.INCOME, RecordType.EXPENSE]),
                    date=datetime.now() + timedelta(days=random.randint(-365, 365)),
                )

            # 导出数据
            env["storage"].export_to_csv(export_path)

            # 验证文件存在
            assert os.path.exists(export_path)

            # 验证CSV格式
            with open(export_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.reader(csvfile)

                # 检查表头
                headers = next(reader)
                assert headers == ["ID", "日期", "类型", "分类", "金额", "备注"]

                # 验证所有行
                for row in reader:
                    assert len(row) == 6  # 6列数据
                    assert row[0].isdigit()  # ID是数字

                    # 验证日期格式
                    try:
                        datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # 允许其他格式
                        pass

                    # 验证金额
                    try:
                        float(row[4])
                    except ValueError:
                        pytest.fail(f"无效的金额格式: {row[4]}")

        finally:
            if export_path and os.path.exists(export_path):
                os.remove(export_path)
            if temp_dir and os.path.exists(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
            if env:
                self.cleanup_temp_database(env)

    @hypothesis.given(
        export_path=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.\\/",
            min_size=5,
            max_size=100,
        )
    )
    @hypothesis.settings(max_examples=50, deadline=None)
    def test_export_path_handling(self, export_path):
        """测试不同导出路径的处理"""
        env = None
        temp_dir = None

        try:
            env = self.setup_temp_database()
            temp_dir = tempfile.mkdtemp()

            # 构造绝对路径
            if ":" not in export_path and not export_path.startswith("/"):
                export_path = os.path.join(temp_dir, export_path)

            # 确保目录存在
            export_dir = os.path.dirname(export_path)
            if export_dir and not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir, exist_ok=True)
                except:
                    # 某些路径可能无效，跳过测试
                    return

            # 添加.csv扩展名
            if not export_path.lower().endswith(".csv"):
                export_path += ".csv"

            # 尝试导出
            try:
                env["storage"].export_to_csv(export_path)

                # 验证导出成功
                assert os.path.exists(export_path)

                # 验证文件大小
                file_size = os.path.getsize(export_path)
                assert file_size > 0

            except Exception as e:
                # 允许因无效路径导致的错误
                valid_error_types = (OSError, IOError, ValueError, TypeError)
                assert isinstance(e, valid_error_types), f"意外错误类型: {type(e)}"

        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            if env:
                self.cleanup_temp_database(env)
