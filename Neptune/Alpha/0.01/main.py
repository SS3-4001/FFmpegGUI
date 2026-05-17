import sys
import subprocess
import os
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ========== 配色方案 ==========
DARK_COLORS = {
    'bg': '#0A1628', 'card': '#11223B', 'text': '#E1E9F5',
    'border': '#2A4B7C', 'button': '#1A3454', 'button_hover': '#3A6EA5',
    'button_press': '#0F2942', 'group_border': '#2A4B7C',
}
LIGHT_COLORS = {
    'bg': '#FFFFFF', 'card': '#F8FAFE', 'text': '#1E2A3A',
    'border': '#C5D9F0', 'button': '#EBF2FA', 'button_hover': '#D4E6FB',
    'button_press': '#B8D6F5', 'group_border': '#C5D9F0',
}

def get_stylesheet(colors):
    return f"""
    QMainWindow {{ background-color: {colors['bg']}; }}
    
    /* ========== 选项卡区域 ========== */
    QTabWidget::pane {{ 
        background-color: {colors['card']}; 
        border: 1px solid {colors['border']}; 
        border-radius: 10px; 
        padding: 10px;
    }}
    QTabWidget::pane > QWidget {{
        background-color: {colors['card']};
    }}
    QTabWidget::tab-bar {{
        alignment: center;
    }}
    QTabBar::tab {{ 
        background-color: {colors['button']}; 
        color: {colors['text']} !important; 
        padding: 6px 12px; 
        margin: 1px; 
        border-radius: 6px; 
        font-weight: bold;
        border: none;
    }}
    QTabBar::tab:selected {{ 
        background-color: {colors['button_hover']}; 
        color: {colors['text']} !important;
    }}
    QTabBar::tab:hover {{ 
        background-color: {colors['button_hover']}; 
        color: {colors['text']} !important;
    }}
    QTabBar::tab:!selected {{ 
        background-color: {colors['button']}; 
        color: {colors['text']} !important;
    }}
    
    /* ========== 基础控件 ========== */
    QLabel {{ 
        color: {colors['text']} !important; 
        font-size: 12px; 
    }}
    
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget {{
        background-color: {colors['card']}; 
        color: {colors['text']} !important; 
        border: 1px solid {colors['border']}; 
        border-radius: 6px; 
        padding: 6px;
        min-height: 24px;
    }}
    QLineEdit:focus, QComboBox:focus {{ 
        border: 2px solid {colors['button_hover']}; 
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {colors['card']};
        color: {colors['text']} !important;
        border: 1px solid {colors['border']};
        selection-background-color: {colors['button_hover']};
        selection-color: {colors['text']} !important;
    }}
    
    /* ========== 按钮 ========== */
    QPushButton {{
        background-color: {colors['button']}; 
        color: {colors['text']} !important; 
        border: none; 
        border-radius: 6px; 
        padding: 8px 16px;
        font-weight: bold;
        min-width: 80px;
    }}
    QPushButton:hover {{ 
        background-color: {colors['button_hover']}; 
        color: {colors['text']} !important;
    }}
    QPushButton:pressed {{ 
        background-color: {colors['button_press']}; 
        color: {colors['text']} !important;
    }}
    
    /* ========== 分组框 ========== */
    QGroupBox {{ 
        color: {colors['text']} !important; 
        border: 1px solid {colors['group_border']}; 
        border-radius: 10px; 
        margin-top: 12px;
        padding-top: 8px;
        font-weight: bold;
        background-color: {colors['card']};
    }}
    QGroupBox::title {{ 
        subcontrol-origin: margin; 
        left: 12px; 
        padding: 0 8px; 
        color: {colors['text']} !important;
    }}
    
    /* ========== 滑块 ========== */
    QSlider::groove:horizontal {{
        border: 1px solid {colors['border']};
        height: 6px;
        background: {colors['button']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {colors['button_hover']};
        border: none;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{ 
        background: {colors['border']}; 
    }}
    QSlider::sub-page:horizontal {{
        background: {colors['button_hover']};
        border-radius: 3px;
    }}
    
    /* ========== 进度条 ========== */
    QProgressBar {{
        border: 1px solid {colors['border']};
        border-radius: 6px;
        text-align: center;
        background: {colors['card']};
        color: {colors['text']} !important;
    }}
    QProgressBar::chunk {{
        background-color: {colors['button_hover']};
        border-radius: 5px;
    }}
    
    /* ========== 滚动条 ========== */
    QScrollBar:vertical {{
        background-color: {colors['card']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {colors['button_hover']};
        border-radius: 5px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {colors['border']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """

def get_system_theme():
    if sys.platform != 'win32': return 'light'
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return 'light' if value == 1 else 'dark'
    except: return 'light'

def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


class FFmpegRunner(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, cmd, output_file):
        super().__init__()
        self.cmd = cmd
        self.output_file = output_file
        self.process = None
    
    def run(self):
        try:
            self.log.emit(f"▶️ 运行: {' '.join(self.cmd)}")
            self.process = QProcess()
            self.process.start(self.cmd[0], self.cmd[1:])
            self.process.waitForFinished(-1)
            if self.process.exitCode() == 0:
                self.finished.emit(True, self.output_file)
            else:
                error = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')[-500:]
                self.finished.emit(False, error)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def stop(self):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()


class BatchRunner(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(int, int)
    
    def __init__(self, file_list, output_format):
        super().__init__()
        self.file_list = file_list
        self.output_format = output_format
        self._is_running = True
    
    def stop(self):
        self._is_running = False
    
    def run(self):
        total = len(self.file_list)
        success = 0
        for i, src in enumerate(self.file_list):
            if not self._is_running:
                self.log.emit("⏹️ 批量处理已取消")
                break
            dst = src.rsplit('.', 1)[0] + f"_converted.{self.output_format}"
            cmd = ["ffmpeg", "-i", src, "-c:v", "libx264", "-c:a", "aac", dst, "-y"]
            self.log.emit(f"  [{i+1}/{total}] 转换: {os.path.basename(src)}")
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                success += 1
                self.log.emit(f"    ✅ 完成 → {os.path.basename(dst)}")
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore')[-200:]
                self.log.emit(f"    ❌ 失败: {os.path.basename(src)}\n       {error_msg}")
            self.progress.emit(i+1, total)
        self.finished.emit(success, total)


class FFmpegGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFmpeg GUI Neptune Build Alpha 0.01")
        self.setWindowIcon(self.create_alpha_icon())
        self.setMinimumSize(1000, 750)
        self.current_runner = None
        self.batch_runner = None
   
        if not check_ffmpeg():
            QMessageBox.critical(self, "缺少依赖", 
                "未检测到 FFmpeg！\n\n请前往 https://ffmpeg.org/download.html 下载安装，\n"
                "并确保 ffmpeg 已添加到系统 PATH 环境变量中。")
        
        self.theme_mode = 'system'
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.create_theme_selector()
        self.create_tabs()
        self.apply_theme()
        if self.theme_mode == 'system': 
            self.start_theme_watcher()
        # Ctrl+F 聚焦搜索框
        ctrl_f = QShortcut(QKeySequence("Ctrl+F"), self)
        ctrl_f.activated.connect(lambda: self.search_input.setFocus())

    def create_alpha_icon(self):
        """生成 iOS 风格圆角图标，白底蓝色 Alpha 文字"""
        size = 256
        radius = 55
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 圆角白色背景
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, size, size, radius, radius)

        # 蓝色文字
        painter.setPen(QColor(58, 110, 165))
        painter.setFont(QFont("Segoe UI", 72, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Alpha")

        painter.end()
        return QIcon(pixmap)

    def create_theme_selector(self):
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 10)
        
        # 左侧：主题选择
        theme_layout.addWidget(QLabel("🎨 主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌙 跟随系统", "🌙 深色", "☀️ 浅色"])
        self.theme_combo.setMaximumWidth(120)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        # 中间：弹性空间
        theme_layout.addStretch()
        
        # 右侧：搜索框
        theme_layout.addWidget(QLabel("🔍"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索功能...")
        self.search_input.setMaximumWidth(200)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self.search_tab)
        self.search_input.textChanged.connect(self.search_tab)
        theme_layout.addWidget(self.search_input)
        
        self.main_layout.addWidget(theme_widget)

    def create_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)
        
        # 原有功能
        self.tabs.addTab(self.create_convert_tab(), "📦 格式转换")
        self.tabs.addTab(self.create_compress_tab(), "🗜️ 视频压缩")
        self.tabs.addTab(self.create_cut_tab(), "✂️ 裁剪视频")
        self.tabs.addTab(self.create_crop_tab(), "🔲 裁剪区域")
        self.tabs.addTab(self.create_resolution_tab(), "📐 调整分辨率")
        self.tabs.addTab(self.create_fps_tab(), "🎬 帧率/速度")
        self.tabs.addTab(self.create_rotate_tab(), "🔄 旋转/翻转")
        self.tabs.addTab(self.create_audio_tab(), "🎵 提取音频")
        self.tabs.addTab(self.create_volume_tab(), "🔊 音量调整")
        self.tabs.addTab(self.create_merge_tab(), "🔗 视频拼接")
        self.tabs.addTab(self.create_screenshot_tab(), "📸 视频截图")
        self.tabs.addTab(self.create_gif_tab(), "🎞️ GIF动图")
        self.tabs.addTab(self.create_watermark_tab(), "💧 添加水印")
        self.tabs.addTab(self.create_batch_tab(), "⚡ 批量处理")
        self.tabs.addTab(self.create_media_info_tab(), "📊 媒体信息")
        self.tabs.addTab(self.create_batch_screenshot_tab(), "🖼️ 批量截图")
        self.tabs.addTab(self.create_audio_tools_tab(), "🔉 音频工具")
        self.tabs.addTab(self.create_reverse_tab(), "⏪ 倒放/反序")
        self.tabs.addTab(self.create_preview_tab(), "🎬 视频预览")
        
        # 新功能
        self.tabs.addTab(self.create_subtitle_tab(), "🎤 自动字幕")
        self.tabs.addTab(self.create_codec_tab(), "🎬 高级编码")
        self.tabs.addTab(self.create_audio_pro_tab(), "🔊 专业音频")
        self.tabs.addTab(self.create_video_fix_tab(), "✨ 画质增强")
        
        self.main_layout.addWidget(self.tabs)
        
        # 日志区域
        log_group = QGroupBox("📋 执行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(130)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        self.main_layout.addWidget(log_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        self.main_layout.addWidget(self.progress_bar)

    def search_tab(self):
        keyword = self.search_input.text().strip().lower()
        if not keyword:
            return
        
        tab_names = [
            "格式转换", "视频压缩", "裁剪视频", "裁剪区域",
            "调整分辨率", "帧率速度", "旋转翻转", "提取音频",
            "音量调整", "视频拼接", "视频截图", "GIF动图",
            "添加水印", "批量处理", "媒体信息", "批量截图",
            "音频工具", "倒放", "视频预览", "自动字幕", "高级编码", "专业音频", "画质增强"
        ]
        
        keyword_map = {
            "格式": "格式转换", "转换": "格式转换", "转码": "格式转换",
            "压缩": "视频压缩", "变小": "视频压缩", "瘦身": "视频压缩",
            "剪": "裁剪视频", "切": "裁剪视频", "截取": "裁剪视频",
            "裁切": "裁剪区域", "抠图": "裁剪区域",
            "大小": "调整分辨率", "尺寸": "调整分辨率", "放大": "调整分辨率", "缩小": "调整分辨率",
            "快": "帧率速度", "慢": "帧率速度", "加速": "帧率速度", "减速": "帧率速度",
            "旋转": "旋转翻转", "转": "旋转翻转", "镜像": "旋转翻转",
            "音乐": "提取音频", "声音": "提取音频", "配音": "提取音频",
            "音量": "音量调整", "大声": "音量调整", "小声": "音量调整",
            "合并": "视频拼接", "连接": "视频拼接", "拼": "视频拼接",
            "截图": "视频截图", "抓图": "视频截图",
            "动图": "GIF动图", "动画": "GIF动图",
            "水印": "添加水印", "logo": "添加水印",
            "批量": "批量处理", "多个": "批量处理",
            "信息": "媒体信息", "详情": "媒体信息", "属性": "媒体信息",
            "墙": "批量截图", "缩略图": "批量截图",
            "音频": "音频工具", "音频处理": "音频工具",
            "倒放": "倒放", "反向": "倒放",
            "预览": "视频预览", "播放": "视频预览",
            "字幕": "自动字幕", "语音": "自动字幕", "whisper": "自动字幕",
            "编码": "高级编码", "vvc": "高级编码", "av1": "高级编码",
            "音轨": "专业音频", "重采样": "专业音频", "均衡": "专业音频",
            "锐化": "画质增强", "降噪": "画质增强", "稳定": "画质增强"
        }
        
        matched_tab = None
        for k, v in keyword_map.items():
            if k in keyword:
                matched_tab = v
                break
        
        if not matched_tab:
            for name in tab_names:
                if keyword in name.lower():
                    matched_tab = name
                    break
        
        if matched_tab:
            for i in range(self.tabs.count()):
                if matched_tab in self.tabs.tabText(i):
                    self.tabs.setCurrentIndex(i)
                    self.log(f"🔍 已跳转到「{matched_tab}」")
                    break
        elif keyword:
            self.log(f"🔍 未找到与「{keyword}」相关的功能，试试：压缩、裁剪、水印、批量...")

    def log(self, msg):
        self.log_text.append(msg)
        QApplication.processEvents()

    def on_theme_changed(self, idx):
        modes = ['system', 'dark', 'light']
        self.theme_mode = modes[idx]
        self.apply_theme()

    def start_theme_watcher(self):
        self._last_theme = get_system_theme()
        self._theme_timer = QTimer()
        self._theme_timer.timeout.connect(self.check_theme_change)
        self._theme_timer.start(1000)

    def check_theme_change(self):
        if self.theme_mode == 'system':
            cur = get_system_theme()
            if cur != self._last_theme:
                self._last_theme = cur
                self.apply_theme()

    def apply_theme(self):
        try:
            if self.theme_mode == 'system':
                theme = get_system_theme()
                colors = DARK_COLORS if theme == 'dark' else LIGHT_COLORS
            elif self.theme_mode == 'dark':
                colors = DARK_COLORS
            else:
                colors = LIGHT_COLORS
        except:
            colors = LIGHT_COLORS
        self.setStyleSheet(get_stylesheet(colors))
        
        # 设置调色板（解决复选框文字颜色问题）
        palette = self.palette()
        text_color = QColor(colors['text'])
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        self.setPalette(palette)

    def select_file(self, edit, filter_str="视频/音频 (*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.png *.jpg)"):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", filter_str)
        if path: edit.setText(path)

    def select_output_folder(self, edit):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder: edit.setText(folder)

    def run_ffmpeg(self, cmd, output_file):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.current_runner = FFmpegRunner(cmd, output_file)
        self.current_runner.log.connect(self.log)
        self.current_runner.finished.connect(self.on_ffmpeg_finished)
        self.current_runner.start()

    def on_ffmpeg_finished(self, success, msg):
        self.progress_bar.setVisible(False)
        self.current_runner = None
        if success:
            self.log(f"✅ 成功: {msg}")
            QMessageBox.information(self, "完成", f"处理完成！\n{msg}")
        else:
            self.log(f"❌ 失败: {msg}")
            QMessageBox.critical(self, "错误", f"处理失败:\n{msg}")

    # ========== 选项卡 1: 格式转换 ==========
    def create_convert_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.conv_input = QLineEdit()
        self.conv_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.conv_input))
        row1.addWidget(self.conv_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("转换设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("输出格式:"))
        self.conv_format = QComboBox()
        self.conv_format.addItems(["mp4", "mkv", "mov", "avi", "webm"])
        row2.addWidget(self.conv_format)
        row2.addStretch()
        gl2.addLayout(row2)
        
        self.use_hevc_convert = QCheckBox("使用 H.265/HEVC 编码（文件更小，兼容性稍差）")
        gl2.addWidget(self.use_hevc_convert)
        
        layout.addWidget(group2)
        
        btn_run = QPushButton("🚀 开始转换")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_convert)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_convert(self):
        src = self.conv_input.text()
        if not src: self.log("❌ 请选择文件"); return
        ext = self.conv_format.currentText()
        dst = src.rsplit('.', 1)[0] + f"_converted.{ext}"
        if ext == "mp4" and self.use_hevc_convert.isChecked():
            cmd = ["ffmpeg", "-i", src, "-c:v", "libx265", "-c:a", "aac", dst, "-y"]
        else:
            cmd = ["ffmpeg", "-i", src, "-c:v", "libx264", "-c:a", "aac", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 2: 视频压缩 ==========
    def create_compress_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.comp_input = QLineEdit()
        self.comp_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.comp_input))
        row1.addWidget(self.comp_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("压缩设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("质量 (CRF):"))
        self.crf = QSlider(Qt.Orientation.Horizontal)
        self.crf.setRange(18, 35)
        self.crf.setValue(23)
        self.crf_label = QLabel("23")
        self.crf.valueChanged.connect(lambda v: self.crf_label.setText(str(v)))
        row2.addWidget(self.crf)
        row2.addWidget(self.crf_label)
        row2.addStretch()
        gl2.addLayout(row2)
        
        info_label = QLabel("💡 数值越小画质越好但文件越大：18(极佳) → 23(推荐) → 35(小体积)")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        
        self.use_hevc = QCheckBox("使用 H.265/HEVC 编码（文件更小，兼容性稍差）")
        gl2.addWidget(self.use_hevc)
        
        layout.addWidget(group2)
        
        btn_run = QPushButton("🗜️ 开始压缩")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_compress)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_compress(self):
        src = self.comp_input.text()
        if not src: self.log("❌ 请选择文件"); return
        dst = src.rsplit('.', 1)[0] + f"_compressed.mp4"
        if self.use_hevc.isChecked():
            cmd = ["ffmpeg", "-i", src, "-c:v", "libx265", "-crf", str(self.crf.value()), "-c:a", "aac", "-b:a", "128k", dst, "-y"]
        else:
            cmd = ["ffmpeg", "-i", src, "-c:v", "libx264", "-crf", str(self.crf.value()), "-c:a", "aac", "-b:a", "128k", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 3: 裁剪视频 ==========
    def create_cut_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.cut_input = QLineEdit()
        self.cut_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.cut_input))
        row1.addWidget(self.cut_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("裁剪设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("开始时间:"))
        self.start_time = QLineEdit()
        self.start_time.setPlaceholderText("00:01:00")
        row2.addWidget(self.start_time)
        row2.addWidget(QLabel("时长:"))
        self.duration = QLineEdit()
        self.duration.setPlaceholderText("00:00:30")
        row2.addWidget(self.duration)
        row2.addStretch()
        gl2.addLayout(row2)
        layout.addWidget(group2)
        
        btn_run = QPushButton("✂️ 开始裁剪")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_cut)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_cut(self):
        src = self.cut_input.text()
        if not src: self.log("❌ 请选择文件"); return
        dst = src.rsplit('.', 1)[0] + "_cut.mp4"
        cmd = ["ffmpeg", "-i", src]
        if self.start_time.text(): cmd.extend(["-ss", self.start_time.text()])
        if self.duration.text(): cmd.extend(["-t", self.duration.text()])
        cmd.extend(["-c", "copy", dst, "-y"])
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 4: 裁剪区域 ==========
    def create_crop_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.crop_input = QLineEdit()
        self.crop_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.crop_input))
        row1.addWidget(self.crop_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("裁剪区域设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("宽度:"))
        self.crop_w = QSpinBox()
        self.crop_w.setRange(1, 9999)
        self.crop_w.setValue(640)
        row2.addWidget(self.crop_w)
        row2.addWidget(QLabel("高度:"))
        self.crop_h = QSpinBox()
        self.crop_h.setRange(1, 9999)
        self.crop_h.setValue(480)
        row2.addWidget(self.crop_h)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("起始X:"))
        self.crop_x = QSpinBox()
        self.crop_x.setRange(0, 9999)
        row3.addWidget(self.crop_x)
        row3.addWidget(QLabel("起始Y:"))
        self.crop_y = QSpinBox()
        self.crop_y.setRange(0, 9999)
        row3.addWidget(self.crop_y)
        row3.addStretch()
        gl2.addLayout(row3)
        
        info_label = QLabel("💡 裁剪区域 = 从 (X,Y) 开始，截取 宽度×高度 的区域")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🔲 开始裁剪")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_crop)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_crop(self):
        src = self.crop_input.text()
        if not src: self.log("❌ 请选择文件"); return
        dst = src.rsplit('.', 1)[0] + f"_crop.mp4"
        cmd = ["ffmpeg", "-i", src, "-vf", f"crop={self.crop_w.value()}:{self.crop_h.value()}:{self.crop_x.value()}:{self.crop_y.value()}", "-c:a", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 5: 调整分辨率 ==========
    def create_resolution_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.res_input = QLineEdit()
        self.res_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.res_input))
        row1.addWidget(self.res_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("分辨率设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("预设:"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["原始", "3840x2160 (4K)","2560x1440 (2K)", "1920x1080 (1080p)", "1280x720 (720p)", "854x480 (480p)", "640x360 (360p)", "426x240 (240p)"])
        row2.addWidget(self.res_combo)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("自定义:"))
        self.res_custom = QLineEdit()
        self.res_custom.setPlaceholderText("例如: 800x600")
        row3.addWidget(self.res_custom)
        row3.addStretch()
        gl2.addLayout(row3)
        layout.addWidget(group2)
        
        btn_run = QPushButton("📐 开始调整")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_resize)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_resize(self):
        src = self.res_input.text()
        if not src: self.log("❌ 请选择文件"); return
        if self.res_custom.text():
            size = self.res_custom.text()
        elif "原始" in self.res_combo.currentText():
            self.log("❌ 请选择分辨率或输入自定义尺寸")
            return
        else:
            size = self.res_combo.currentText().split()[0]
        dst = src.rsplit('.', 1)[0] + f"_resize_{size}.mp4"
        cmd = ["ffmpeg", "-i", src, "-vf", f"scale={size}", "-c:a", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 6: 帧率/速度 ==========
    def create_fps_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.fps_input = QLineEdit()
        self.fps_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.fps_input))
        row1.addWidget(self.fps_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("播放设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("帧率:"))
        self.fps = QComboBox()
        self.fps.addItems(["原始", "120", "60", "50", "30", "25", "24", "15", "10"])
        row2.addWidget(self.fps)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("播放速度:"))
        self.speed = QDoubleSpinBox()
        self.speed.setRange(0.25, 4.0)
        self.speed.setValue(1.0)
        self.speed.setSingleStep(0.25)
        row3.addWidget(self.speed)
        row3.addWidget(QLabel("倍"))
        row3.addStretch()
        gl2.addLayout(row3)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🎬 开始处理")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_fps)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_fps(self):
        src = self.fps_input.text()
        if not src: self.log("❌ 请选择文件"); return
        dst = src.rsplit('.', 1)[0] + f"_adjusted.mp4"
        
        filters = []
        if self.speed.value() != 1.0:
            filters.append(f"setpts={1/self.speed.value()}*PTS")
        if self.fps.currentText() != "原始":
            filters.append(f"fps={self.fps.currentText()}")
        
        cmd = ["ffmpeg", "-i", src]
        if filters:
            cmd.extend(["-filter:v", ",".join(filters)])
        if self.speed.value() != 1.0:
            cmd.extend(["-filter:a", f"atempo={self.speed.value()}"])
        cmd.extend(["-c:a", "aac", dst, "-y"])
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 7: 旋转/翻转 ==========
    def create_rotate_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.rot_input = QLineEdit()
        self.rot_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.rot_input))
        row1.addWidget(self.rot_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("旋转/翻转设置")
        gl2 = QVBoxLayout(group2)
        self.rot_combo = QComboBox()
        self.rot_combo.addItems(["顺时针 90°", "逆时针 90°", "旋转 180°", "水平镜像", "垂直镜像"])
        gl2.addWidget(self.rot_combo)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🔄 开始处理")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_rotate)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_rotate(self):
        src = self.rot_input.text()
        if not src: self.log("❌ 请选择文件"); return
        mapping = {"顺时针 90°": "transpose=1", "逆时针 90°": "transpose=2", "旋转 180°": "transpose=2,transpose=2", "水平镜像": "hflip", "垂直镜像": "vflip"}
        dst = src.rsplit('.', 1)[0] + "_rotated.mp4"
        cmd = ["ffmpeg", "-i", src, "-vf", mapping[self.rot_combo.currentText()], "-c:a", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 8: 提取音频 ==========
    def create_audio_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.aud_input = QLineEdit()
        self.aud_input.setPlaceholderText("未选择视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.aud_input))
        row1.addWidget(self.aud_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("音频设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("输出格式:"))
        self.aud_format = QComboBox()
        self.aud_format.addItems(["mp3", "aac", "flac", "wav"])
        row2.addWidget(self.aud_format)
        row2.addStretch()
        gl2.addLayout(row2)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🎵 提取音频")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_audio)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_audio(self):
        src = self.aud_input.text()
        if not src: self.log("❌ 请选择文件"); return
        ext = self.aud_format.currentText()
        dst = src.rsplit('.', 1)[0] + f"_audio.{ext}"
        codec = "libmp3lame" if ext == "mp3" else ext
        cmd = ["ffmpeg", "-i", src, "-vn", "-c:a", codec, dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 9: 音量调整 ==========
    def create_volume_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.vol_input = QLineEdit()
        self.vol_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.vol_input))
        row1.addWidget(self.vol_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("音量设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("音量:"))
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 200)
        self.vol_slider.setValue(100)
        self.vol_label = QLabel("100%")
        self.vol_slider.valueChanged.connect(lambda v: self.vol_label.setText(f"{v}%"))
        row2.addWidget(self.vol_slider)
        row2.addWidget(self.vol_label)
        row2.addStretch()
        gl2.addLayout(row2)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🔊 调整音量")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_volume)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_volume(self):
        src = self.vol_input.text()
        if not src: self.log("❌ 请选择文件"); return
        vol = self.vol_slider.value() / 100.0
        dst = src.rsplit('.', 1)[0] + f"_adjusted.mp4"
        cmd = ["ffmpeg", "-i", src, "-af", f"volume={vol}", "-c:v", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 10: 视频拼接 ==========
    def create_merge_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("视频列表（按顺序拼接）")
        gl = QVBoxLayout(group)
        self.merge_list = QListWidget()
        self.merge_list.setMinimumHeight(150)
        gl.addWidget(self.merge_list)
        
        btn_row = QHBoxLayout()
        btn_add = QPushButton("➕ 添加视频")
        btn_add.clicked.connect(self.add_to_merge)
        btn_remove = QPushButton("➖ 移除选中")
        btn_remove.clicked.connect(lambda: self.merge_list.takeCurrentRow())
        btn_clear = QPushButton("🗑️ 清空")
        btn_clear.clicked.connect(lambda: self.merge_list.clear())
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        gl.addLayout(btn_row)
        
        info_label = QLabel("💡 提示：建议所有视频使用相同的编码格式，否则拼接可能失败。")
        info_label.setWordWrap(True)
        gl.addWidget(info_label)
        layout.addWidget(group)
        
        btn_run = QPushButton("🔗 开始拼接")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_merge)
        layout.addWidget(btn_run)
        return w
    
    def add_to_merge(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多个视频", "", "视频 (*.mp4 *.mkv *.avi)")
        for f in files: 
            self.merge_list.addItem(f)
    
    def do_merge(self):
        if self.merge_list.count() < 2: 
            self.log("❌ 至少需要2个视频")
            return
        
        list_file = os.path.join(os.path.dirname(self.merge_list.item(0).text()), "concat_list.txt")
        with open(list_file, "w", encoding='utf-8') as f:
            for i in range(self.merge_list.count()):
                path = self.merge_list.item(i).text().replace("'", "'\\''")
                f.write(f"file '{path}'\n")
        
        dst = os.path.dirname(self.merge_list.item(0).text()) + "/merged.mp4"
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 11: 视频截图 ==========
    def create_screenshot_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.snap_input = QLineEdit()
        self.snap_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.snap_input))
        row1.addWidget(self.snap_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("截图设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("时间点:"))
        self.snap_time = QLineEdit()
        self.snap_time.setPlaceholderText("留空则截取中间帧")
        row2.addWidget(self.snap_time)
        row2.addStretch()
        gl2.addLayout(row2)
        layout.addWidget(group2)
        
        btn_run = QPushButton("📸 截图")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_screenshot)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_screenshot(self):
        src = self.snap_input.text()
        if not src: self.log("❌ 请选择文件"); return
        dst = src.rsplit('.', 1)[0] + "_screenshot.jpg"
        cmd = ["ffmpeg", "-i", src]
        if self.snap_time.text(): 
            cmd.extend(["-ss", self.snap_time.text()])
        cmd.extend(["-vframes", "1", dst, "-y"])
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 12: GIF动图 ==========
    def create_gif_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.gif_input = QLineEdit()
        self.gif_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.gif_input))
        row1.addWidget(self.gif_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("GIF设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("帧率:"))
        self.gif_fps = QSpinBox()
        self.gif_fps.setRange(5, 30)
        self.gif_fps.setValue(10)
        row2.addWidget(self.gif_fps)
        row2.addWidget(QLabel("宽度:"))
        self.gif_width = QSpinBox()
        self.gif_width.setRange(100, 1920)
        self.gif_width.setValue(480)
        row2.addWidget(self.gif_width)
        row2.addStretch()
        gl2.addLayout(row2)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🎞️ 生成GIF")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_gif)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_gif(self):
        src = self.gif_input.text()
        if not src: self.log("❌ 请选择文件"); return
        dst = src.rsplit('.', 1)[0] + ".gif"
        scale = f"scale={self.gif_width.value()}:-1"
        cmd = ["ffmpeg", "-i", src, "-vf", f"fps={self.gif_fps.value()},{scale}", "-c:v", "gif", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 13: 添加水印 ==========
    def create_watermark_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.wm_input = QLineEdit()
        self.wm_input.setPlaceholderText("未选择视频")
        btn1 = QPushButton("📂 浏览视频")
        btn1.clicked.connect(lambda: self.select_file(self.wm_input))
        row1.addWidget(self.wm_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        
        row2 = QHBoxLayout()
        self.wm_image = QLineEdit()
        self.wm_image.setPlaceholderText("未选择水印图片")
        btn2 = QPushButton("🖼️ 浏览图片")
        btn2.clicked.connect(lambda: self.select_file(self.wm_image, "图片 (*.png *.jpg *.jpeg)"))
        row2.addWidget(self.wm_image)
        row2.addWidget(btn2)
        gl.addLayout(row2)
        layout.addWidget(group)
        
        group2 = QGroupBox("水印位置")
        gl2 = QVBoxLayout(group2)
        self.wm_pos = QComboBox()
        self.wm_pos.addItems(["左上角", "右上角", "左下角", "右下角", "中央"])
        gl2.addWidget(self.wm_pos)
        layout.addWidget(group2)
        
        btn_run = QPushButton("💧 添加水印")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_watermark)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_watermark(self):
        src = self.wm_input.text()
        wm = self.wm_image.text()
        if not src or not wm: 
            self.log("❌ 请选择视频和水印图片")
            return
        pos_map = {
            "左上角": "10:10", 
            "右上角": "main_w-overlay_w-10:10", 
            "左下角": "10:main_h-overlay_h-10", 
            "右下角": "main_w-overlay_w-10:main_h-overlay_h-10", 
            "中央": "(main_w-overlay_w)/2:(main_h-overlay_h)/2"
        }
        dst = src.rsplit('.', 1)[0] + "_watermarked.mp4"
        cmd = ["ffmpeg", "-i", src, "-i", wm, "-filter_complex", f"overlay={pos_map[self.wm_pos.currentText()]}", "-c:a", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)

    # ========== 选项卡 14: 批量处理 ==========
    def create_batch_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("待处理文件列表")
        gl = QVBoxLayout(group)
        self.batch_list = QListWidget()
        self.batch_list.setMinimumHeight(150)
        gl.addWidget(self.batch_list)
        
        btn_row = QHBoxLayout()
        btn_add = QPushButton("➕ 添加文件")
        btn_add.clicked.connect(self.add_to_batch)
        btn_clear = QPushButton("🗑️ 清空")
        btn_clear.clicked.connect(lambda: self.batch_list.clear())
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        gl.addLayout(btn_row)
        layout.addWidget(group)
        
        group2 = QGroupBox("转换设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("目标格式:"))
        self.batch_format = QComboBox()
        self.batch_format.addItems(["mp4", "mkv", "mov", "avi", "webm"])
        row2.addWidget(self.batch_format)
        row2.addStretch()
        gl2.addLayout(row2)
        layout.addWidget(group2)
        
        self.batch_progress = QProgressBar()
        self.batch_progress.setVisible(False)
        layout.addWidget(self.batch_progress)
        
        btn_run = QPushButton("⚡ 批量转换")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_batch)
        layout.addWidget(btn_run)
        
        self.batch_cancel_btn = QPushButton("⏹️ 取消")
        self.batch_cancel_btn.setVisible(False)
        self.batch_cancel_btn.clicked.connect(self.cancel_batch)
        layout.addWidget(self.batch_cancel_btn)
        
        layout.addStretch()
        return w
    
    def add_to_batch(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多个文件", "", "视频 (*.mp4 *.mkv *.avi *.mov)")
        for f in files: 
            self.batch_list.addItem(f)
    
    def do_batch(self):
        if self.batch_list.count() == 0:
            self.log("❌ 请添加文件")
            return
        
        file_list = [self.batch_list.item(i).text() for i in range(self.batch_list.count())]
        self.batch_runner = BatchRunner(file_list, self.batch_format.currentText())
        self.batch_runner.log.connect(self.log)
        self.batch_runner.progress.connect(self.update_batch_progress)
        self.batch_runner.finished.connect(self.on_batch_finished)
        
        self.batch_progress.setVisible(True)
        self.batch_progress.setRange(0, len(file_list))
        self.batch_cancel_btn.setVisible(True)
        self.batch_runner.start()
        self.log(f"📦 开始批量转换 {len(file_list)} 个文件...")
    
    def update_batch_progress(self, current, total):
        self.batch_progress.setValue(current)
        self.batch_progress.setFormat(f"{current}/{total}")
    
    def cancel_batch(self):
        if self.batch_runner:
            self.batch_runner.stop()
            self.batch_cancel_btn.setEnabled(False)
    
    def on_batch_finished(self, success, total):
        self.batch_progress.setVisible(False)
        self.batch_cancel_btn.setVisible(False)
        self.batch_cancel_btn.setEnabled(True)
        self.log(f"✨ 批量处理完成！成功 {success}/{total}")
        self.batch_runner = None

    # ========== 新功能 15: 媒体信息查看 ==========
    def create_media_info_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("选择视频/音频文件")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.info_input = QLineEdit()
        self.info_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.info_input))
        row1.addWidget(self.info_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        btn_info = QPushButton("📊 获取媒体信息")
        btn_info.setMinimumHeight(40)
        btn_info.clicked.connect(self.show_media_info)
        layout.addWidget(btn_info)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.info_text)
        
        layout.addStretch()
        return w
    
    def show_media_info(self):
        src = self.info_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", src]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info_lines = []
                info_lines.append("=" * 50)
                info_lines.append(f"📁 文件: {os.path.basename(src)}")
                info_lines.append("=" * 50)
                
                if 'format' in data:
                    fmt = data['format']
                    info_lines.append(f"\n📦 容器格式: {fmt.get('format_name', 'N/A')}")
                    info_lines.append(f"📏 文件大小: {int(fmt.get('size', 0)) // 1024} KB")
                    info_lines.append(f"⏱️ 时长: {float(fmt.get('duration', 0)):.2f} 秒")
                    info_lines.append(f"📊 总码率: {fmt.get('bit_rate', 'N/A')} bps")
                
                for i, stream in enumerate(data.get('streams', [])):
                    if stream.get('codec_type') == 'video':
                        info_lines.append(f"\n🎬 视频流 #{i}")
                        info_lines.append(f"   编码: {stream.get('codec_name', 'N/A')}")
                        info_lines.append(f"   分辨率: {stream.get('width', 'N/A')} x {stream.get('height', 'N/A')}")
                        info_lines.append(f"   帧率: {stream.get('r_frame_rate', 'N/A')}")
                        info_lines.append(f"   码率: {stream.get('bit_rate', 'N/A')} bps")
                        info_lines.append(f"   像素格式: {stream.get('pix_fmt', 'N/A')}")
                    elif stream.get('codec_type') == 'audio':
                        info_lines.append(f"\n🎵 音频流 #{i}")
                        info_lines.append(f"   编码: {stream.get('codec_name', 'N/A')}")
                        info_lines.append(f"   采样率: {stream.get('sample_rate', 'N/A')} Hz")
                        info_lines.append(f"   声道: {stream.get('channels', 'N/A')}")
                        info_lines.append(f"   码率: {stream.get('bit_rate', 'N/A')} bps")
                
                self.info_text.setText("\n".join(info_lines))
                self.log(f"✅ 已获取 {os.path.basename(src)} 的媒体信息")
            else:
                self.info_text.setText("获取信息失败，请确保文件存在且 ffprobe 可用")
                self.log(f"❌ ffprobe 执行失败")
        except Exception as e:
            self.info_text.setText(f"错误: {str(e)}")
            self.log(f"❌ 获取信息出错: {str(e)}")

    # ========== 新功能 16: 批量截图/缩略图墙 ==========
    def create_batch_screenshot_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.bs_input = QLineEdit()
        self.bs_input.setPlaceholderText("未选择视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.bs_input))
        row1.addWidget(self.bs_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("截图设置")
        gl2 = QVBoxLayout(group2)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("模式:"))
        self.screenshot_mode = QComboBox()
        self.screenshot_mode.addItems(["缩略图墙 (4x4)", "时间间隔截图", "单张截图"])
        row2.addWidget(self.screenshot_mode)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("截图间隔(秒):"))
        self.screenshot_interval = QDoubleSpinBox()
        self.screenshot_interval.setRange(0.5, 60)
        self.screenshot_interval.setValue(10)
        self.screenshot_interval.setSingleStep(5)
        row3.addWidget(self.screenshot_interval)
        row3.addStretch()
        gl2.addLayout(row3)
        
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("缩略图宽度:"))
        self.thumb_width = QSpinBox()
        self.thumb_width.setRange(100, 500)
        self.thumb_width.setValue(160)
        row4.addWidget(self.thumb_width)
        row4.addStretch()
        gl2.addLayout(row4)
        
        info_label = QLabel("💡 缩略图墙模式会生成 4x4 共 16 张预览图；间隔模式每隔 N 秒截一张图")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        layout.addWidget(group2)
        
        btn_run = QPushButton("🖼️ 开始截图")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_batch_screenshot)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_batch_screenshot(self):
        src = self.bs_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        mode = self.screenshot_mode.currentText()
        base_name = src.rsplit('.', 1)[0]
        
        if "缩略图墙" in mode:
            dst = base_name + "_thumbnails.jpg"
            cmd = ["ffmpeg", "-i", src, "-vf", f"fps=1/5,scale={self.thumb_width.value()}:-1,tile=4x4", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
        elif "时间间隔" in mode:
            interval = self.screenshot_interval.value()
            self.log(f"📸 将每隔 {interval} 秒截一张图，输出为 {base_name}_001.jpg 等")
            dst = base_name + "_%03d.jpg"
            cmd = ["ffmpeg", "-i", src, "-vf", f"fps=1/{interval}", dst]
            self.run_ffmpeg(cmd, base_name + "_间隔截图")
        else:
            dst = base_name + "_screenshot.jpg"
            cmd = ["ffmpeg", "-i", src, "-vframes", "1", dst, "-y"]
            self.run_ffmpeg(cmd, dst)

    # ========== 新功能 17: 音频工具 ==========
    def create_audio_tools_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("音频文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.audio_input = QLineEdit()
        self.audio_input.setPlaceholderText("未选择音频/视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.audio_input))
        row1.addWidget(self.audio_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("音频处理功能")
        gl2 = QVBoxLayout(group2)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("处理类型:"))
        self.audio_func = QComboBox()
        self.audio_func.addItems(["格式转换", "音频剪辑", "音频合并", "调整音量", "音频倒放"])
        row2.addWidget(self.audio_func)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("输出格式:"))
        self.audio_format = QComboBox()
        self.audio_format.addItems(["mp3", "aac", "flac", "wav", "ogg"])
        row3.addWidget(self.audio_format)
        row3.addStretch()
        gl2.addLayout(row3)
        
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("开始时间(剪辑):"))
        self.audio_start = QLineEdit()
        self.audio_start.setPlaceholderText("00:00:00")
        row4.addWidget(self.audio_start)
        row4.addWidget(QLabel("时长(剪辑):"))
        self.audio_duration = QLineEdit()
        self.audio_duration.setPlaceholderText("00:00:30")
        row4.addWidget(self.audio_duration)
        row4.addStretch()
        gl2.addLayout(row4)
        
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("音量比例(0-200%):"))
        self.audio_volume = QSlider(Qt.Orientation.Horizontal)
        self.audio_volume.setRange(0, 200)
        self.audio_volume.setValue(100)
        self.audio_vol_label = QLabel("100%")
        self.audio_volume.valueChanged.connect(lambda v: self.audio_vol_label.setText(f"{v}%"))
        row5.addWidget(self.audio_volume)
        row5.addWidget(self.audio_vol_label)
        row5.addStretch()
        gl2.addLayout(row5)
        
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("合并文件列表:"))
        self.audio_merge_list = QListWidget()
        self.audio_merge_list.setMaximumHeight(100)
        row6.addWidget(self.audio_merge_list)
        gl2.addLayout(row6)
        
        btn_merge_add = QPushButton("➕ 添加音频到合并列表")
        btn_merge_add.clicked.connect(self.add_audio_to_merge)
        gl2.addWidget(btn_merge_add)
        
        layout.addWidget(group2)
        
        btn_run = QPushButton("🎵 执行音频处理")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_audio_tool)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def add_audio_to_merge(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择音频文件", "", "音频 (*.mp3 *.wav *.flac *.aac *.m4a)")
        for f in files:
            self.audio_merge_list.addItem(f)
    
    def do_audio_tool(self):
        src = self.audio_input.text()
        func = self.audio_func.currentText()
        dst = src.rsplit('.', 1)[0] + f"_processed.{self.audio_format.currentText()}"
        
        if func == "格式转换":
            if not src:
                self.log("❌ 请选择文件")
                return
            codec = "libmp3lame" if self.audio_format.currentText() == "mp3" else self.audio_format.currentText()
            cmd = ["ffmpeg", "-i", src, "-vn", "-c:a", codec, dst, "-y"]
            self.run_ffmpeg(cmd, dst)
        
        elif func == "音频剪辑":
            if not src:
                self.log("❌ 请选择文件")
                return
            cmd = ["ffmpeg", "-i", src]
            if self.audio_start.text():
                cmd.extend(["-ss", self.audio_start.text()])
            if self.audio_duration.text():
                cmd.extend(["-t", self.audio_duration.text()])
            cmd.extend(["-c", "copy", dst, "-y"])
            self.run_ffmpeg(cmd, dst)
        
        elif func == "音频合并":
            if self.audio_merge_list.count() < 2:
                self.log("❌ 至少需要2个音频文件")
                return
            list_file = "audio_concat.txt"
            with open(list_file, "w", encoding='utf-8') as f:
                for i in range(self.audio_merge_list.count()):
                    path = self.audio_merge_list.item(i).text().replace("'", "'\\''")
                    f.write(f"file '{path}'\n")
            cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
        
        elif func == "调整音量":
            if not src:
                self.log("❌ 请选择文件")
                return
            vol = self.audio_volume.value() / 100.0
            cmd = ["ffmpeg", "-i", src, "-af", f"volume={vol}", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
        
        elif func == "音频倒放":
            if not src:
                self.log("❌ 请选择文件")
                return
            cmd = ["ffmpeg", "-i", src, "-af", "areverse", dst, "-y"]
            self.run_ffmpeg(cmd, dst)

    # ========== 新功能 18: 视频倒放 ==========
    def create_reverse_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.reverse_input = QLineEdit()
        self.reverse_input.setPlaceholderText("未选择视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.reverse_input))
        row1.addWidget(self.reverse_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("倒放设置")
        gl2 = QVBoxLayout(group2)
        
        self.reverse_video = QCheckBox("倒放视频")
        self.reverse_video.setChecked(True)
        gl2.addWidget(self.reverse_video)
        
        self.reverse_audio = QCheckBox("倒放音频")
        self.reverse_audio.setChecked(True)
        gl2.addWidget(self.reverse_audio)
        
        info_label = QLabel("💡 倒放视频+音频会产生有趣的反向播放效果！")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        layout.addWidget(group2)
        
        btn_run = QPushButton("⏪ 开始倒放")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_reverse)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w
    
    def do_reverse(self):
        src = self.reverse_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        dst = src.rsplit('.', 1)[0] + "_reversed.mp4"
        filters = []
        if self.reverse_video.isChecked():
            filters.append("reverse")
        if self.reverse_audio.isChecked():
            filters.append("areverse")
        
        if len(filters) == 0:
            self.log("❌ 请至少选择一项倒放")
            return
        elif len(filters) == 1:
            if "reverse" in filters[0]:
                cmd = ["ffmpeg", "-i", src, "-vf", "reverse", "-c:a", "copy", dst, "-y"]
            else:
                cmd = ["ffmpeg", "-i", src, "-af", "areverse", "-c:v", "copy", dst, "-y"]
        else:
            cmd = ["ffmpeg", "-i", src, "-vf", "reverse", "-af", "areverse", dst, "-y"]
        
        self.run_ffmpeg(cmd, dst)

    # ========== 新功能 19: 视频预览 ==========
    def create_preview_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        # 文件选择
        group = QGroupBox("选择视频文件")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.preview_input = QLineEdit()
        self.preview_input.setPlaceholderText("未选择视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.preview_input))
        row1.addWidget(self.preview_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        # 预览设置
        group2 = QGroupBox("预览设置")
        gl2 = QVBoxLayout(group2)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("起始时间:"))
        self.preview_start = QLineEdit()
        self.preview_start.setPlaceholderText("留空从头播放，例: 00:01:30")
        row2.addWidget(self.preview_start)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        self.preview_autoexit = QCheckBox("播放完后自动关闭窗口")
        self.preview_autoexit.setChecked(True)
        row3.addWidget(self.preview_autoexit)
        row3.addStretch()
        gl2.addLayout(row3)
        
        info_label = QLabel("💡 提示：\n• ffplay 播放器会单独弹窗\n• 按 ESC 键关闭播放窗口\n• 按键盘左右箭头键可以逐帧进退，方便找裁剪点")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        layout.addWidget(group2)
        
        btn_preview = QPushButton("🎬 预览视频")
        btn_preview.setMinimumHeight(40)
        btn_preview.clicked.connect(self.do_preview)
        layout.addWidget(btn_preview)
        layout.addStretch()
        return w

    def do_preview(self):
        src = self.preview_input.text()
        if not src:
            self.log("❌ 请选择视频文件")
            return
        
        # 检查 ffplay 是否可用
        try:
            subprocess.run(["ffplay", "-version"], capture_output=True, check=True)
        except:
            self.log("❌ 未找到 ffplay，请确保 FFmpeg 已正确安装并添加到 PATH")
            QMessageBox.warning(self, "缺少依赖", "未找到 ffplay！\n\n请确保 FFmpeg 已安装并添加到系统 PATH 中。")
            return
        
        # 构建命令
        cmd = ["ffplay"]
        
        # 添加起始时间参数
        if self.preview_start.text().strip():
            cmd.extend(["-ss", self.preview_start.text().strip()])
        
        # 自动关闭参数
        if self.preview_autoexit.isChecked():
            cmd.append("-autoexit")
        
        # 添加输入文件
        cmd.append(src)
        
        self.log(f"▶️ 开始预览: {os.path.basename(src)}")
        if self.preview_start.text().strip():
            self.log(f"   起始时间: {self.preview_start.text().strip()}")
        
        # 非阻塞方式启动 ffplay
        try:
            subprocess.Popen(cmd, shell=False)
            self.log("✅ 预览窗口已打开")
        except Exception as e:
            self.log(f"❌ 启动预览失败: {str(e)}")

    # ========== 新功能 20: 自动字幕 & 字幕处理 ==========
    def create_subtitle_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        # 文件选择
        group = QGroupBox("选择视频/音频文件")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.sub_input = QLineEdit()
        self.sub_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.sub_input, "媒体文件 (*.mp4 *.mkv *.avi *.mov *.mp3 *.wav)"))
        row1.addWidget(self.sub_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        # 功能选择
        group2 = QGroupBox("字幕功能")
        gl2 = QVBoxLayout(group2)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("功能:"))
        self.sub_func = QComboBox()
        self.sub_func.addItems(["🎤 语音识别生成字幕 (Whisper)", "📝 烧录字幕到视频", "📄 提取字幕流", "🔄 字幕格式转换"])
        self.sub_func.currentIndexChanged.connect(self.on_sub_func_changed)
        row2.addWidget(self.sub_func)
        row2.addStretch()
        gl2.addLayout(row2)
        
        # Whisper 模型选择
        self.whisper_model_layout = QHBoxLayout()
        self.whisper_model_layout.addWidget(QLabel("Whisper 模型:"))
        self.whisper_model = QComboBox()
        self.whisper_model.addItems(["tiny (最快, 最低精度)", "base", "small", "medium", "large (最慢, 最高精度)"])
        self.whisper_model.setCurrentIndex(2)
        self.whisper_model_layout.addWidget(self.whisper_model)
        self.whisper_model_layout.addStretch()
        gl2.addLayout(self.whisper_model_layout)
        
        # 烧录字幕参数
        self.burn_layout = QHBoxLayout()
        self.sub_file = QLineEdit()
        self.sub_file.setPlaceholderText("字幕文件路径 (.srt/.ass)")
        btn_sub = QPushButton("📂 选择字幕")
        btn_sub.clicked.connect(lambda: self.select_file(self.sub_file, "字幕 (*.srt *.ass *.ssa)"))
        self.burn_layout.addWidget(QLabel("字幕文件:"))
        self.burn_layout.addWidget(self.sub_file)
        self.burn_layout.addWidget(btn_sub)
        gl2.addLayout(self.burn_layout)
        
        # 字幕语言
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("语言 (Whisper):"))
        self.sub_lang = QComboBox()
        self.sub_lang.addItems(["auto (自动)", "zh (中文)", "en (英文)", "ja (日文)", "ko (韩文)", "fr (法文)", "de (德文)"])
        lang_layout.addWidget(self.sub_lang)
        lang_layout.addStretch()
        gl2.addLayout(lang_layout)
        
        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("字幕格式:"))
        self.sub_format = QComboBox()
        self.sub_format.addItems(["srt", "ass", "vtt"])
        format_layout.addWidget(self.sub_format)
        format_layout.addStretch()
        gl2.addLayout(format_layout)
        
        info_label = QLabel("💡 提示：Whisper 需要安装 openai-whisper (pip install openai-whisper)\n• 首次使用会下载模型（几百MB）\n• 烧录字幕需要先有字幕文件")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        
        layout.addWidget(group2)
        
        # 初始隐藏/显示
        self.on_sub_func_changed(0)
        
        btn_run = QPushButton("🎤 执行字幕处理")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_subtitle)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w

    def on_sub_func_changed(self, idx):
        is_whisper = idx == 0
        is_burn = idx == 1
        self.whisper_model.setVisible(is_whisper)
        self.sub_lang.setVisible(is_whisper)
        self.sub_format.setVisible(not is_burn)
        self.burn_layout.parentWidget().setVisible(is_burn)

    def do_subtitle(self):
        src = self.sub_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        func_idx = self.sub_func.currentIndex()
        base_name = src.rsplit('.', 1)[0]
        
        if func_idx == 0:  # Whisper 语音识别
            self.log("🎤 开始 Whisper 语音识别...")
            self.log("   这可能需要几分钟，请耐心等待...")
            model = self.whisper_model.currentText().split()[0]
            lang = self.sub_lang.currentText().split()[0]
            if lang == "auto":
                lang = ""
            else:
                lang = f"--language {lang}"
            
            dst = base_name + f".{self.sub_format.currentText()}"
            cmd = ["whisper", src, "--model", model, "--output_format", self.sub_format.currentText(), "--output_dir", os.path.dirname(src)]
            if lang:
                cmd.extend(lang.split())
            self.log(f"   命令: whisper {os.path.basename(src)} --model {model}")
            self.run_ffmpeg(cmd, dst)
            
        elif func_idx == 1:  # 烧录字幕
            sub = self.sub_file.text()
            if not sub:
                self.log("❌ 请选择字幕文件")
                return
            dst = base_name + "_hardsub.mp4"
            cmd = ["ffmpeg", "-i", src, "-vf", f"subtitles={sub}", "-c:a", "copy", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
            
        elif func_idx == 2:  # 提取字幕流
            dst = base_name + ".srt"
            cmd = ["ffmpeg", "-i", src, "-map", "0:s:0", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
            
        elif func_idx == 3:  # 字幕格式转换
            sub = self.sub_file.text()
            if not sub:
                self.log("❌ 请选择字幕文件")
                return
            dst = sub.rsplit('.', 1)[0] + f".{self.sub_format.currentText()}"
            cmd = ["ffmpeg", "-i", sub, dst, "-y"]
            self.run_ffmpeg(cmd, dst)

    # ========== 新功能 21: 高级编码 ==========
    def create_codec_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.codec_input = QLineEdit()
        self.codec_input.setPlaceholderText("未选择文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.codec_input))
        row1.addWidget(self.codec_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("编码设置")
        gl2 = QVBoxLayout(group2)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("编码格式:"))
        self.vvc_codec = QComboBox()
        self.vvc_codec.addItems(["H.264 (libx264)", "H.265 (libx265)", "H.266/VVC (libvvc)", "AV1 (libaom-av1)"])
        row2.addWidget(self.vvc_codec)
        row2.addStretch()
        gl2.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("质量/CRF:"))
        self.vvc_crf = QSlider(Qt.Orientation.Horizontal)
        self.vvc_crf.setRange(18, 35)
        self.vvc_crf.setValue(23)
        self.vvc_crf_label = QLabel("23")
        self.vvc_crf.valueChanged.connect(lambda v: self.vvc_crf_label.setText(str(v)))
        row3.addWidget(self.vvc_crf)
        row3.addWidget(self.vvc_crf_label)
        row3.addStretch()
        gl2.addLayout(row3)
        
        row4 = QHBoxLayout()
        self.gpu_accel = QCheckBox("使用 Vulkan/GPU 加速 (需要编译支持)")
        row4.addWidget(self.gpu_accel)
        row4.addStretch()
        gl2.addLayout(row4)
        
        info_label = QLabel("💡 提示：\n• H.266/VVC 需要编译支持 libvvc 的 FFmpeg\n• AV1 编码速度较慢但压缩率高\n• GPU 加速需要特定版本的 FFmpeg")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        
        layout.addWidget(group2)
        
        btn_run = QPushButton("🎬 开始编码")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_advanced_codec)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w

    def do_advanced_codec(self):
        src = self.codec_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        codec_map = {
            "H.264 (libx264)": "libx264",
            "H.265 (libx265)": "libx265",
            "H.266/VVC (libvvc)": "libvvc",
            "AV1 (libaom-av1)": "libaom-av1"
        }
        codec = codec_map[self.vvc_codec.currentText()]
        dst = src.rsplit('.', 1)[0] + f"_{codec}.mp4"
        
        cmd = ["ffmpeg", "-i", src, "-c:v", codec, "-crf", str(self.vvc_crf.value()), "-c:a", "aac"]
        
        if self.gpu_accel.isChecked():
            if codec == "libx264":
                cmd.extend(["-hwaccel", "vulkan", "-hwaccel_output_format", "vulkan"])
            elif codec == "libx265":
                cmd.extend(["-hwaccel", "vulkan", "-hwaccel_output_format", "vulkan"])
        
        cmd.extend([dst, "-y"])
        self.run_ffmpeg(cmd, dst)

    # ========== 新功能 22: 专业音频处理 ==========
    def create_audio_pro_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.ap_input = QLineEdit()
        self.ap_input.setPlaceholderText("未选择音频/视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.ap_input))
        row1.addWidget(self.ap_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("专业音频处理")
        gl2 = QVBoxLayout(group2)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("处理类型:"))
        self.ap_func = QComboBox()
        self.ap_func.addItems(["音频重采样", "多音轨信息", "多音轨提取", "音频均衡器", "5.1 转立体声"])
        self.ap_func.currentIndexChanged.connect(self.on_ap_func_changed)
        row2.addWidget(self.ap_func)
        row2.addStretch()
        gl2.addLayout(row2)
        
        # 重采样参数
        self.resample_layout = QHBoxLayout()
        self.resample_layout.addWidget(QLabel("采样率:"))
        self.sample_rate = QComboBox()
        self.sample_rate.addItems(["44100", "48000", "96000", "192000"])
        self.resample_layout.addWidget(self.sample_rate)
        self.resample_layout.addWidget(QLabel("Hz"))
        self.resample_layout.addStretch()
        gl2.addLayout(self.resample_layout)
        
        # 音轨选择
        self.track_layout = QHBoxLayout()
        self.track_layout.addWidget(QLabel("音轨索引:"))
        self.track_index = QSpinBox()
        self.track_index.setRange(0, 10)
        self.track_index.setValue(0)
        self.track_layout.addWidget(self.track_index)
        self.track_layout.addStretch()
        gl2.addLayout(self.track_layout)
        
        # 均衡器参数
        self.equalizer_layout = QHBoxLayout()
        self.equalizer_layout.addWidget(QLabel("均衡器预设:"))
        self.equalizer_preset = QComboBox()
        self.equalizer_preset.addItems(["无", "低音增强", "高音增强", "人声增强", "摇滚", "古典"])
        self.equalizer_layout.addWidget(self.equalizer_preset)
        self.equalizer_layout.addStretch()
        gl2.addLayout(self.equalizer_layout)
        
        info_label = QLabel("💡 提示：\n• 音频重采样：改变采样率，如 48k→44.1k\n• 多音轨：查看视频中的所有音频流\n• 5.1 转立体声：将环绕声转为双声道")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        
        layout.addWidget(group2)
        
        self.on_ap_func_changed(0)
        
        btn_run = QPushButton("🔊 执行处理")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_audio_pro)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w

    def on_ap_func_changed(self, idx):
        is_resample = idx == 0
        is_track_extract = idx == 2
        is_equalizer = idx == 3
        self.resample_layout.parentWidget().setVisible(is_resample)
        self.track_layout.parentWidget().setVisible(is_track_extract)
        self.equalizer_layout.parentWidget().setVisible(is_equalizer)

    def do_audio_pro(self):
        src = self.ap_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        func = self.ap_func.currentIndex()
        base_name = src.rsplit('.', 1)[0]
        
        if func == 0:  # 重采样
            dst = base_name + f"_resampled.{src.rsplit('.', 1)[1] if '.' in src else 'mp4'}"
            sr = self.sample_rate.currentText()
            cmd = ["ffmpeg", "-i", src, "-af", f"aresample={sr}", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
            
        elif func == 1:  # 多音轨信息
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", src]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    info = []
                    for i, stream in enumerate(data.get('streams', [])):
                        if stream.get('codec_type') == 'audio':
                            info.append(f"音轨 #{i}: {stream.get('codec_name', 'N/A')}, {stream.get('sample_rate', 'N/A')}Hz, {stream.get('channels', 'N/A')}声道")
                    if info:
                        self.log("📀 多音轨信息:")
                        for line in info:
                            self.log(f"   {line}")
                        QMessageBox.information(self, "音轨信息", "\n".join(info))
                    else:
                        self.log("❌ 未检测到音轨")
            except Exception as e:
                self.log(f"❌ 获取失败: {str(e)}")
                
        elif func == 2:  # 提取指定音轨
            dst = base_name + f"_track{self.track_index.value()}.mp3"
            cmd = ["ffmpeg", "-i", src, "-map", f"0:a:{self.track_index.value()}", "-c:a", "mp3", dst, "-y"]
            self.run_ffmpeg(cmd, dst)
            
        elif func == 3:  # 均衡器
            eq_map = {
                "低音增强": "bass=g=10",
                "高音增强": "treble=g=10",
                "人声增强": "aequalizer=100:2:1:1",
                "摇滚": "aequalizer=100:1:1:2,aequalizer=4000:1:1:2",
                "古典": "aequalizer=200:1:1:1.5,aequalizer=3000:1:1:1.5"
            }
            eq = eq_map.get(self.equalizer_preset.currentText(), "")
            if not eq:
                self.log("⏩ 跳过无效效果")
                return
            dst = base_name + "_equalized.mp3"
            cmd = ["ffmpeg", "-i", src, "-af", eq, dst, "-y"]
            self.run_ffmpeg(cmd, dst)
            
        elif func == 4:  # 5.1 转立体声
            dst = base_name + "_stereo.mp3"
            cmd = ["ffmpeg", "-i", src, "-af", "channelmap=channel_layout=stereo", dst, "-y"]
            self.run_ffmpeg(cmd, dst)

    # ========== 新功能 23: 画质增强 ==========
    def create_video_fix_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(15)
        
        group = QGroupBox("文件设置")
        gl = QVBoxLayout(group)
        row1 = QHBoxLayout()
        self.fix_input = QLineEdit()
        self.fix_input.setPlaceholderText("未选择视频文件")
        btn1 = QPushButton("📂 浏览")
        btn1.clicked.connect(lambda: self.select_file(self.fix_input))
        row1.addWidget(self.fix_input)
        row1.addWidget(btn1)
        gl.addLayout(row1)
        layout.addWidget(group)
        
        group2 = QGroupBox("画质增强滤镜")
        gl2 = QVBoxLayout(group2)
        
        self.sharp = QCheckBox("锐化 (unsharp)")
        self.sharp.setToolTip("增强边缘清晰度")
        gl2.addWidget(self.sharp)
        
        self.denoise = QCheckBox("降噪 (hqdn3d)")
        self.denoise.setToolTip("减少画面噪点")
        gl2.addWidget(self.denoise)
        
        self.deblock = QCheckBox("去块 (deblock)")
        self.deblock.setToolTip("去除压缩产生的方块效应")
        gl2.addWidget(self.deblock)
        
        self.hdr2sdr = QCheckBox("HDR 转 SDR")
        self.hdr2sdr.setToolTip("将 HDR 视频转换为普通 SDR")
        gl2.addWidget(self.hdr2sdr)
        
        self.stabilize = QCheckBox("视频稳定化 (deshake)")
        self.stabilize.setToolTip("消除手持拍摄抖动")
        gl2.addWidget(self.stabilize)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("色彩空间:"))
        self.colorspace = QComboBox()
        self.colorspace.addItems(["不转换", "bt709 (SDR 标准)", "bt2020 (HDR 标准)", "bt601 (SD 标准)"])
        row3.addWidget(self.colorspace)
        row3.addStretch()
        gl2.addLayout(row3)
        
        info_label = QLabel("💡 提示：\n• 多个滤镜可以同时使用，但会增加处理时间\n• HDR 转 SDR 需要正确设置色彩映射")
        info_label.setWordWrap(True)
        gl2.addWidget(info_label)
        
        layout.addWidget(group2)
        
        btn_run = QPushButton("✨ 应用画质增强")
        btn_run.setMinimumHeight(40)
        btn_run.clicked.connect(self.do_video_fix)
        layout.addWidget(btn_run)
        layout.addStretch()
        return w

    def do_video_fix(self):
        src = self.fix_input.text()
        if not src:
            self.log("❌ 请选择文件")
            return
        
        filters = []
        if self.sharp.isChecked():
            filters.append("unsharp=5:5:1.0:5:5:0.0")
        if self.denoise.isChecked():
            filters.append("hqdn3d=2.5")
        if self.deblock.isChecked():
            filters.append("deblock")
        if self.stabilize.isChecked():
            filters.append("deshake")
        if self.hdr2sdr.isChecked():
            filters.append("tonemap=hable")
        
        cs_map = {
            "bt709 (SDR 标准)": "bt709",
            "bt2020 (HDR 标准)": "bt2020nc",
            "bt601 (SD 标准)": "bt601"
        }
        if self.colorspace.currentText() != "不转换":
            filters.append(f"colorspace=all={cs_map[self.colorspace.currentText()]}")
        
        if not filters:
            self.log("❌ 请至少选择一项滤镜")
            return
        
        dst = src.rsplit('.', 1)[0] + "_enhanced.mp4"
        filter_str = ",".join(filters)
        cmd = ["ffmpeg", "-i", src, "-vf", filter_str, "-c:a", "copy", dst, "-y"]
        self.run_ffmpeg(cmd, dst)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FFmpegGUI()
    window.show()
    sys.exit(app.exec())    
