from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
from main import graph

class WorkerThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            result = graph.invoke({"input": self.file_path})
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qwen-VL-Max 数据分析工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 加载动画标签
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #4CAF50;
                margin: 20px;
            }
        """)
        self.loading_label.setText("加载中...")
        self.loading_label.hide()
        
        # 主部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # 文件选择按钮
        self.btn_select = QPushButton("选择图片文件")
        self.btn_select.clicked.connect(self.select_file)
        self.layout.addWidget(self.btn_select)
        
        # 进度条
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)
        
        # 结果显示区域
        self.result_label = QLabel("结果:")
        self.layout.addWidget(self.result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.jpeg)")
        if file_path:
            self.process_file(file_path)
    
    def process_file(self, file_path):
        self.progress.setValue(0)
        self.result_text.clear()
        self.loading_label.show()
        self.btn_select.setEnabled(False)
        
        # 创建并启动工作线程
        self.worker_thread = WorkerThread(file_path)
        self.worker_thread.finished.connect(self.on_processing_finished)
        self.worker_thread.error.connect(self.on_processing_error)
        self.worker_thread.start()
    
    def on_processing_finished(self, result):
        json_data = result['standardized']
        self.progress.setValue(100)
        self.result_text.setText(json_data)
        self.loading_label.hide()
        self.btn_select.setEnabled(True)
    
    def on_processing_error(self, error_msg):
        self.result_text.setText(f"处理失败: {error_msg}")
        self.progress.setValue(0)
        self.loading_label.hide()
        self.btn_select.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())