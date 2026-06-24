/**
 * 智能简历分析系统 — 前端应用
 * Chart.js 可视化 + 文件上传 + API 交互
 */

let radarChart = null;
let selectedFile = null;
let lastAnalysisData = null;

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    loadJobList();
});

// ==================== 文件上传 ====================

function handleDragOver(e) {
    e.preventDefault();
    document.getElementById('uploadZone').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    document.getElementById('uploadZone').classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    document.getElementById('uploadZone').classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) setFile(file);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) setFile(file);
}

function setFile(file) {
    const validTypes = ['.pdf', '.docx', '.txt',
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(ext) && !validTypes.includes(file.type)) {
        alert('仅支持 PDF / DOCX / TXT 格式文件');
        return;
    }

    selectedFile = file;
    const preview = document.getElementById('filePreview');
    preview.style.display = 'flex';
    document.getElementById('fileName').textContent = `${file.name} (${formatSize(file.size)})`;

    // 清空文本输入
    document.getElementById('resumeText').value = '';
}

function removeFile() {
    selectedFile = null;
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('fileInput').value = '';
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
}

// ==================== 简历分析 ====================

async function analyzeResume() {
    const textInput = document.getElementById('resumeText').value.trim();
    if (!selectedFile && !textInput) {
        showTip('⚠️ 请上传简历文件或粘贴简历文本', 'error');
        return;
    }

    showLoading(true);
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('analysisResults').style.display = 'none';

    try {
        let res;
        if (selectedFile) {
            const formData = new FormData();
            formData.append('file', selectedFile);
            res = await fetch('/api/analyze', { method: 'POST', body: formData });
        } else {
            const formData = new FormData();
            formData.append('text', textInput);
            res = await fetch('/api/analyze', { method: 'POST', body: formData });
        }

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || '分析失败');
        }

        const result = await res.json();
        if (result.code !== 0) throw new Error(result.message || '分析异常');

        lastAnalysisData = result.data;
        renderResults(result.data);
        document.getElementById('analysisResults').style.display = 'block';
        showTip('✅ 分析完成！', 'success');
    } catch (err) {
        showTip('❌ ' + err.message, 'error');
        document.getElementById('emptyState').style.display = 'flex';
    } finally {
        showLoading(false);
        document.getElementById('analyzeBtn').disabled = false;
    }
}

// ==================== 结果渲染 ====================

function renderResults(data) {
    renderScores(data.scores);
    renderRadarChart(data.radar);
    renderSkillBars(data.skill_breakdown);
    renderSuggestions(data.suggestions);
    renderSummary(data.parsed);
}

function renderScores(scores) {
    const section = document.getElementById('scoreSection');

    const colorMap = {
        'A': 'grade-A', 'B': 'grade-B', 'C': 'grade-C', 'D': 'grade-D', 'F': 'grade-F'
    };

    section.innerHTML = `
        <div class="score-card total">
            <div>
                <div class="score-label">综合评分</div>
                <div class="score-value">${scores.total}</div>
                <div class="score-sub">满分100分</div>
            </div>
            <div>
                <span class="grade-badge ${colorMap[scores.grade]}">${scores.grade}</span>
            </div>
            <div style="flex:1;">
                <div style="font-size:14px;font-weight:500;">${scores.grade_desc}</div>
            </div>
        </div>
        <div class="score-card">
            <div class="score-label">📋 完整度</div>
            <div class="score-value" style="color:${scoreColor(scores.completeness, 30)}">${scores.completeness}</div>
            <div class="score-sub">/ 30分</div>
        </div>
        <div class="score-card">
            <div class="score-label">🛠️ 技能</div>
            <div class="score-value" style="color:${scoreColor(scores.skills, 25)}">${scores.skills}</div>
            <div class="score-sub">/ 25分</div>
        </div>
        <div class="score-card">
            <div class="score-label">💼 经验</div>
            <div class="score-value" style="color:${scoreColor(scores.experience, 25)}">${scores.experience}</div>
            <div class="score-sub">/ 25分</div>
        </div>
        <div class="score-card">
            <div class="score-label">📝 格式</div>
            <div class="score-value" style="color:${scoreColor(scores.format, 20)}">${scores.format}</div>
            <div class="score-sub">/ 20分</div>
        </div>
    `;
}

function scoreColor(score, max) {
    const ratio = score / max;
    if (ratio >= 0.8) return '#10b981';
    if (ratio >= 0.6) return '#6366f1';
    if (ratio >= 0.4) return '#f59e0b';
    return '#ef4444';
}

function renderRadarChart(radarData) {
    const ctx = document.getElementById('radarChart').getContext('2d');

    if (radarChart) radarChart.destroy();

    const colors = ['rgba(124,58,237,0.2)', 'rgba(124,58,237,1)'];

    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: radarData.labels,
            datasets: [{
                label: '技能分布',
                data: radarData.values,
                backgroundColor: 'rgba(124,58,237,0.15)',
                borderColor: 'rgba(124,58,237,0.8)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(124,58,237,1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { stepSize: 25, font: { size: 10 }, backdropColor: 'transparent' },
                    pointLabels: { font: { size: 11, weight: '500' } },
                    grid: { color: 'rgba(0,0,0,0.06)' },
                }
            },
            plugins: {
                legend: { display: false },
            }
        }
    });
}

function renderSkillBars(breakdown) {
    const container = document.getElementById('skillBars');
    if (!breakdown || breakdown.length === 0) {
        container.innerHTML = '<p style="color:#9ca3af;text-align:center;padding:40px;">未检测到足够技能信息</p>';
        return;
    }

    container.innerHTML = breakdown.map(b => `
        <div class="skill-bar-item">
            <div class="skill-bar-header">
                <span class="skill-bar-label">${b.category}</span>
                <span class="skill-bar-count">${b.count}项 (${b.percentage}%)</span>
            </div>
            <div class="skill-bar-track">
                <div class="skill-bar-fill" style="width:${b.percentage}%"></div>
            </div>
            <div class="skill-bar-tags">
                ${b.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function renderSuggestions(suggestions) {
    const container = document.getElementById('suggestionsList');
    const priorityLabels = { high: '🔴 优先', medium: '🟡 建议', low: '🔵 可选' };

    container.innerHTML = suggestions.map((s, i) => `
        <div class="suggestion-item priority-${s.priority}">
            <span class="suggestion-priority">${priorityLabels[s.priority] || s.priority}</span>
            <div class="suggestion-content">
                <div class="suggestion-category">${s.category}</div>
                <div class="suggestion-tip">${s.tip}</div>
            </div>
        </div>
    `).join('');
}

function renderSummary(parsed) {
    const container = document.getElementById('resumeSummary');
    const items = [
        { label: '👤 姓名', value: parsed.name },
        { label: '📧 邮箱', value: parsed.email },
        { label: '📱 电话', value: parsed.phone },
        { label: '🎓 教育背景', value: parsed.education },
        { label: '⏳ 预估经验', value: parsed.experience_years ? parsed.experience_years + ' 年' : null },
        { label: '🛠️ 检测技能', value: parsed.skills?.length ? parsed.skills.length + ' 项' : null },
        { label: '📁 项目经验', value: parsed.projects?.length ? parsed.projects.length + ' 个' : null },
        { label: '📝 简历字数', value: parsed.word_count ? parsed.word_count + ' 字' : null },
        { label: '🏷️ 技能列表', value: parsed.skills?.slice(0, 8).join(' · ') },
    ];

    container.innerHTML = items.map(item => `
        <div class="summary-item">
            <div class="summary-item-label">${item.label}</div>
            <div class="summary-item-value ${item.value ? '' : 'empty'}">
                ${item.value || '未检测到'}
            </div>
        </div>
    `).join('');
}

// ==================== 岗位匹配 ====================

async function loadJobList() {
    try {
        const res = await fetch('/api/jobs');
        const { data } = await res.json();
        const select = document.getElementById('jobSelect');
        data.forEach(job => {
            const opt = document.createElement('option');
            opt.value = job.title;
            opt.textContent = `${job.title} (${job.salary_range})`;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error('加载岗位列表失败:', err);
    }
}

async function matchJob() {
    const jobTitle = document.getElementById('jobSelect').value;
    if (!jobTitle) {
        alert('请选择目标岗位');
        return;
    }

    const textInput = document.getElementById('resumeText').value.trim();
    if (!selectedFile && !textInput) {
        // 尝试使用上一次分析结果
        if (lastAnalysisData) {
            // 用已解析的数据做匹配
        } else {
            alert('请先上传简历或进行分析');
            return;
        }
    }

    showLoading(true);

    try {
        const formData = new FormData();
        if (selectedFile) {
            formData.append('file', selectedFile);
        } else if (textInput) {
            formData.append('text', textInput);
        }
        formData.append('job_title', jobTitle);

        const res = await fetch('/api/match', { method: 'POST', body: formData });
        const result = await res.json();

        if (result.code !== 0) {
            alert(result.message || '匹配失败');
            return;
        }

        renderMatchResult(result.data.match);
    } catch (err) {
        alert('匹配请求失败: ' + err.message);
    } finally {
        showLoading(false);
    }
}

function renderMatchResult(match) {
    const container = document.getElementById('matchResult');
    container.style.display = 'block';

    const rateClass = match.match_rate >= 70 ? 'high' : match.match_rate >= 50 ? 'mid' : 'low';
    const rateColor = match.match_rate >= 70 ? '#059669' : match.match_rate >= 50 ? '#d97706' : '#dc2626';

    container.innerHTML = `
        <div class="match-header">
            <div>
                <strong>${match.job_title}</strong>
                <span style="font-size:12px;color:#6b7280;margin-left:8px;">${match.salary_range} · ${match.demand}</span>
            </div>
            <div class="match-rate ${rateClass}" style="color:${rateColor}">${match.match_rate}%</div>
        </div>
        <div class="match-detail">
            <p>${match.verdict}</p>
            ${match.matched_keywords.length > 0 ? `
                <p style="margin-top:8px;">
                    <span class="label">✅ 匹配关键词：</span>
                    ${match.matched_keywords.map(k => `<span class="skill-tag" style="background:#d1fae5;color:#065f46;">${k}</span>`).join(' ')}
                </p>
            ` : ''}
        </div>
        ${match.missing_must.length > 0 ? `
            <div class="match-missing">
                <div class="match-missing-title" style="color:#dc2626;">⚠️ 缺失的必备技能：</div>
                ${match.missing_must.map(s => `<span class="missing-tag">${s}</span>`).join(' ')}
            </div>
        ` : ''}
        ${match.missing_nice.length > 0 ? `
            <div class="match-missing" style="border-color:#fcd34d;">
                <div class="match-missing-title" style="color:#d97706;">💡 建议补充的加分技能：</div>
                ${match.missing_nice.map(s => `<span class="missing-tag" style="background:#fef3c7;color:#92400e;">${s}</span>`).join(' ')}
            </div>
        ` : ''}
    `;
}

// ==================== 示例简历 ====================

async function loadSample() {
    try {
        const res = await fetch('/api/sample');
        const { data } = await res.json();
        document.getElementById('resumeText').value = data.text;
        removeFile();
        showTip('📋 示例简历已加载，点击「开始分析」查看AI分析报告', 'info');
    } catch (err) {
        console.error('加载示例失败:', err);
    }
}

// ==================== 工具函数 ====================

function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function showTip(msg, type) {
    const tip = document.getElementById('analyzeTip');
    tip.textContent = msg;
    tip.style.color = type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#6b7280';
    if (type === 'success') {
        setTimeout(() => { tip.textContent = ''; }, 5000);
    }
}

// 快捷键 Ctrl+Enter 分析
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        analyzeResume();
    }
});
