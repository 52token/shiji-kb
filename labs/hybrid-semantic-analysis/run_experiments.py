#!/usr/bin/env python3
"""
运行完整的A/B测试实验

流程:
1. 运行方案A (本地模型)
2. 运行方案B (混合方案)
3. 运行方案C (纯LLM)
4. 评估对比结果
"""

import sys
import json
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from methods.method_a_local import LTPAnnotator
from methods.method_b_hybrid import HybridAnnotator
from methods.method_c_llm import PureLLMAnnotator
from utils.evaluator import Evaluator


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/experiment.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def load_config():
    """加载配置"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_test_data():
    """加载测试数据"""
    data_file = Path(__file__).parent / "data" / "test_corpus.txt"
    with open(data_file, encoding="utf-8") as f:
        return f.read().strip()


def save_result(result, output_file):
    """保存标注结果"""
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True)

    # 保存标注文本
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.tagged_text)

    # 保存元数据
    metadata_file = output_file.with_suffix(".json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(result.metadata, f, ensure_ascii=False, indent=2)


def run_method_a(config, text):
    """运行方案A"""
    print("\n" + "=" * 80)
    print("方案A: 本地模型 (LTP依存文法)")
    print("=" * 80)

    annotator = LTPAnnotator(config["local_model"])
    result = annotator.annotate(text)

    output_file = Path(__file__).parent / "results" / "method_a_ltp_result.tagged.md"
    save_result(result, output_file)

    print(f"\n✓ 方案A完成")
    print(f"  - 实体数: {result.metadata['entity_count']}")
    print(f"  - 耗时: {result.metadata['time_seconds']:.2f}秒")
    print(f"  - Token: {result.metadata['token_count']}")

    return result


def run_method_b(config, text):
    """运行方案B"""
    print("\n" + "=" * 80)
    print("方案B: 混合方案 (本地+LLM)")
    print("=" * 80)

    annotator = HybridAnnotator(config)
    result = annotator.annotate(text)

    output_file = Path(__file__).parent / "results" / "method_b_hybrid_result.tagged.md"
    save_result(result, output_file)

    print(f"\n✓ 方案B完成")
    print(f"  - 总实体数: {result.metadata['entity_count']}")
    print(f"  - 本地实体: {result.metadata['local_entity_count']}")
    print(f"  - LLM实体: {result.metadata['llm_entity_count']}")
    print(f"  - 耗时: {result.metadata['time_seconds']:.2f}秒")
    print(f"  - Token: {result.metadata['token_count']}")

    return result


def run_method_c(config, text):
    """运行方案C"""
    print("\n" + "=" * 80)
    print("方案C: 纯LLM")
    print("=" * 80)

    annotator = PureLLMAnnotator(config)
    result = annotator.annotate(text)

    output_file = Path(__file__).parent / "results" / "method_c_llm_result.tagged.md"
    save_result(result, output_file)

    print(f"\n✓ 方案C完成")
    print(f"  - 实体数: {result.metadata['entity_count']}")
    print(f"  - 耗时: {result.metadata['time_seconds']:.2f}秒")
    print(f"  - Token: {result.metadata['token_count']}")

    return result


def evaluate_results(config):
    """评估结果"""
    print("\n" + "=" * 80)
    print("评估对比")
    print("=" * 80)

    ground_truth_file = Path(__file__).parent / config["evaluation"]["ground_truth"]

    if not ground_truth_file.exists():
        print(f"警告: 标准答案不存在: {ground_truth_file}")
        print("跳过评估步骤")
        return

    evaluator = Evaluator(str(ground_truth_file))

    # 评估各方法
    results_dir = Path(__file__).parent / "results"

    methods = [
        ("method_a_ltp", "method_a_ltp_result.tagged.md"),
        ("method_b_hybrid", "method_b_hybrid_result.tagged.md"),
        ("method_c_llm", "method_c_llm_result.tagged.md"),
    ]

    evaluation_results = []
    metadata_list = []

    for method_name, filename in methods:
        result_file = results_dir / filename
        metadata_file = result_file.with_suffix(".json")

        # 评估
        eval_result = evaluator.evaluate_file(result_file, method_name)
        if eval_result:
            evaluation_results.append(eval_result)

            # 加载元数据
            if metadata_file.exists():
                with open(metadata_file, encoding="utf-8") as f:
                    metadata = json.load(f)
                    metadata_list.append(metadata)

    # 对比
    if evaluation_results:
        comparison = evaluator.compare_methods(evaluation_results)

        # 生成报告
        output_file = results_dir / "comparison.json"
        evaluator.generate_report(comparison, metadata_list, str(output_file))


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="运行A/B测试实验")
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=["a", "b", "c", "all"],
        default=["all"],
        help="要运行的方案 (a/b/c/all)"
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="跳过评估步骤"
    )

    args = parser.parse_args()

    # 设置日志
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logging()

    # 加载配置
    config = load_config()

    # 加载测试数据
    text = load_test_data()
    print(f"测试数据: {len(text)} 字符")

    # 运行实验
    methods_to_run = args.methods
    if "all" in methods_to_run:
        methods_to_run = ["a", "b", "c"]

    results = {}

    if "a" in methods_to_run:
        try:
            results["a"] = run_method_a(config, text)
        except Exception as e:
            logging.error(f"方案A执行失败: {e}", exc_info=True)

    if "b" in methods_to_run:
        try:
            results["b"] = run_method_b(config, text)
        except Exception as e:
            logging.error(f"方案B执行失败: {e}", exc_info=True)

    if "c" in methods_to_run:
        try:
            results["c"] = run_method_c(config, text)
        except Exception as e:
            logging.error(f"方案C执行失败: {e}", exc_info=True)

    # 评估
    if not args.skip_eval and results:
        try:
            evaluate_results(config)
        except Exception as e:
            logging.error(f"评估失败: {e}", exc_info=True)

    print("\n" + "=" * 80)
    print("实验完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
