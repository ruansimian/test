"""
报告生成器：控制台格式化输出 + 文本报告导出
"""
from typing import List, Optional
from analyzer import GradeAnalyzer, SubjectStats
from models import Student

# 终端宽度
W = 72
SEP = "=" * W
SEP2 = "-" * W


def _bar(value: float, max_val: float, width: int = 20) -> str:
    filled = int(value / max_val * width) if max_val else 0
    return "█" * filled + "░" * (width - filled)


def _pct(v: float) -> str:
    return f"{v:.1f}%"


class Reporter:
    def __init__(self, analyzer: GradeAnalyzer):
        self.analyzer = analyzer

    # ── 汇总报告 ───────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [SEP, "  成绩分析系统 — 班级汇总报告", SEP]
        students = self.analyzer.students
        lines.append(f"  学生总人数：{len(students)}")
        lines.append(f"  班级平均分：{self.analyzer.class_average():.2f}")
        lines.append(f"  全科及格率：{_pct(self.analyzer.class_pass_rate())}")
        lines.append(SEP2)

        # 各科目统计
        lines.append("  各科目统计")
        lines.append(SEP2)
        fmt = "  {:<8} {:>7} {:>7} {:>7} {:>7} {:>7}  {:>8}  {:>8}"
        lines.append(fmt.format("科目", "平均分", "中位数", "最高", "最低", "标准差", "及格率", "优秀率"))
        lines.append(SEP2)
        for item in self.analyzer.compare_subjects():
            lines.append(fmt.format(
                item["subject"],
                f"{item['mean']:.1f}",
                f"{item['median']:.1f}",
                f"{item['max']:.1f}",
                f"{item['min']:.1f}",
                f"{item['std_dev']:.1f}",
                _pct(item["pass_rate"]),
                _pct(item["excellent_rate"]),
            ))
        lines.append(SEP)
        return "\n".join(lines)

    # ── 排名榜 ─────────────────────────────────────────────────────────────

    def rank_table(self, subject: Optional[str] = None) -> str:
        title = f'按"{subject}"排名' if subject else "按平均分排名"
        lines = [SEP, f"  学生排名榜 — {title}", SEP2]
        fmt = "  {:<4} {:<10} {:<8} {:<8} {:>7} {:>7}  {}"
        lines.append(fmt.format("排名", "学号", "姓名", "班级", "分数", "等级", "成绩条"))
        lines.append(SEP2)
        for r in self.analyzer.rank_students(subject):
            stu: Student = r["student"]
            bar = _bar(r["score"], 100)
            lines.append(fmt.format(
                r["rank"],
                stu.student_id,
                stu.name,
                stu.class_name,
                f"{r['score']:.1f}",
                f"{r['letter']} {r['level']}",
                bar,
            ))
        lines.append(SEP)
        return "\n".join(lines)

    # ── 单科详情 ────────────────────────────────────────────────────────────

    def subject_detail(self, subject: str) -> str:
        stats: Optional[SubjectStats] = self.analyzer.subject_stats(subject)
        if stats is None:
            return f"未找到科目：{subject}"

        dist = stats.grade_distribution()
        lines = [SEP, f"  科目详情 — {subject}", SEP2]
        lines.append(f"  参与人数：{stats.count}")
        lines.append(f"  平均分：  {stats.mean:.2f}    中位数：{stats.median:.2f}")
        lines.append(f"  最高分：  {stats.max_score:.1f}    最低分：{stats.min_score:.1f}")
        lines.append(f"  标准差：  {stats.std_dev:.2f}")
        lines.append(f"  及格率：  {_pct(stats.pass_rate)}    优秀率：{_pct(stats.excellent_rate)}")
        lines.append(SEP2)
        lines.append("  等级分布")
        labels = {"A": "优秀(90-100)", "B": "良好(80-89)", "C": "中等(70-79)",
                  "D": "及格(60-69)", "F": "不及格(<60)"}
        for letter, count in dist.items():
            pct = count / stats.count * 100 if stats.count else 0
            bar = _bar(count, stats.count)
            lines.append(f"  {labels[letter]:<14}  {count:>3}人  {_pct(pct):>6}  {bar}")
        lines.append(SEP)
        return "\n".join(lines)

    # ── 学生个人报告 ─────────────────────────────────────────────────────

    def student_report(self, student_id: str) -> str:
        stu = next((s for s in self.analyzer.students if s.student_id == student_id), None)
        if stu is None:
            return f"未找到学号：{student_id}"

        lines = [SEP, f"  个人成绩报告 — {stu.name}（{stu.student_id}）", SEP2]
        lines.append(f"  班级：{stu.class_name}    平均分：{stu.average_score:.2f}    总分：{stu.total_score:.1f}")
        lines.append(SEP2)
        fmt = "  {:<8} {:>7} {:>6}  {:>7}  {}"
        lines.append(fmt.format("科目", "得分", "等级", "班级排名", "成绩条"))
        lines.append(SEP2)
        for g in stu.grades:
            ranking = self.analyzer.rank_students(g.subject)
            rank = next((r["rank"] for r in ranking if r["student"].student_id == student_id), "-")
            bar = _bar(g.score, g.full_score)
            lines.append(fmt.format(
                g.subject, f"{g.score:.1f}", f"{g.letter} {g.level}",
                f"第{rank}名", bar,
            ))
        lines.append(SEP)
        return "\n".join(lines)

    # ── 导出文本报告 ─────────────────────────────────────────────────────

    def export_full_report(self, filepath: str):
        subjects = self.analyzer.all_subjects()
        parts = [
            self.summary(),
            self.rank_table(),
        ]
        for subj in subjects:
            parts.append(self.subject_detail(subj))
        for stu in self.analyzer.students:
            parts.append(self.student_report(stu.student_id))

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n\n".join(parts))
        print(f"完整报告已导出：{filepath}")
