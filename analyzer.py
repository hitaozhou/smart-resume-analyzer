"""
智能简历分析引擎
功能：文本解析、技能提取、多维评分、岗位匹配、改进建议
"""

import re
from collections import Counter
from typing import Optional


# ==================== 技能词库 ====================

SKILL_DATABASE = {
    "编程语言": ["Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#", "PHP", "Ruby",
                "Swift", "Kotlin", "Scala", "Shell", "SQL", "R", "MATLAB"],
    "前端技术": ["React", "Vue", "Angular", "Next.js", "Nuxt", "HTML5", "CSS3", "Sass", "Webpack",
                "Vite", "Tailwind", "Bootstrap", "jQuery", "Redux", "Pinia"],
    "后端技术": ["FastAPI", "Django", "Flask", "Spring Boot", "Express", "NestJS", "Gin", "Rails",
                "Laravel", "ASP.NET", "Node.js", "GraphQL", "REST API", "WebSocket"],
    "数据库": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "Oracle",
              "ClickHouse", "Cassandra", "Neo4j", "DynamoDB"],
    "云与运维": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "GitHub Actions",
                "Terraform", "Ansible", "Nginx", "Linux", "Prometheus", "Grafana"],
    "AI与数据": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "TensorFlow",
                "Scikit-learn", "Pandas", "NumPy", "LLM", "Transformer", "数据挖掘", "数据分析"],
    "通用技能": ["Git", "Agile", "Scrum", "项目管理", "技术文档", "团队协作", "跨部门沟通",
                "需求分析", "系统设计", "性能优化", "Code Review", "单元测试", "UI设计"],
}

JOB_TEMPLATES = {
    "前端开发工程师": {
        "keywords": ["React", "Vue", "JavaScript", "TypeScript", "HTML5", "CSS3", "前端", "Web",
                     "响应式", "组件化", "性能优化", "跨浏览器", "小程序"],
        "must_have": ["JavaScript", "HTML5", "CSS3", "React/Vue"],
        "nice_to_have": ["TypeScript", "Node.js", "Webpack", "Next.js", "Tailwind"],
        "salary_range": "15K-35K",
        "demand": "高需求"
    },
    "后端开发工程师": {
        "keywords": ["Python", "Java", "Go", "API", "数据库", "微服务", "后端", "服务端",
                     "并发", "分布式", "缓存", "消息队列", "系统架构"],
        "must_have": ["Python/Java/Go(任一)", "数据库", "REST API", "Linux"],
        "nice_to_have": ["Docker", "Kubernetes", "微服务", "Redis", "消息队列"],
        "salary_range": "18K-40K",
        "demand": "高需求"
    },
    "数据分析师": {
        "keywords": ["数据分析", "SQL", "Python", "Excel", "可视化", "统计", "报表",
                     "数据挖掘", "BI", "Tableau", "Power BI", "业务分析"],
        "must_have": ["SQL", "Excel", "Python/R", "数据可视化"],
        "nice_to_have": ["Tableau", "Power BI", "统计学", "机器学习"],
        "salary_range": "12K-28K",
        "demand": "中等需求"
    },
    "AI/算法工程师": {
        "keywords": ["机器学习", "深度学习", "算法", "Python", "PyTorch", "TensorFlow",
                     "NLP", "CV", "模型", "训练", "推理", "特征工程"],
        "must_have": ["Python", "机器学习", "PyTorch/TensorFlow", "算法基础"],
        "nice_to_have": ["深度学习", "NLP", "CV", "模型部署", "论文"],
        "salary_range": "25K-60K",
        "demand": "高需求"
    },
    "全栈开发工程师": {
        "keywords": ["全栈", "前后端", "React", "Vue", "Node.js", "Python", "数据库",
                     "DevOps", "API", "TypeScript", "全流程"],
        "must_have": ["JavaScript", "至少一种后端语言", "数据库", "前后端经验"],
        "nice_to_have": ["TypeScript", "Docker", "AWS/云服务", "CI/CD"],
        "salary_range": "18K-40K",
        "demand": "高需求"
    },
}

IMPROVEMENT_TIPS = {
    "缺少联系方式": "简历必须包含电话和邮箱，这是HR联系你的唯一途径。建议放在简历顶部显眼位置。",
    "缺少技能列表": "技能列表是ATS筛选的关键。建议独立一个「专业技能」模块，按熟练程度分类列出。",
    "缺少项目经验": "项目经验是技术简历的核心。每个项目应包括：项目背景 → 你的职责 → 技术栈 → 量化成果。",
    "描述太笼统": "避免使用「负责开发工作」等模糊表述。改用STAR法则：情境→任务→行动→结果，用数据说话。",
    "没有量化成果": "用数字展示影响力：性能提升了X%、用户增长了Y%、处理了Z万条数据。数字比形容词更有说服力。",
    "格式问题": "建议使用清晰的层级结构，统一字体和间距。技术术语保持大小写一致（如React而非react）。",
    "技能过时": "关注当前行业热门技术栈。建议补充云计算、AI工具链等2024年热门技能。",
    "缺少教育背景": "教育背景是基础信息，尤其是应届生。包括学校、专业、毕业时间、GPA（如果优秀）。",
    "自我评价空泛": "自我评价应突出核心竞争力，3-5句为宜。避免套话，用具体成就支撑观点。",
    "排版密集": "适当使用项目符号和留白，确保10秒内可快速扫描关键信息。HR平均看一份简历仅6-10秒。",
}


class ResumeAnalyzer:
    """简历分析引擎"""

    def __init__(self):
        self.raw_text = ""
        self.parsed = {}

    def parse_text(self, text: str) -> dict:
        """解析简历文本，提取结构化信息"""
        self.raw_text = text
        lines = text.split('\n')

        parsed = {
            "name": self._extract_name(text, lines),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "education": self._extract_education(text),
            "skills": self._extract_skills(text),
            "experience_years": self._estimate_experience(text),
            "projects": self._extract_projects(text),
            "word_count": len(text),
        }
        self.parsed = parsed
        return parsed

    def score_resume(self, parsed: dict) -> dict:
        """多维度评分"""
        scores = {}

        # 1. 完整度评分 (30分)
        completeness = 30
        if not parsed.get("name"): completeness -= 8
        if not parsed.get("email"): completeness -= 6
        if not parsed.get("phone"): completeness -= 6
        if not parsed.get("education"): completeness -= 5
        if len(parsed.get("skills", [])) < 3: completeness -= 5
        scores["completeness"] = max(0, completeness)

        # 2. 技能丰富度评分 (25分)
        skill_count = len(parsed.get("skills", []))
        if skill_count >= 12: scores["skills"] = 25
        elif skill_count >= 8: scores["skills"] = 20
        elif skill_count >= 5: scores["skills"] = 15
        elif skill_count >= 3: scores["skills"] = 10
        else: scores["skills"] = 5

        # 3. 经验质量评分 (25分)
        years = parsed.get("experience_years", 0)
        project_count = len(parsed.get("projects", []))
        if years >= 3 and project_count >= 3: scores["experience"] = 25
        elif years >= 2 and project_count >= 2: scores["experience"] = 20
        elif years >= 1 and project_count >= 1: scores["experience"] = 15
        elif project_count >= 1: scores["experience"] = 10
        else: scores["experience"] = 5

        # 4. 表达与格式评分 (20分)
        format_score = 20
        if parsed.get("word_count", 0) < 200: format_score -= 8  # 太短
        if not self._has_quantified_achievements(self.raw_text): format_score -= 6
        if not self._has_clear_structure(self.raw_text): format_score -= 6
        scores["format"] = max(0, format_score)

        # 总分
        total = sum(scores.values())
        scores["total"] = total

        # 等级
        if total >= 85: scores["grade"] = "A"
        elif total >= 70: scores["grade"] = "B"
        elif total >= 55: scores["grade"] = "C"
        elif total >= 40: scores["grade"] = "D"
        else: scores["grade"] = "F"

        scores["grade_desc"] = {
            "A": "🏆 优秀 — 简历质量很高，可以放心投递！",
            "B": "👍 良好 — 整体不错，仍有优化空间。",
            "C": "📝 一般 — 建议针对性改进后再投递。",
            "D": "⚠️ 较差 — 需要大幅优化，参考下方建议。",
            "F": "🚨 需重写 — 简历存在严重问题，建议重新梳理。",
        }.get(scores["grade"], "")

        return scores

    def generate_suggestions(self, parsed: dict) -> list:
        """生成改进建议"""
        suggestions = []

        if not parsed.get("email") or not parsed.get("phone"):
            suggestions.append({
                "priority": "high",
                "category": "基本信息",
                "tip": IMPROVEMENT_TIPS["缺少联系方式"]
            })

        if len(parsed.get("skills", [])) < 5:
            suggestions.append({
                "priority": "high",
                "category": "技能展示",
                "tip": IMPROVEMENT_TIPS["缺少技能列表"]
            })

        if len(parsed.get("projects", [])) < 2:
            suggestions.append({
                "priority": "high",
                "category": "项目经验",
                "tip": IMPROVEMENT_TIPS["缺少项目经验"]
            })

        if not self._has_quantified_achievements(self.raw_text):
            suggestions.append({
                "priority": "medium",
                "category": "成果量化",
                "tip": IMPROVEMENT_TIPS["没有量化成果"]
            })

        if parsed.get("word_count", 0) < 200:
            suggestions.append({
                "priority": "medium",
                "category": "内容完整度",
                "tip": IMPROVEMENT_TIPS["描述太笼统"]
            })

        if not parsed.get("education"):
            suggestions.append({
                "priority": "medium",
                "category": "教育背景",
                "tip": IMPROVEMENT_TIPS["缺少教育背景"]
            })

        if not self._has_clear_structure(self.raw_text):
            suggestions.append({
                "priority": "low",
                "category": "排版格式",
                "tip": IMPROVEMENT_TIPS["排版密集"]
            })

        # 检查自我评价
        if "自我评价" not in self.raw_text and "个人总结" not in self.raw_text:
            suggestions.append({
                "priority": "low",
                "category": "个人总结",
                "tip": IMPROVEMENT_TIPS["自我评价空泛"]
            })

        # 至少返回3条建议
        if len(suggestions) < 3:
            extra_tips = [
                {"priority": "medium", "category": "持续优化", "tip": IMPROVEMENT_TIPS["技能过时"]},
                {"priority": "low", "category": "排版格式", "tip": IMPROVEMENT_TIPS["格式问题"]},
            ]
            for t in extra_tips:
                if len(suggestions) < 3:
                    suggestions.append(t)

        return suggestions

    def match_job(self, parsed: dict, job_title: str) -> dict:
        """匹配岗位，返回匹配度和差距分析"""
        template = JOB_TEMPLATES.get(job_title)
        if not template:
            # 尝试模糊匹配
            for key in JOB_TEMPLATES:
                if job_title in key or key in job_title:
                    template = JOB_TEMPLATES[key]
                    job_title = key
                    break

        if not template:
            return {"error": f"暂无「{job_title}」的岗位模板，请尝试其他岗位"}

        skills_text = " ".join(parsed.get("skills", []))

        # 关键词匹配
        matched = []
        for kw in template["keywords"]:
            if kw.lower() in skills_text.lower() or kw.lower() in self.raw_text.lower():
                matched.append(kw)

        match_rate = min(95, int(len(matched) / max(len(template["keywords"]), 1) * 100))

        # 必备技能检查
        missing_must = []
        for skill in template["must_have"]:
            found = False
            for sub_skill in skill.split('/'):
                if sub_skill.lower() in skills_text.lower():
                    found = True
                    break
            if not found:
                missing_must.append(skill)

        # 加分技能
        missing_nice = [s for s in template["nice_to_have"]
                        if not any(part.lower() in skills_text.lower() for part in s.split('/'))]

        return {
            "job_title": job_title,
            "match_rate": match_rate,
            "matched_keywords": matched[:15],
            "missing_must": missing_must,
            "missing_nice": missing_nice,
            "salary_range": template["salary_range"],
            "demand": template["demand"],
            "verdict": self._match_verdict(match_rate, len(missing_must)),
        }

    def get_skill_radar(self, parsed: dict) -> dict:
        """技能雷达图数据"""
        skills = parsed.get("skills", [])

        categories = {
            "编程语言": 0, "前端技术": 0, "后端技术": 0,
            "数据库": 0, "云与运维": 0, "AI与数据": 0
        }

        for skill in skills:
            for cat, skill_list in SKILL_DATABASE.items():
                if cat in categories and skill in skill_list:
                    categories[cat] += 1

        # 归一化到 0-100
        max_per_cat = 5
        return {
            "labels": list(categories.keys()),
            "values": [min(100, v * 20) for v in categories.values()],
            "legend": [f"{k} ({v}项)" for k, v in categories.items()]
        }

    def get_skill_breakdown(self, parsed: dict) -> list:
        """技能分类明细"""
        skills = parsed.get("skills", [])
        breakdown = []

        for cat, skill_list in SKILL_DATABASE.items():
            matched = [s for s in skills if s in skill_list]
            if matched:
                breakdown.append({
                    "category": cat,
                    "skills": matched,
                    "count": len(matched),
                    "percentage": min(100, int(len(matched) / max(len(skill_list), 1) * 100))
                })

        breakdown.sort(key=lambda x: x["count"], reverse=True)
        return breakdown

    # ==================== 内部方法 ====================

    def _extract_name(self, text: str, lines: list) -> Optional[str]:
        """提取姓名"""
        # 通常在第一行
        for line in lines[:5]:
            line = line.strip()
            # 中文姓名：2-4个汉字
            match = re.match(r'^([一-龥]{2,4})$', line)
            if match:
                return match.group(1)
            # 英文姓名
            match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)$', line)
            if match:
                return match.group(1)
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """提取邮箱"""
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """提取手机号"""
        match = re.search(r'1[3-9]\d{9}', text)
        return match.group(0) if match else None

    def _extract_education(self, text: str) -> Optional[str]:
        """提取教育背景"""
        patterns = [
            r'(大学|学院|University|College)',
            r'(本科|硕士|博士|大专|Bachelor|Master|PhD)',
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                # 返回匹配行
                for line in text.split('\n'):
                    if match.group(0) in line:
                        return line.strip()[:60]
        return None

    def _extract_skills(self, text: str) -> list:
        """提取技能列表"""
        found = []
        for cat, skill_list in SKILL_DATABASE.items():
            for skill in skill_list:
                if skill.lower() in text.lower():
                    found.append(skill)
        return list(dict.fromkeys(found))  # 去重保序

    def _estimate_experience(self, text: str) -> float:
        """估算工作年限"""
        # 匹配年份范围
        matches = re.findall(r'(20\d{2})[.\-/~—至到]+(20\d{2}|至今|现在|present)', text, re.IGNORECASE)
        if matches:
            total_years = 0
            for start, end in matches:
                start_y = int(start)
                end_y = 2026 if end in ('至今', '现在', 'present') else int(end)
                total_years += max(0, end_y - start_y)
            return min(total_years, 20)  # 上限20年
        return 0.5  # 默认应届

    def _extract_projects(self, text: str) -> list:
        """提取项目经验"""
        projects = []
        # 匹配项目描述模式
        project_indicators = ['项目名称', '项目描述', '项目经验', 'PROJECT', '项目：',
                              '负责项目', '参与项目', '主导']

        lines = text.split('\n')
        in_project_section = False
        current_project = ""

        for line in lines:
            if any(ind in line for ind in project_indicators):
                in_project_section = True
                if current_project:
                    projects.append(current_project.strip()[:100])
                current_project = line.strip()
            elif in_project_section:
                if line.strip() and not line.startswith(('教育', '技能', '工作', '联系')):
                    current_project += " " + line.strip()
                else:
                    if len(current_project) > 10:
                        projects.append(current_project.strip()[:100])
                    current_project = ""
                    in_project_section = False

        if len(current_project) > 10:
            projects.append(current_project.strip()[:100])

        return projects[:10]

    def _has_quantified_achievements(self, text: str) -> bool:
        """检查是否有量化成果"""
        patterns = [
            r'\d+%', r'\d+万', r'\d+人', r'\d+倍',
            r'提升.*\d+', r'增长.*\d+', r'降低.*\d+',
            r'处理.*\d+', r'负责.*\d+人', r'管理.*\d+'
        ]
        return any(re.search(p, text) for p in patterns)

    def _has_clear_structure(self, text: str) -> bool:
        """检查结构是否清晰"""
        structure_keywords = ['教育背景', '工作经历', '项目经验', '技能', '自我评价',
                             '联系方式', 'Education', 'Experience', 'Skills']
        found = sum(1 for kw in structure_keywords if kw.lower() in text.lower())
        return found >= 3

    def _match_verdict(self, rate: int, missing_count: int) -> str:
        """匹配结论"""
        if rate >= 75 and missing_count == 0:
            return "🎯 高度匹配！您的技能与岗位要求非常契合，建议立即投递。"
        elif rate >= 60:
            return "👍 较为匹配。补充缺失的必备技能后可大幅提升竞争力。"
        elif rate >= 40:
            return "📝 部分匹配。建议针对该岗位定向优化简历，重点补充技能短板。"
        else:
            return "🔄 匹配度较低。建议先学习核心技能，或尝试其他方向的岗位。"


# 全局单例
resume_analyzer = ResumeAnalyzer()
