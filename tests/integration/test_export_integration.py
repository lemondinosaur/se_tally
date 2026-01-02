import csv
import os
import tempfile
from datetime import datetime, timedelta

from record import RecordType

from . import BaseIntegrationTest


class TestDataExportIntegration(BaseIntegrationTest):
    """测试数据导出功能与文件系统的集成"""

    def test_csv_export_with_multiple_records(self, record_manager, test_db):
        """测试多条记录的CSV导出功能"""
        # 创建测试记录
        records = self.create_test_records(record_manager, count=15)
        assert len(records) == 15

        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        export_path = os.path.join(temp_dir, "test_export.csv")

        try:
            # 导出数据
            test_db.export_to_csv(export_path)

            # 验证文件存在
            assert os.path.exists(export_path)

            # 验证文件内容
            with open(export_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.reader(csvfile)

                # 检查表头
                headers = next(reader)
                assert headers == ["ID", "日期", "类型", "分类", "金额", "备注"]

                # 检查数据行
                rows = list(reader)
                assert len(rows) >= 15  # 应包含所有测试记录

                # 验证数据格式
                for row in rows:
                    assert len(row) == 6  # 6列数据
                    record_id = int(row[0])
                    date_str = row[1]
                    record_type = row[2]
                    category = row[3]
                    amount = float(row[4])
                    description = row[5]

                    # 验证基本格式
                    assert record_id > 0
                    datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")  # 验证日期格式
                    assert record_type in [
                        RecordType.INCOME.value,
                        RecordType.EXPENSE.value,
                    ]
                    assert category  # 分类不为空
                    assert amount > 0  # 金额大于0
                    assert description  # 备注不为空

        finally:
            # 清理临时文件
            if os.path.exists(export_path):
                os.remove(export_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    def test_export_with_filtered_records(self, record_manager, test_db):
        """测试筛选条件下的数据导出"""
        # 创建测试记录
        self.create_test_records(record_manager, count=20)

        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        export_path = os.path.join(temp_dir, "filtered_export.csv")

        try:
            # 按条件筛选记录
            today = datetime.now()
            yesterday = today - timedelta(days=1)

            # 获取昨日和今日的记录
            filtered_records = record_manager.search_records(
                start_date=yesterday.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=today.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                ),
                min_amount=50,
            )

            # 导出筛选后的记录
            test_db.export_to_csv(export_path, filtered_records)

            # 验证导出文件
            with open(export_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # 跳过表头

                exported_count = 0
                for row in reader:
                    exported_count += 1
                    amount = float(row[4])
                    date_str = row[1]
                    record_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

                    # 验证导出的记录符合筛选条件
                    assert amount >= 50
                    assert yesterday.date() <= record_date.date() <= today.date()

                # 验证导出数量
                assert exported_count == len(filtered_records)

        finally:
            # 清理临时文件
            if os.path.exists(export_path):
                os.remove(export_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
