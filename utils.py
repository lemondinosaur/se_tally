"""
工具函数模块，提供共用的辅助功能
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import platform
import matplotlib.font_manager as fm
from typing import Dict, List, Tuple


# 根据操作系统选择合适的中文字体
def configure_fonts():
    """配置matplotlib字体以支持中文字和货币符号"""
    system = platform.system()
    
    font_path = None
    if system == 'Windows':
        font_path = 'SimHei'  # Windows
    elif system == 'Darwin':  # macOS
        font_path = 'Heiti TC'
    elif system == 'Linux':
        # 尝试几种常见的Linux中文字体
        possible_fonts = ['WenQuanYi Zen Hei', 'Droid Sans Fallback', 'AR PL UKai CN']
        for font in possible_fonts:
            try:
                fm.findfont(font, fontpaths=None, fallback_to_default=False)
                font_path = font
                break
            except:
                continue
        if font_path is None:
            font_path = 'DejaVu Sans'  # 默认
    
    # 设置全局字体
    plt.rcParams['font.sans-serif'] = [font_path, 'Microsoft YaHei', 'SimSun', 'Heiti TC', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 配置字体
configure_fonts()

# 预定义颜色方案
CATEGORY_COLORS = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
    '#8E44AD', '#2ECC71', '#E74C3C', '#3498DB', '#1ABC9C', '#F39C12'
]

def get_chinese_period_name(period_type: str) -> str:
    """获取周期类型的中文名称
    
    Args:
        period_type: 周期类型（day/week/month）
        
    Returns:
        中文名称
    """
    period_map = {
        "day": "日",
        "week": "周",
        "month": "月"
    }
    return period_map.get(period_type, "未知")

def format_currency(amount: float, use_symbol=True) -> str:
    """格式化金额，添加千分位分隔符，保留两位小数
    
    Args:
        amount: 金额
        use_symbol: 是否使用货币符号
        
    Returns:
        格式化后的金额字符串
    """
    if use_symbol:
        currency_symbol = "￥"
        return f"{currency_symbol}{amount:,.2f}"
    else:
        return f"{amount:,.2f}"

def create_pie_chart(category_expenses: Dict[str, float], title: str = "支出分类比例", 
                    figsize: Tuple[int, int] = (6, 6)) -> plt.Figure:
    """创建饼图
    
    Args:
        category_expenses: 分类-金额映射字典
        title: 图表标题
        figsize: 图表大小
        
    Returns:
        matplotlib Figure对象
    """
    # 过滤金额为0的项
    filtered_data = {k: v for k, v in category_expenses.items() if v > 0}
    if not filtered_data:
        # 创建空图表
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    labels = list(filtered_data.keys())
    sizes = list(filtered_data.values())
    
    # 创建颜色列表，根据分类数量生成不同颜色
    colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 饼图
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', colors=colors,
        startangle=90, textprops={'fontsize': 9}
    )
    
    # 等比例显示，使饼图为圆形
    ax.axis('equal')
    
    # 设置标题
    ax.set_title(title, fontsize=14, pad=20)
    
    # 添加图例（当标签过多时更清晰）
    if len(labels) > 5:
        ax.legend(wedges, labels,
                 title="分类",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    return fig

def create_line_chart(trend_data: List[Dict], title: str = "收支趋势", 
                     figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """创建折线图
    
    Args:
        trend_ 趋势数据列表
        title: 图表标题
        figsize: 图表大小
        
    Returns:
        matplotlib Figure对象
    """
    if not trend_data:
        # 创建空图表
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    periods = [item["period"] for item in trend_data]
    incomes = [item["income"] for item in trend_data]
    expenses = [item["expense"] for item in trend_data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制折线
    ax.plot(periods, incomes, marker='o', linestyle='-', linewidth=2, 
            label='收入', color='#2ECC71')
    ax.plot(periods, expenses, marker='o', linestyle='-', linewidth=2, 
            label='支出', color='#E74C3C')
    
    # 添加数据标签
    for i, (income, expense) in enumerate(zip(incomes, expenses)):
        if income > 0:
            ax.annotate(f'{format_currency(income)}', 
                       (periods[i], income),
                       textcoords="offset points",
                       xytext=(0,10),
                       ha='center',
                       fontsize=8)
        if expense > 0:
            ax.annotate(f'{format_currency(expense)}', 
                       (periods[i], expense),
                       textcoords="offset points",
                       xytext=(0,-15),
                       ha='center',
                       fontsize=8)
    
    # 设置标题和标签
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel('时间', fontsize=10)
    ax.set_ylabel('金额 (元)', fontsize=10)
    
    # 网格线
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 图例
    ax.legend()
    
    # 旋转x轴标签，避免重叠
    plt.xticks(rotation=45)
    
    # 自动调整布局
    plt.tight_layout()
    return fig

def ensure_directory_exists(directory_path: str):
    """确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)