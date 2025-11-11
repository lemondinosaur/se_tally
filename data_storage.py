"""
数据存储模块，负责账目数据的持久化
使用SQLite数据库进行本地存储
"""

import os
import sqlite3
import csv
import datetime
from typing import List, Optional
from record import Record, RecordType


class DataStorage:
    """数据存储类，封装数据库操作"""
    
    def __init__(self, db_path: str = None):
        """初始化数据存储，创建数据库连接和表结构
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            # 获取当前脚本所在目录
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 创建data目录
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            # 设置数据库文件路径
            db_path = os.path.join(data_dir, 'account_book.db')
            
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库，创建所需表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建账目记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            date TIMESTAMP NOT NULL
        )
        """)
        
        # 创建分类预设表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense'))
        )
        """)
        
        # 插入默认分类
        default_categories = [
            ('薪资', 'income'), ('兼职', 'income'), ('理财', 'income'), ('其他收入', 'income'),
            ('餐饮', 'expense'), ('交通', 'expense'), ('购物', 'expense'), ('娱乐', 'expense'),
            ('医疗', 'expense'), ('住房', 'expense'), ('通讯', 'expense'), ('其他支出', 'expense')
        ]
        
        for category, category_type in default_categories:
            cursor.execute("""
            INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)
            """, (category, category_type))
        
        conn.commit()
        conn.close()
    
    def save_record(self, record: Record) -> int:
        """保存账目记录到数据库
        
        Args:
            record: 要保存的账目记录对象
            
        Returns:
            保存记录的ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO records (amount, category, description, type, date)
        VALUES (?, ?, ?, ?, ?)
        """, (
            record.amount,
            record.category,
            record.description,
            'income' if record.type == RecordType.INCOME else 'expense',
            record.date.strftime("%Y-%m-%d %H:%M:%S.%f")
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_record(self, record_id: int) -> Optional[Record]:
        """根据ID获取账目记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            对应的Record对象，如果不存在则返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Record(
            amount=row[1],
            category=row[2],
            description=row[3],
            record_type=RecordType.INCOME if row[4] == 'income' else RecordType.EXPENSE,
            date=self._parse_datetime(row[5]),
            record_id=row[0]
        )
    
    def get_all_records(self, start_date: datetime.datetime = None, 
                       end_date: datetime.datetime = None) -> List[Record]:
        """获取所有账目记录，可按日期范围筛选
        
        Args:
            start_date: 起始日期，可选
            end_date: 结束日期，可选
            
        Returns:
            Record对象列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM records"
        params = []
        
        if start_date or end_date:
            query += " WHERE"
            conditions = []
            
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
            
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
            
            query += " " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            try:
                records.append(Record(
                    amount=row[1],
                    category=row[2],
                    description=row[3],
                    record_type=RecordType.INCOME if row[4] == 'income' else RecordType.EXPENSE,
                    date=self._parse_datetime(row[5]),
                    record_id=row[0]
                ))
            except ValueError as e:
                print(f"Error parsing date for record {row[0]}: {e}")
        
        return records
    
    def update_record(self, record: Record) -> bool:
        """更新已存在的账目记录
        
        Args:
            record: 要更新的账目记录对象
            
        Returns:
            更新是否成功
        """
        if not record.id:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE records SET amount = ?, category = ?, description = ?, 
        type = ?, date = ? WHERE id = ?
        """, (
            record.amount,
            record.category,
            record.description,
            'income' if record.type == RecordType.INCOME else 'expense',
            record.date.strftime("%Y-%m-%d %H:%M:%S.%f"),
            record.id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_record(self, record_id: int) -> bool:
        """删除账目记录
        
        Args:
            record_id: 要删除的记录ID
            
        Returns:
            删除是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def search_records(self, keyword: str = None, category: str = None,
                      start_date: datetime.datetime = None, end_date: datetime.datetime = None,
                      min_amount: float = None, max_amount: float = None,
                      record_type: RecordType = None) -> List[Record]:
        """按条件搜索账目记录
        
        Args:
            keyword: 关键词（在备注或分类中搜索）
            category: 分类
            start_date: 起始日期
            end_date: 结束日期
            min_amount: 最小金额
            max_amount: 最大金额
            record_type: 记录类型
            
        Returns:
            符合条件的Record对象列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM records WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND (description LIKE ? OR category LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        if min_amount is not None:
            query += " AND amount >= ?"
            params.append(min_amount)
        
        if max_amount is not None:
            query += " AND amount <= ?"
            params.append(max_amount)
        
        if record_type:
            type_str = 'income' if record_type == RecordType.INCOME else 'expense'
            query += " AND type = ?"
            params.append(type_str)
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            try:
                records.append(Record(
                    amount=row[1],
                    category=row[2],
                    description=row[3],
                    record_type=RecordType.INCOME if row[4] == 'income' else RecordType.EXPENSE,
                    date=self._parse_datetime(row[5]),
                    record_id=row[0]
                ))
            except ValueError as e:
                print(f"Error parsing date for record {row[0]}: {e}")
        
        return records
    
    def export_to_csv(self, file_path: str, records: List[Record] = None):
        """将账目记录导出为CSV文件
        
        Args:
            file_path: 导出文件路径
            records: 要导出的记录列表，如果为None则导出所有记录
        """
        if records is None:
            records = self.get_all_records()
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', '日期', '类型', '分类', '金额', '备注'])
            
            for record in records:
                writer.writerow([
                    record.id,
                    record.date.strftime("%Y-%m-%d %H:%M:%S"),
                    record.type.value,
                    record.category,
                    record.amount,
                    record.description
                ])
    
    def get_categories(self, record_type: RecordType = None) -> List[str]:
        """获取分类列表
        
        Args:
            record_type: 可选，指定获取收入或支出的分类
            
        Returns:
            分类名称列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT name FROM categories"
        params = []
        
        if record_type:
            type_str = 'income' if record_type == RecordType.INCOME else 'expense'
            query += " WHERE type = ?"
            params.append(type_str)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def _parse_datetime(self, date_str):
        """安全解析数据库中的时间字符串，支持带或不带微秒
        
        Args:
            date_str: 日期时间字符串
            
        Returns:
            datetime 对象
        """
        if not date_str:
            return datetime.datetime.now()
        
        try:
            # 尝试带微秒格式
            if '.' in date_str:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            # 尝试不带微秒格式
            return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError) as e:
            print(f"日期解析错误: {e}, 使用当前时间")
            return datetime.datetime.now()