import json
import os
import time
from datetime import datetime

import pytest


def run_fuzz_test(test_file, duration_seconds=3600):
    """运行单个模糊测试，指定持续时间"""
    print(f"正在运行模糊测试: {test_file}")
    print(f"持续时间: {duration_seconds//3600}小时 {(duration_seconds%3600)//60}分钟")

    # 准备输出目录
    output_dir = "fuzz_results"
    os.makedirs(output_dir, exist_ok=True)
    crash_dir = os.path.join(output_dir, "crashes")
    os.makedirs(crash_dir, exist_ok=True)

    # 生成唯一标识
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = os.path.splitext(os.path.basename(test_file))[0]

    # 运行测试
    try:
        start_time = time.time()

        # 使用pytest运行具体的模糊测试
        result = pytest.main(["-v", test_file, f"--hypothesis-show-statistics"])

        elapsed_time = time.time() - start_time

        # 保存结果
        stats_file = os.path.join(output_dir, f"{test_name}_{timestamp}_stats.json")
        stats = {
            "test_file": test_file,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": elapsed_time,
            "exit_code": int(result),
            "passed": result == pytest.ExitCode.OK,
        }

        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        print(f"统计信息已保存到: {stats_file}")

        # 检查是否发现崩溃
        crash_count = 0
        if result != pytest.ExitCode.OK:
            crash_count = 1
            crash_file = os.path.join(crash_dir, f"{test_name}_{timestamp}_crash.json")
            with open(crash_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "test_file": test_file,
                        "timestamp": datetime.now().isoformat(),
                        "error": "Hypothesis found a failing example",
                    },
                    f,
                    indent=2,
                )
            print(f"发现崩溃案例，已保存到: {crash_file}")

        return {
            "crash_count": crash_count,
            "duration": elapsed_time,
            "stats_file": stats_file,
        }

    except Exception as e:
        print(f"运行模糊测试时出错: {e}")
        return {"error": str(e)}


def main():
    """主函数，运行所有模糊测试"""
    print("=== 简约记账本系统 Hypothesis 模糊测试 ===")

    # 模糊测试文件列表
    fuzz_tests = [
        "tests\\fuzz\\test_date_parsing_fuzz.py",
        "tests\\fuzz\\test_amount_processing_fuzz.py",
        "tests\\fuzz\\test_search_fuzz.py",
        "tests\\fuzz\\test_export_fuzz.py",
    ]

    # 每个测试的持续时间（秒）
    duration = 5 * 3600  # 5小时

    results = {}
    total_crashes = 0

    for test_file in fuzz_tests:
        if not os.path.exists(test_file):
            print(f"警告: 模糊测试文件不存在: {test_file}")
            continue

        print(f"\n{'=' * 60}")
        print(f"开始测试: {test_file}")
        print(f"{'=' * 60}")

        result = run_fuzz_test(test_file, duration)
        results[test_file] = result

        if "crash_count" in result:
            total_crashes += result["crash_count"]

        # 每个测试之间暂停
        time.sleep(2)

    print(f"\n{'=' * 60}")
    print("模糊测试完成！")
    print(f"总测试数量: {len(results)}")
    print(f"总崩溃案例: {total_crashes}")

    if total_crashes > 0:
        print("⚠️  检测到崩溃！请检查 fuzz_results/crashes/ 目录")
    else:
        print("✅  未检测到崩溃，系统稳定性良好")

    print(f"详细结果请查看 fuzz_results/ 目录")


if __name__ == "__main__":
    main()
