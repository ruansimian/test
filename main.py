#!/usr/bin/env python3
"""
成绩分析系统 — 命令行入口

用法：
  python main.py demo                        # 使用内置示例数据演示
  python main.py summary  <csv_file>         # 班级汇总报告
  python main.py rank     <csv_file> [科目]  # 排名榜（可选指定科目）
  python main.py subject  <csv_file> <科目>  # 单科详情
  python main.py student  <csv_file> <学号>  # 学生个人报告
  python main.py export   <csv_file> <out>   # 导出完整文本报告
  python main.py init     <csv_file>         # 生成示例 CSV 文件
"""
import sys
import os

from data_manager import (
    load_from_csv, save_to_csv, write_sample_csv, generate_sample_data,
)
from analyzer import GradeAnalyzer
from reporter import Reporter


def _load(csv_path: str) -> Reporter:
    if not os.path.exists(csv_path):
        print(f"错误：文件不存在 — {csv_path}")
        sys.exit(1)
    students = load_from_csv(csv_path)
    if not students:
        print("错误：未能从文件中读取到学生数据")
        sys.exit(1)
    return Reporter(GradeAnalyzer(students))


def cmd_demo():
    students = generate_sample_data()
    analyzer = GradeAnalyzer(students)
    reporter = Reporter(analyzer)
    print(reporter.summary())
    print()
    print(reporter.rank_table())
    print()
    # 第一个科目详情
    subjects = analyzer.all_subjects()
    if subjects:
        print(reporter.subject_detail(subjects[0]))
    print()
    # 第一个学生报告
    if students:
        print(reporter.student_report(students[0].student_id))


def cmd_summary(csv_path: str):
    reporter = _load(csv_path)
    print(reporter.summary())


def cmd_rank(csv_path: str, subject: str = None):
    reporter = _load(csv_path)
    print(reporter.rank_table(subject))


def cmd_subject(csv_path: str, subject: str):
    reporter = _load(csv_path)
    print(reporter.subject_detail(subject))


def cmd_student(csv_path: str, student_id: str):
    reporter = _load(csv_path)
    print(reporter.student_report(student_id))


def cmd_export(csv_path: str, out_path: str):
    reporter = _load(csv_path)
    reporter.export_full_report(out_path)


def cmd_init(csv_path: str):
    write_sample_csv(csv_path)


HELP = __doc__


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(HELP)
        return

    cmd = args[0]

    if cmd == "demo":
        cmd_demo()
    elif cmd == "summary" and len(args) >= 2:
        cmd_summary(args[1])
    elif cmd == "rank" and len(args) >= 2:
        cmd_rank(args[1], args[2] if len(args) >= 3 else None)
    elif cmd == "subject" and len(args) >= 3:
        cmd_subject(args[1], args[2])
    elif cmd == "student" and len(args) >= 3:
        cmd_student(args[1], args[2])
    elif cmd == "export" and len(args) >= 3:
        cmd_export(args[1], args[2])
    elif cmd == "init" and len(args) >= 2:
        cmd_init(args[1])
    else:
        print("参数错误，请查看帮助：")
        print(HELP)
        sys.exit(1)


if __name__ == "__main__":
    main()
