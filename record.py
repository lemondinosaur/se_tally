"""
账目记录类定义，遵循Google Python风格指南
"""

from enum import Enum
from datetime import datetime


class RecordType(Enum):
    """账目类型枚举：收入或支出"""
    INCOME = "收入"
    EXPENSE = "支出"


class Record:
    """账目记录类，存储单条账目信息"""
    
    def __init__(self, amount: float, category: str, description: str,
                 record_type: RecordType, date: datetime = None, record_id: int = None):
        """初始化账目记录
        
        Args:
            amount: 金额
            category: 分类（如餐饮、交通等）
            description: 备注描述
            record_type: 记录类型（收入或支出）
            date: 日期，默认为当前时间
            record_id: 记录ID，数据库主键，新建记录时可为None
        """
        self.id = record_id
        self.amount = amount
        self.category = category
        self.description = description
        self.type = record_type
        self.date = date if date else datetime.now()
    
    def __str__(self):
        """返回记录的字符串表示"""
        return (f"ID: {self.id}, 金额: {self.amount}, 类别: {self.category}, "
                f"备注: {self.description}, 类型: {self.type.value}, 日期: {self.date}")