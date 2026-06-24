"""
智能简历分析系统 — FastAPI 后端
功能：简历上传解析、AI多维评分、岗位匹配、改进建议、可视化数据
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import io
import os

from analyzer import resume_analyzer, JOB_TEMPLATES

app = FastAPI(
    title="智能简历分析系统",
    description="AI驱动的简历分析、评分、岗位匹配工具",
    version="1.0.0"
)


# ==================== 文件解析 ====================

def extract_text_from_txt(content: bytes) -> str:
    """从TXT提取文本"""
    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode('utf-8', errors='ignore')


def extract_text_from_pdf(content: bytes) -> str:
    """从PDF提取文本"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF解析失败: {str(e)}")


def extract_text_from_docx(content: bytes) -> str:
    """从DOCX提取文本"""
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX解析失败: {str(e)}")


async def parse_resume_file(file: UploadFile) -> str:
    """根据文件类型解析简历"""
    content = await file.read()
    filename = file.filename.lower() if file.filename else ""

    if filename.endswith('.txt'):
        return extract_text_from_txt(content)
    elif filename.endswith('.pdf'):
        return extract_text_from_pdf(content)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(content)
    else:
        raise HTTPException(status_code=400, detail="仅支持 PDF / DOCX / TXT 格式")


# ==================== API 路由 ====================

@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(None), text: str = Form(None)):
    """
    上传并分析简历
    支持文件上传(PDF/DOCX/TXT)或直接粘贴文本
    """
    # 获取文本内容
    if file and file.filename:
        resume_text = await parse_resume_file(file)
    elif text and text.strip():
        resume_text = text.strip()
    else:
        raise HTTPException(status_code=400, detail="请上传简历文件或粘贴简历文本")

    if len(resume_text) < 50:
        raise HTTPException(status_code=400, detail="简历内容太少，至少需要50个字符")

    # 解析
    parsed = resume_analyzer.parse_text(resume_text)

    # 评分
    scores = resume_analyzer.score_resume(parsed)

    # 建议
    suggestions = resume_analyzer.generate_suggestions(parsed)

    # 雷达图数据
    radar = resume_analyzer.get_skill_radar(parsed)

    # 技能分类
    skill_breakdown = resume_analyzer.get_skill_breakdown(parsed)

    return {
        "code": 0,
        "data": {
            "parsed": parsed,
            "scores": scores,
            "suggestions": suggestions,
            "radar": radar,
            "skill_breakdown": skill_breakdown,
            "text_preview": resume_text[:500] + ("..." if len(resume_text) > 500 else ""),
        }
    }


@app.get("/api/jobs")
async def get_job_templates():
    """获取可匹配的岗位列表"""
    jobs = []
    for title, info in JOB_TEMPLATES.items():
        jobs.append({
            "title": title,
            "salary_range": info["salary_range"],
            "demand": info["demand"],
            "keywords_count": len(info["keywords"]),
        })
    return {"code": 0, "data": jobs}


@app.post("/api/match")
async def match_job(
    file: UploadFile = File(None),
    text: str = Form(None),
    job_title: str = Form(...)
):
    """
    简历与岗位匹配分析
    """
    # 获取简历文本
    if file and file.filename:
        resume_text = await parse_resume_file(file)
    elif text and text.strip():
        resume_text = text.strip()
    else:
        raise HTTPException(status_code=400, detail="请上传简历文件或粘贴简历文本")

    # 解析
    parsed = resume_analyzer.parse_text(resume_text)

    # 匹配
    match_result = resume_analyzer.match_job(parsed, job_title)

    if "error" in match_result:
        return {"code": 1, "message": match_result["error"]}

    return {
        "code": 0,
        "data": {
            "parsed": parsed,
            "match": match_result,
        }
    }


@app.get("/api/sample")
async def get_sample_resume():
    """获取示例简历文本（用于演示）"""
    sample = """张三

联系方式：13812345678 | zhangsan@email.com | 浙江省杭州市

教育背景
浙江开放大学 · 计算机科学与技术 · 本科 · 2025届
GPA: 3.6/4.0

专业技能
• 编程语言：Python, JavaScript, TypeScript, Java, SQL
• 前端技术：React, Vue.js, HTML5, CSS3, Tailwind, Next.js
• 后端技术：FastAPI, Django, Node.js, REST API, WebSocket
• 数据库：MySQL, MongoDB, Redis
• 云与运维：Docker, Git, Linux, CI/CD, Nginx
• AI/数据：PyTorch, Scikit-learn, Pandas, NumPy, LLM应用开发

项目经验

电商智能客服系统 | 全栈开发 | 2024.03 - 2024.06
• 基于FastAPI + WebSocket构建实时对话系统，响应延迟<200ms
• 实现意图识别引擎，准确率92%，支持8类业务场景
• 前端采用响应式三栏布局，兼容PC/平板/手机
• 上线后处理用户咨询1.2万+次，满意度提升35%

AI简历分析工具 | 独立开发 | 2024.01 - 2024.02
• 使用Python构建简历解析和多维评分系统
• 集成PDF/DOCX文件解析，支持6个维度的智能评分
• 实现岗位匹配算法，基于TF-IDF关键词提取
• 累计帮助200+求职者优化简历

校园二手交易平台 | 前端负责人 | 2023.09 - 2023.12
• 使用React + TypeScript开发，采用Zustand状态管理
• 实现即时通讯、商品搜索、在线支付等核心功能
• 项目获得校创新创业大赛二等奖

自我评价
热爱技术，具备良好的自学能力和问题解决能力。关注AI前沿技术，善于将新技术应用于实际项目。
有强烈的责任心和团队协作精神，期望在AI+电商方向持续深耕。"""

    return {"code": 0, "data": {"text": sample.strip()}}


# ==================== 静态文件 ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
