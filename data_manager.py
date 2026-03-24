"""
数据管理：CSV 导入/导出、示例数据生成
"""
import csv
import json
import os
from typing import List, Dict
from models import Student


# ── CSV ──────────────────────────────────────────────────────────────────────

def load_from_csv(filepath: str) -> List[Student]:
    """
    从 CSV 文件加载学生成绩。
    格式：学号,姓名,班级,科目1,科目2,...
    第一行为表头，科目列名即为科目名称。
    """
    students: Dict[str, Student] = {}
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        subject_cols = [c for c in fields if c not in ("学号", "姓名", "班级", "平均分", "总分")]

        for row in reader:
            sid = row.get("学号", "").strip()
            name = row.get("姓名", "").strip()
            cls = row.get("班级", "").strip()
            if not sid or not name:
                continue
            if sid not in students:
                students[sid] = Student(sid, name, cls)
            stu = students[sid]
            for subj in subject_cols:
                val = row.get(subj, "").strip()
                if val:
                    try:
                        stu.add_grade(subj, float(val))
                    except ValueError:
                        pass
    return list(students.values())


def save_to_csv(students: List[Student], filepath: str):
    """将学生成绩导出为 CSV 文件"""
    all_subjects = sorted({g.subject for s in students for g in s.grades})
    fieldnames = ["学号", "姓名", "班级"] + all_subjects + ["平均分", "总分"]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for stu in students:
            row: Dict = {
                "学号": stu.student_id,
                "姓名": stu.name,
                "班级": stu.class_name,
                "平均分": f"{stu.average_score:.2f}",
                "总分": f"{stu.total_score:.2f}",
            }
            for subj in all_subjects:
                g = stu.get_grade(subj)
                row[subj] = f"{g.score:.1f}" if g else ""
            writer.writerow(row)


# ── JSON ─────────────────────────────────────────────────────────────────────

def save_to_json(students: List[Student], filepath: str):
    data = []
    for stu in students:
        data.append({
            "student_id": stu.student_id,
            "name": stu.name,
            "class_name": stu.class_name,
            "grades": [
                {"subject": g.subject, "score": g.score, "full_score": g.full_score}
                for g in stu.grades
            ],
        })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_from_json(filepath: str) -> List[Student]:
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    students = []
    for item in data:
        stu = Student(item["student_id"], item["name"], item.get("class_name", ""))
        for g in item.get("grades", []):
            stu.add_grade(g["subject"], g["score"], g.get("full_score", 100.0))
        students.append(stu)
    return students


# ── 示例数据 ──────────────────────────────────────────────────────────────────

def generate_sample_data() -> List[Student]:
    """生成用于演示的示例学生数据"""
    import random
    random.seed(42)

    names = [
        "张伟", "王芳", "李娜", "刘洋", "陈静",
        "杨帆", "赵磊", "周婷", "吴昊", "徐晨",
        "孙悦", "马超", "胡敏", "郑浩", "林小红",
        "高明", "何丽", "罗勇", "宋涛", "谢雨",
    ]
    subjects = ["语文", "数学", "英语", "物理", "化学"]

    students = []
    for i, name in enumerate(names):
        sid = f"2024{i+1:03d}"
        cls = "高一(1)班" if i < 10 else "高一(2)班"
        stu = Student(sid, name, cls)
        for subj in subjects:
            # 模拟正态分布的成绩
            mean = random.uniform(65, 88)
            score = max(0, min(100, random.gauss(mean, 10)))
            stu.add_grade(subj, round(score, 1))
        students.append(stu)
    return students


def write_sample_csv(filepath: str):
    """将示例数据写入 CSV 文件"""
    students = generate_sample_data()
    save_to_csv(students, filepath)
    print(f"示例数据已写入：{filepath}")
