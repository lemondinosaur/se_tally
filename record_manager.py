"""
记录管理模块，封装账目记录的CRUD操作
"""

import datetime
from typing import List, Optional

from data_storage import DataStorage
from record import Record, RecordType


class RecordManager:
    """记录管理器，提供账目记录的增删改查功能"""

    def __init__(self, storage: DataStorage = None):
        """初始化记录管理器

        Args:
            storage: 数据存储实例，如果为None则创建新实例
        """
        self.storage = storage or DataStorage()

    def add_record(
        self,
        amount: float,
        category: str,
        description: str,
        record_type: RecordType,
        date: datetime.datetime,
    ) -> int:
        """添加新账目记录

        Args:
            amount: 金额
            category: 分类
            description: 备注
            record_type: 记录类型（收入或支出）
            date: 日期

        Returns:
            新记录的ID
        """
        record = Record(
            amount=amount,
            category=category,
            description=description,
            record_type=record_type,
            date=date,
        )

        return self.storage.save_record(record)

    def get_record(self, record_id: int) -> Optional[Record]:
        """获取指定ID的账目记录

        Args:
            record_id: 记录ID

        Returns:
            对应的Record对象，如果不存在则返回None
        """
        return self.storage.get_record(record_id)

    def get_all_records(
        self, start_date: datetime.datetime = None, end_date: datetime.datetime = None
    ) -> List[Record]:
        """获取所有账目记录，可按日期范围筛选

        Args:
            start_date: 起始日期
            end_date: 结束日期

        Returns:
            Record对象列表
        """
        return self.storage.get_all_records(start_date, end_date)

    def update_record(
        self,
        record_id: int,
        amount: float,
        category: str,
        description: str,
        record_type: RecordType,
        date: datetime.datetime,
    ) -> bool:
        """更新账目记录

        Args:
            record_id: 要更新的记录ID
            amount: 金额
            category: 分类
            description: 备注
            record_type: 记录类型
            date: 日期

        Returns:
            更新是否成功
        """
        record = self.get_record(record_id)
        if not record:
            return False

        record.amount = amount
        record.category = category
        record.description = description
        record.type = record_type
        record.date = date

        return self.storage.update_record(record)

    def delete_record(self, record_id: int) -> bool:
        """删除账目记录

        Args:
            record_id: 要删除的记录ID

        Returns:
            删除是否成功
        """
        return self.storage.delete_record(record_id)

    def search_records(
        self,
        keyword: str = None,
        category: str = None,
        start_date: datetime.datetime = None,
        end_date: datetime.datetime = None,
        min_amount: float = None,
        max_amount: float = None,
        record_type: RecordType = None,
    ) -> List[Record]:
        """按条件搜索账目记录

        Args:
            keyword: 关键词
            category: 分类
            start_date: 起始日期
            end_date: 结束日期
            min_amount: 最小金额
            max_amount: 最大金额
            record_type: 记录类型

        Returns:
            符合条件的Record对象列表
        """
        return self.storage.search_records(
            keyword, category, start_date, end_date, min_amount, max_amount, record_type
        )

    def get_categories(self, record_type: RecordType = None) -> List[str]:
        """获取分类列表

        Args:
            record_type: 可选，指定获取收入或支出的分类

        Returns:
            分类名称列表
        """
        return self.storage.get_categories(record_type)
