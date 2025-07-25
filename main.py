import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image
import io

class PDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer - PyQt5")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel("Open a PDF file to start...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")

        self.btn_open = QPushButton("Open PDF")
        self.btn_prev = QPushButton("← Prev")
        self.btn_next = QPushButton("Next →")
        self.page_label = QLabel("Page 0 / 0")

        self.btn_prev.setEnabled(False)
        self.btn_next.setEnabled(False)

        # Zoom
        self.btn_zoom_in = QPushButton("Zoom +")
        self.btn_zoom_out = QPushButton("Zoom -")
        self.zoom_level = 2.0  # Default scale factor

        # Add to button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.page_label)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addWidget(self.btn_zoom_out)
        btn_layout.addWidget(self.btn_zoom_in)

        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.image_label)

        self.setLayout(main_layout)

        # Events
        self.btn_open.clicked.connect(self.open_pdf)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)

        # PDF State
        self.doc = None
        self.page_num = 0

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.show_page()
            self.btn_prev.setEnabled(True)
            self.btn_next.setEnabled(True)

    def show_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        qt_image = self.pil2pixmap(image)
        self.image_label.setPixmap(qt_image)
        self.page_label.setText(f"Page {self.page_num + 1} / {len(self.doc)}")

    def prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def next_page(self):
        if self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def pil2pixmap(self, img):
        img = img.convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def zoom_in(self):
        self.zoom_level += 0.5
        self.show_page()

    def zoom_out(self):
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.5
            self.show_page()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())