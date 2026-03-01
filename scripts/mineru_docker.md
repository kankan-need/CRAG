# MinerU 2.5 本地部署指南

MinerU 2.5 使用 1.2B 参数的视觉语言模型进行 PDF 布局分析和内容识别，支持多级标题（1, 1.1, 1.1.1）的自动识别与切分。

## 0. 已完成的部署步骤

本项目已为你完成以下配置：

- **MinerU 安装**：`mineru[all]` 已安装到 Anaconda 环境
- **MinerU2.5 VLM 模型**：已下载到 `C:\Users\<用户名>\.cache\modelscope\hub\models\OpenDataLab\MinerU2___5-2509-1___2B`
- **配置文件**：`C:\Users\<用户名>\mineru.json` 已自动生成
- **测试 PDF**：已生成 `data/pdf_input/sample_railway_std.pdf`

## 1. 安装 MinerU（如未安装）

```bash
pip install uv
uv pip install -U "mineru[all]" --system
```

### 1.2 从源码安装（可指定 VLM 模型）

```bash
git clone https://github.com/opendatalab/MinerU.git
cd MinerU
uv pip install -e .[all]
```

## 2. MinerU2.5 模型 (OpenDataLab)

论文/文档中提到的 MinerU2.5-2509-1.2B 模型地址：
- ModelScope: https://modelscope.cn/models/OpenDataLab/MinerU2.5-2509-1.2B

使用 `auto` 或 `vlm` 后端时，MinerU 会按需从 ModelScope/HuggingFace 下载该模型。

```bash
# 可选：预先下载模型到本地
pip install modelscope
python -c "
from modelscope import snapshot_download
snapshot_download('OpenDataLab/MinerU2.5-2509-1.2B', cache_dir='./models')
"
```

## 3. 运行模式

| 模式 | 说明 | 硬件要求 |
|------|------|----------|
| pipeline | 混合模式，兼容性好 | CPU 或 6GB+ VRAM |
| auto / vlm | 使用 MinerU2.5 VLM，精度更高 | 10GB+ VRAM, GPU |

### 3.1 CPU / 低显存

```bash
mineru -p ./data/pdf_input -o ./data/pdf_parsed -b pipeline
```

### 3.2 GPU + MinerU2.5 模型

```bash
mineru -p ./data/pdf_input -o ./data/pdf_parsed -b auto
```

## 4. 输出与标题结构

MinerU 输出的 Markdown 中会保留原始文档结构：
- `#` 一级标题
- `##` 二级标题
- `###` 三级标题
- 等

本项目中 `scripts/mineru_parse.py` 会：
1. 调用 MinerU 解析 `data/pdf_input` 下的 PDF
2. 将输出的 `.md` 复制到 `data/knowledge_base`
3. 便于后续按多级标题切分后存入向量库

## 5. 铁路标准 PDF 获取

1. 访问 https://hbba.sacinfo.org.cn/stdList
2. 选择「国家铁路局」或行业代码「TB铁路」
3. 下载所需标准的 PDF
4. 放入 `data/pdf_input` 目录
5. 运行 `python scripts/mineru_parse.py`
