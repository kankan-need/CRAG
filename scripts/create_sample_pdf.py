"""生成测试 PDF 供 MinerU 解析"""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from pathlib import Path

# 使用系统自带字体或宋体（Windows）
def register_chinese_font():
    try:
        # Windows 宋体
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        return 'SimSun'
    except Exception:
        try:
            pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
            return 'SimHei'
        except Exception:
            return 'Helvetica'

ROOT = Path(__file__).resolve().parent.parent
PDF_OUT = ROOT / "data" / "pdf_input"
CONTENT = """
# TB/T 30001-2020 铁路接发列车作业

## 1 范围

本文件规定了铁路接发列车作业的基本要求、作业程序、安全规定等内容。
适用于国家铁路、地方铁路及专用铁路的接发列车作业。

## 2 术语和定义

### 2.1 接发列车
指车站值班员、助理值班员等行车人员办理列车接入和发出站线的作业。

### 2.2 行车闭塞
采用信号或凭证，保证同一区间、同一时间只允许一列列车占用的行车方法。

## 3 作业程序

### 3.1 接车作业
1. 确认区间空闲  2. 办理闭塞  3. 准备进路  4. 开放信号  5. 接车  6. 开通区间

### 3.2 发车作业
1. 请求闭塞  2. 办理闭塞  3. 准备进路  4. 开放信号  5. 发车  6. 报点
""".strip()

def main():
    PDF_OUT.mkdir(parents=True, exist_ok=True)
    font_name = register_chinese_font()
    
    doc = SimpleDocTemplate(
        str(PDF_OUT / "sample_railway_std.pdf"),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        'Chinese',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
    )
    h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
    )
    h2 = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
    )
    
    story = []
    for line in CONTENT.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
            continue
        if line.startswith('# '):
            story.append(Paragraph(line[2:], h1))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], h2))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h2))
        else:
            story.append(Paragraph(line, normal))
        story.append(Spacer(1, 6))
    
    doc.build(story)
    print(f"已生成测试 PDF: {PDF_OUT / 'sample_railway_std.pdf'}")

if __name__ == "__main__":
    main()
