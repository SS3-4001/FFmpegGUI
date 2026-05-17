# FFmpegGUI
一个比较普通的，FFmpeg的GUI工具，还在更新中
# FFmpeg GUI Neptune

一个用 PyQt6 写的 FFmpeg 图形界面工具，目前支持 10+ 功能。

## 功能
- 格式转换 / 压缩 / 裁剪 / 水印...
- 批量处理 / 媒体信息 / 自动字幕...
- 深色/浅色主题，跟随系统

## 安装
pip install PyQt6
# 还需要 ffmpeg 在 PATH 里

## 运行
python main.p

## 已知问题
- 自动字幕需要额外安装 whisper
- H.266 编码需要编译版 ffmpeg
- 在系统为浅色模式的情况下，切换深色模式会导致部分界面字体不更改颜色

## 截图
<img width="959" height="567" alt="屏幕截图 2026-05-17 132518" src="https://github.com/user-attachments/assets/741f5b0c-b879-4bdc-9cb0-9488f451cc94" />

<img width="958" height="562" alt="屏幕截图 2026-05-17 132537" src="https://github.com/user-attachments/assets/55e8210a-f204-4b89-8e6a-9555b0fc18a7" />


