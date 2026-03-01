@echo off
chcp 65001 >nul
set MINERU_MODEL_SOURCE=modelscope
cd /d d:\CRAG

echo 使用 auto 模式（MinerU2.5 VLM，需 10GB+ 显存）...
mineru -p data/pdf_input -o data/pdf_parsed -b auto

echo.
echo 解析完成。输出目录: data\pdf_parsed
pause
