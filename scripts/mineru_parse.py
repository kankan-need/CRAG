"""
使用 MinerU 解析 PDF，保留多级标题结构 (1, 1.1, 1.1.1)
MinerU 输出 Markdown 时会保留 # ## ### 等标题层级
"""
import sys
import subprocess
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
PDF_IN = ROOT / "data" / "pdf_input"
PDF_OUT = ROOT / "data" / "pdf_parsed"
KB_DIR = ROOT / "data" / "knowledge_base"


def check_mineru():
    """检查 MinerU 是否已安装"""
    try:
        import mineru
        return True
    except ImportError:
        return False


def run_mineru_cli(pdf_path: Path, output_dir: Path, backend: str = "pipeline"):
    """
    调用 MinerU 命令行解析 PDF
    backend: pipeline (CPU/兼容) 或 auto (GPU/VLM，需 MinerU2.5 模型)
    """
    cmd = [
        sys.executable, "-m", "mineru",
        "-p", str(pdf_path),
        "-o", str(output_dir),
        "-b", backend,
    ]
    subprocess.run(cmd, check=True)


def post_process_markdown(md_path: Path, out_path: Path):
    """
    后处理：将 MinerU 输出的 Markdown 中的 # ## ### 映射为 1, 1.1, 1.1.1 风格
    便于后续按标题切分
    """
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    result = []
    counters = [0] * 6  # 支持 6 级标题
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            parts = line.split(" ", 1)
            level = len(parts[0])  # ### -> 3
            title = parts[1].strip() if len(parts) > 1 else ""
            # 更新计数器
            counters[level - 1] += 1
            for i in range(level, 6):
                counters[i] = 0
            num_prefix = ".".join(str(c) for c in counters[:level] if c > 0)
            result.append(f"\n## {num_prefix} {title}\n")
        else:
            result.append(line)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(result).replace("\n\n\n", "\n\n"), encoding="utf-8")


def main():
    PDF_IN.mkdir(parents=True, exist_ok=True)
    PDF_OUT.mkdir(parents=True, exist_ok=True)
    
    if not check_mineru():
        print("未安装 MinerU，请运行: pip install mineru[all]")
        print("或: uv pip install -U \"mineru[all]\"")
        return 1
    
    pdfs = list(PDF_IN.glob("**/*.pdf"))
    if not pdfs:
        print(f"请在 {PDF_IN} 中放入 PDF 文件")
        print("铁路标准 PDF 可从以下渠道获取:")
        print("  - https://hbba.sacinfo.org.cn/stdList 选择 TB铁路")
        print("  - https://down.waizi.org.cn/TB/")
        return 1
    
    backend = "pipeline"  # 纯 CPU 可用；有 GPU 可改为 auto
    print("使用 MinerU 解析 PDF (backend=%s)..." % backend)
    
    for pdf in pdfs:
        name = pdf.stem
        out_dir = PDF_OUT / name
        print(f"解析: {pdf.name}")
        try:
            run_mineru_cli(pdf, out_dir, backend=backend)
            # 将输出的 md 复制到知识库
            md_files = list(out_dir.rglob("*.md"))
            for mf in md_files:
                dest = KB_DIR / f"{name}_{mf.name}"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(mf.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                print(f"  已复制到知识库: {dest.name}")
        except Exception as e:
            print(f"  解析失败: {e}")
    
    print("完成。请运行 python main.py build 重建向量库。")


if __name__ == "__main__":
    sys.exit(main() or 0)
