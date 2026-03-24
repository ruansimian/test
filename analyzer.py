"""
成绩分析引擎：统计分析、排名、分布
"""
import math
from typing import List, Dict, Optional
from models import Student, Grade, score_to_grade, GRADE_LEVELS


class SubjectStats:
    """单科统计结果"""
    def __init__(self, subject: str, scores: List[float]):
        self.subject = subject
        self.scores = sorted(scores)
        self.count = len(scores)

    @property
    def mean(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores) / self.count

    @property
    def median(self) -> float:
        if not self.scores:
            return 0.0
        n = self.count
        mid = n // 2
        return self.scores[mid] if n % 2 else (self.scores[mid - 1] + self.scores[mid]) / 2

    @property
    def std_dev(self) -> float:
        if self.count < 2:
            return 0.0
        m = self.mean
        variance = sum((x - m) ** 2 for x in self.scores) / self.count
        return math.sqrt(variance)

    @property
    def max_score(self) -> float:
        return max(self.scores) if self.scores else 0.0

    @property
    def min_score(self) -> float:
        return min(self.scores) if self.scores else 0.0

    @property
    def pass_rate(self) -> float:
        if not self.scores:
            return 0.0
        passed = sum(1 for s in self.scores if s >= 60)
        return passed / self.count * 100

    @property
    def excellent_rate(self) -> float:
        if not self.scores:
            return 0.0
        excellent = sum(1 for s in self.scores if s >= 90)
        return excellent / self.count * 100

    def grade_distribution(self) -> Dict[str, int]:
        """各等级人数分布"""
        dist = {letter: 0 for _, _, letter, _ in GRADE_LEVELS}
        for s in self.scores:
            letter, _ = score_to_grade(s)
            dist[letter] += 1
        return dist

    def percentile(self, score: float) -> float:
        """计算某分数的百分位排名"""
        if not self.scores:
            return 0.0
        below = sum(1 for s in self.scores if s < score)
        return below / self.count * 100


class GradeAnalyzer:
    def __init__(self, students: List[Student]):
        self.students = students

    # ── 学生排名 ─────────────────────────────────────────────────────────────

    def rank_students(self, subject: Optional[str] = None) -> List[Dict]:
        """
        按总分或指定科目排名。
        返回列表：[{rank, student, score, ...}, ...]
        """
        results = []
        for stu in self.students:
            if subject:
                grade = stu.get_grade(subject)
                if grade is None:
                    continue
                score = grade.score
                percentage = grade.percentage
            else:
                score = stu.average_score
                percentage = stu.average_percentage

            results.append({
                "student": stu,
                "score": score,
                "percentage": percentage,
                "letter": score_to_grade(percentage)[0],
                "level": score_to_grade(percentage)[1],
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        for i, r in enumerate(results, 1):
            r["rank"] = i

        return results

    # ── 科目统计 ─────────────────────────────────────────────────────────────

    def subject_stats(self, subject: str) -> Optional[SubjectStats]:
        scores = []
        for stu in self.students:
            g = stu.get_grade(subject)
            if g is not None:
                scores.append(g.score)
        if not scores:
            return None
        return SubjectStats(subject, scores)

    def all_subjects(self) -> List[str]:
        subjects = set()
        for stu in self.students:
            for g in stu.grades:
                subjects.add(g.subject)
        return sorted(subjects)

    def all_subject_stats(self) -> Dict[str, SubjectStats]:
        return {s: self.subject_stats(s) for s in self.all_subjects()}

    # ── 班级整体统计 ───────────────────────────────────────────────────────

    def class_average(self) -> float:
        if not self.students:
            return 0.0
        return sum(s.average_score for s in self.students) / len(self.students)

    def class_pass_rate(self) -> float:
        """所有科目均及格的学生比例"""
        if not self.students:
            return 0.0
        all_pass = sum(
            1 for s in self.students
            if s.grades and all(g.score >= 60 for g in s.grades)
        )
        return all_pass / len(self.students) * 100

    def score_segments(self, subject: Optional[str] = None) -> Dict[str, int]:
        """分数段人数统计（每10分一段）"""
        segments = {f"{i}-{i+9}": 0 for i in range(0, 100, 10)}
        segments["100"] = 0
        for stu in self.students:
            if subject:
                g = stu.get_grade(subject)
                scores = [g.score] if g else []
            else:
                scores = [stu.average_score] if stu.grades else []
            for score in scores:
                if score == 100:
                    segments["100"] += 1
                else:
                    key = f"{int(score // 10) * 10}-{int(score // 10) * 10 + 9}"
                    if key in segments:
                        segments[key] += 1
        return segments

    # ── 对比分析 ──────────────────────────────────────────────────────────

    def compare_subjects(self) -> List[Dict]:
        """各科目横向对比"""
        result = []
        for subject, stats in self.all_subject_stats().items():
            if stats:
                result.append({
                    "subject": subject,
                    "mean": stats.mean,
                    "median": stats.median,
                    "std_dev": stats.std_dev,
                    "max": stats.max_score,
                    "min": stats.min_score,
                    "pass_rate": stats.pass_rate,
                    "excellent_rate": stats.excellent_rate,
                })
        result.sort(key=lambda x: x["mean"], reverse=True)
        return result
