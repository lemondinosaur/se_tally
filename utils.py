"""
工具函数模块，提供共用的辅助功能
"""

import os
import platform
from typing import Dict, List, Tuple

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt


# 根据操作系统选择合适的中文字体
def configure_fonts():
    """配置matplotlib字体以支持中文字和货币符号"""
    system = platform.system()

    font_path = None
    if system == "Windows":
        font_path = "SimHei"  # Windows
    elif system == "Darwin":  # macOS
        font_path = "Heiti TC"
    elif system == "Linux":
        # 尝试几种常见的Linux中文字体
        possible_fonts = ["WenQuanYi Zen Hei", "Droid Sans Fallback", "AR PL UKai CN"]
        for font in possible_fonts:
            fm.findfont(font, fontpaths=None, fallback_to_default=False)
            font_path = font
            break
        if font_path is None:
            font_path = "DejaVu Sans"  # 默认

    # 设置全局字体
    plt.rcParams["font.sans-serif"] = [
        font_path,
        "Microsoft YaHei",
        "SimSun",
        "Heiti TC",
        "Arial Unicode MS",
    ]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# 配置字体
configure_fonts()

# 预定义颜色方案
CATEGORY_COLORS = [
    "#FF6384",
    "#36A2EB",
    "#FFCE56",
    "#4BC0C0",
    "#9966FF",
    "#FF9F40",
    "#8E44AD",
    "#2ECC71",
    "#E74C3C",
    "#3498DB",
    "#1ABC9C",
    "#F39C12",
]


def get_chinese_period_name(period_type: str) -> str:
    """获取周期类型的中文名称

    Args:
        period_type: 周期类型（day/week/month）

    Returns:
        中文名称
    """
    period_map = {"day": "日", "week": "周", "month": "月"}
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

    return f"{amount:,.2f}"


def create_pie_chart(
    data: Dict[str, float],
    title: str = "支出分类比例",
    show_title: bool = True,
    figsize: Tuple[int, int] = (7, 7),
    radius: float = 0.8,
) -> plt.Figure:
    """创建饼图

    Args:
         数据字典，键为分类名称，值为金额
        title: 图表标题
        show_title: 是否在图表内部显示标题
        figsize: 图表大小
        radius: 饼图半径比例(0-1)

    Returns:
        matplotlib Figure对象
    """
    # 过滤金额为0的项
    filtered_data = {k: v for k, v in data.items() if v > 0}
    if not filtered_data:
        # 创建空图表
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(
            0.5, 0.5, "暂无数据", ha="center", va="center", fontsize=12, color="#666"
        )
        ax.axis("off")
        if show_title:
            fig.suptitle(title, fontsize=18, fontweight="bold", y=0.95)
        return fig

    labels = list(filtered_data.keys())
    sizes = list(filtered_data.values())

    # 生成颜色
    colors = [CATEGORY_COLORS[i % len(CATEGORY_COLORS)] for i in range(len(labels))]

    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)

    # 饼图 - 使用 radius 参数控制饼大小
    wedges = ax.pie(
        sizes,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%" if pct > 3 else "",
        colors=colors,
        radius=radius,  # 关键：缩小饼图半径
        startangle=60,
        textprops={"fontsize": 12},
        explode=[0.02] * len(labels),
    )

    # 等比例显示
    ax.axis("equal")

    # 仅在需要时设置标题
    if show_title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=20)

    # 添加图例
    if len(labels) > 8:
        ax.legend(
            wedges,
            labels,
            title="分类",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=13,
        )

    plt.tight_layout()
    return fig


def create_line_chart(
    trend_data: List[Dict],
    title: str = "收支趋势",
    show_title: bool = True,
    figsize: Tuple[int, int] = (10, 5),
) -> plt.Figure:
    """创建折线图

    Args:
        trend_data: 趋势数据列表
        title: 图表标题
        show_title: 是否在图表内部显示标题
        figsize: 图表大小

    Returns:
        matplotlib Figure对象
    """
    if not trend_data:
        # 创建空图表
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(
            0.5, 0.5, "暂无数据", ha="center", va="center", fontsize=16, color="#666"
        )
        ax.axis("off")
        if show_title:
            fig.suptitle(title, fontsize=18, fontweight="bold", y=0.95)
        return fig

    periods = [item["period"] for item in trend_data]
    incomes = [item["income"] for item in trend_data]
    expenses = [item["expense"] for item in trend_data]

    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)

    # 添加折线图 - 这是关键修复！
    ax.plot(periods, incomes, label="收入", color="#2ECC71", marker="o", linewidth=2)
    ax.plot(periods, expenses, label="支出", color="#E74C3C", marker="s", linewidth=2)

    # 添加数据标签
    for i, (_, income, expense) in enumerate(zip(periods, incomes, expenses)):
        if income > 0:
            ax.annotate(
                f"{format_currency(income)}",
                (i, income),
                xytext=(0, 12),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                bbox={
                    "boxstyle": "round,pad=0.3",
                    "fc": "white",
                    "ec": "#2ECC71",
                    "alpha": 0.8,
                },
            )
        if expense > 0:
            ax.annotate(
                f"{format_currency(expense)}",
                (i, expense),
                xytext=(0, -15),
                textcoords="offset points",
                ha="center",
                va="top",
                fontsize=9,
                bbox={
                    "boxstyle": "round,pad=0.3",
                    "fc": "white",
                    "ec": "#E74C3C",
                    "alpha": 0.8,
                },
            )

    # 仅在需要时设置标题
    if show_title:
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    ax.set_xlabel("时间", fontsize=12, labelpad=10)
    ax.set_ylabel("金额 (元)", fontsize=12, labelpad=10)

    # 网格线
    ax.grid(True, linestyle="--", alpha=0.7, which="both")

    # Y轴从0开始
    ax.set_ylim(bottom=0)

    # 美化Y轴
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))

    # 图例 - 现在有图形元素可以显示了
    ax.legend(
        loc="upper left", frameon=True, shadow=True, fontsize=11, title_fontsize=12
    )

    # 旋转X轴标签
    plt.xticks(rotation=45, ha="right")

    # 紧凑布局
    plt.tight_layout()
    return fig


def ensure_directory_exists(directory_path: str):
    """确保目录存在，如果不存在则创建

    Args:
        directory_path: 目录路径
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
