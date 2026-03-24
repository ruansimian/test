"""
数据模型：学生、成绩、科目
"""
from dataclasses import dataclass, field
from typing import List, Optional


GRADE_LEVELS = [
    (90, 100, "A", "优秀"),
    (80, 90,  "B", "良好"),
    (70, 80,  "C", "中等"),
    (60, 70,  "D", "及格"),
    (0,  60,  "F", "不及格"),
]


def score_to_grade(score: float) -> tuple[str, str]:
    """将分数转换为等级和描述"""
    for low, high, letter, desc in GRADE_LEVELS:
        if low <= score <= high:
            return letter, desc
    return "F", "不及格"


@dataclass
class Grade:
    subject: str
    score: float
    full_score: float = 100.0

    @property
    def percentage(self) -> float:
        return self.score / self.full_score * 100

    @property
    def letter(self) -> str:
        return score_to_grade(self.percentage)[0]

    @property
    def level(self) -> str:
        return score_to_grade(self.percentage)[1]

    def __repr__(self):
        return f"{self.subject}: {self.score}/{self.full_score} ({self.letter})"


@dataclass
class Student:
    student_id: str
    name: str
    class_name: str = ""
    grades: List[Grade] = field(default_factory=list)

    def add_grade(self, subject: str, score: float, full_score: float = 100.0):
        # 已存在则更新
        for g in self.grades:
            if g.subject == subject:
                g.score = score
                g.full_score = full_score
                return
        self.grades.append(Grade(subject, score, full_score))

    def get_grade(self, subject: str) -> Optional[Grade]:
        for g in self.grades:
            if g.subject == subject:
                return g
        return None

    @property
    def total_score(self) -> float:
        return sum(g.score for g in self.grades)

    @property
    def average_score(self) -> float:
        if not self.grades:
            return 0.0
        return self.total_score / len(self.grades)

    @property
    def average_percentage(self) -> float:
        if not self.grades:
            return 0.0
        return sum(g.percentage for g in self.grades) / len(self.grades)

    def __repr__(self):
        return f"Student({self.student_id}, {self.name}, avg={self.average_score:.1f})"
