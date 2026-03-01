@echo off
chcp 65001 >nul
set MINERU_MODEL_SOURCE=modelscope
cd /d d:\CRAG

echo 使用 pipeline 模式（CPU，兼容性好）...
mineru -p data/pdf_input -o data/pdf_parsed -b pipeline

echo.
echo 解析完成。输出目录: data\pdf_parsed
pause
