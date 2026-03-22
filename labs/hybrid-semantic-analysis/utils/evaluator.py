"""
A/B测试评估工具

对比三种方案的:
- 时间成本
- Token成本
- 标注质量
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.base import (
    parse_tagged_text,
    calculate_metrics,
    verify_text_integrity,
)


class Evaluator:
    """评估器"""

    def __init__(self, ground_truth_file: str):
        """
        Args:
            ground_truth_file: 标准答案文件路径
        """
        self.ground_truth_file = Path(ground_truth_file)

        # 加载标准答案
        with open(self.ground_truth_file, encoding="utf-8") as f:
            ground_truth_text = f.read()

        self.gold_entities = parse_tagged_text(ground_truth_text)
        print(f"加载标准答案: {len(self.gold_entities)} 个实体")

    def evaluate_file(self, result_file: str, method_name: str) -> Dict:
        """
        评估单个结果文件

        Args:
            result_file: 结果文件路径
            method_name: 方法名称

        Returns:
            评估结果字典
        """
        result_file = Path(result_file)

        if not result_file.exists():
            print(f"结果文件不存在: {result_file}")
            return None

        # 加载结果
        with open(result_file, encoding="utf-8") as f:
            result_text = f.read()

        # 解析实体
        pred_entities = parse_tagged_text(result_text)

        # 计算指标
        metrics = calculate_metrics(pred_entities, self.gold_entities)

        # 验证文本完整性
        # (需要原文,这里简化处理)
        integrity_ok = True  # TODO: 实际验证

        # 构建评估结果
        evaluation = {
            "method": method_name,
            "file": str(result_file),
            "entity_count": len(pred_entities),
            "gold_entity_count": len(self.gold_entities),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "tp": metrics["tp"],
            "fp": metrics["fp"],
            "fn": metrics["fn"],
            "text_integrity": integrity_ok,
        }

        return evaluation

    def compare_methods(self, results: List[Dict]) -> Dict:
        """
        对比多个方法的结果

        Args:
            results: 评估结果列表

        Returns:
            对比报告
        """
        comparison = {
            "methods": [],
            "summary": {},
        }

        for result in results:
            if result is None:
                continue

            method_name = result["method"]
            comparison["methods"].append({
                "name": method_name,
                "precision": result["precision"],
                "recall": result["recall"],
                "f1": result["f1"],
                "entity_count": result["entity_count"],
            })

        # 找出最佳方法
        if comparison["methods"]:
            best_f1 = max(comparison["methods"], key=lambda x: x["f1"])
            best_precision = max(comparison["methods"], key=lambda x: x["precision"])
            best_recall = max(comparison["methods"], key=lambda x: x["recall"])

            comparison["summary"] = {
                "best_f1": best_f1["name"],
                "best_precision": best_precision["name"],
                "best_recall": best_recall["name"],
            }

        return comparison

    def generate_report(
        self,
        comparison: Dict,
        metadata_list: List[Dict],
        output_file: str
    ):
        """
        生成对比报告

        Args:
            comparison: 对比结果
            metadata_list: 元数据列表(时间/token等)
            output_file: 输出文件路径
        """
        output_file = Path(output_file)

        # 合并数据
        full_report = {
            "comparison": comparison,
            "metadata": metadata_list,
        }

        # 保存JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(full_report, f, ensure_ascii=False, indent=2)

        print(f"\n对比报告已保存: {output_file}")

        # 打印摘要
        self._print_summary(comparison, metadata_list)

    def _print_summary(self, comparison: Dict, metadata_list: List[Dict]):
        """打印摘要表格"""
        print("\n" + "=" * 80)
        print("A/B测试对比报告")
        print("=" * 80)

        # 表头
        print(f"\n{'方法':<20} {'精确率':<10} {'召回率':<10} {'F1':<10} {'耗时(秒)':<12} {'Token':<10}")
        print("-" * 80)

        # 合并数据
        method_data = {}
        for item in comparison["methods"]:
            method_data[item["name"]] = item

        for meta in metadata_list:
            method_name = meta.get("method", "unknown")
            if method_name in method_data:
                method_data[method_name].update({
                    "time": meta.get("time_seconds", 0),
                    "tokens": meta.get("token_count", 0),
                })

        # 打印各方法
        for method_name, data in method_data.items():
            precision = data.get("precision", 0) * 100
            recall = data.get("recall", 0) * 100
            f1 = data.get("f1", 0) * 100
            time_sec = data.get("time", 0)
            tokens = data.get("tokens", 0)

            print(
                f"{method_name:<20} "
                f"{precision:>8.2f}% "
                f"{recall:>8.2f}% "
                f"{f1:>8.2f}% "
                f"{time_sec:>10.2f} "
                f"{tokens:>10}"
            )

        # 打印最佳方法
        print("\n" + "-" * 80)
        print("最佳方法:")
        summary = comparison.get("summary", {})
        print(f"  - F1最高: {summary.get('best_f1', 'N/A')}")
        print(f"  - 精确率最高: {summary.get('best_precision', 'N/A')}")
        print(f"  - 召回率最高: {summary.get('best_recall', 'N/A')}")
        print("=" * 80)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="评估标注结果")
    parser.add_argument(
        "--ground-truth",
        default="data/ground_truth.tagged.md",
        help="标准答案文件"
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="结果目录"
    )
    parser.add_argument(
        "--output",
        default="results/comparison.json",
        help="输出报告文件"
    )

    args = parser.parse_args()

    # 创建评估器
    base_dir = Path(__file__).parent.parent
    ground_truth = base_dir / args.ground_truth

    if not ground_truth.exists():
        print(f"标准答案不存在: {ground_truth}")
        print("请先创建标准答案文件")
        return

    evaluator = Evaluator(str(ground_truth))

    # 评估各方法
    results_dir = base_dir / args.results_dir

    methods = [
        ("method_a_ltp", "method_a_ltp_result.tagged.md"),
        ("method_b_hybrid", "method_b_hybrid_result.tagged.md"),
        ("method_c_llm", "method_c_llm_result.tagged.md"),
    ]

    evaluation_results = []
    metadata_list = []

    for method_name, filename in methods:
        result_file = results_dir / filename
        print(f"\n评估 {method_name}...")

        eval_result = evaluator.evaluate_file(result_file, method_name)
        if eval_result:
            evaluation_results.append(eval_result)

            # 模拟元数据(实际应从结果中读取)
            metadata_list.append({
                "method": method_name,
                "time_seconds": 0,  # TODO: 从实际运行中获取
                "token_count": 0,
            })

    # 对比
    if evaluation_results:
        comparison = evaluator.compare_methods(evaluation_results)

        # 生成报告
        output_file = base_dir / args.output
        evaluator.generate_report(comparison, metadata_list, str(output_file))
    else:
        print("\n没有找到任何结果文件")


if __name__ == "__main__":
    main()
