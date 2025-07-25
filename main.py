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
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QSizePolicy
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

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

        self.page_input = QSpinBox()
        self.page_input.setMinimum(1)
        self.page_input.setMaximum(1)
        self.page_input.setFixedWidth(70)

        self.btn_go = QPushButton("Go")

        # Zoom
        self.btn_zoom_in = QPushButton("Zoom +")
        self.btn_zoom_out = QPushButton("Zoom -")
        self.zoom_level = 2.0  # Default scale factor

        self.splitter = QSplitter()

        # Thumbnails list on the left
        self.thumb_list = QListWidget()
        self.thumb_list.setMaximumWidth(150)
        self.thumb_list.setSpacing(5)
        self.thumb_list.setResizeMode(QListWidget.Adjust)
        self.thumb_list.setViewMode(QListWidget.IconMode)
        self.thumb_list.setIconSize(QSize(120, 160))
        self.thumb_list.setMovement(QListWidget.Static)
        self.thumb_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.thumb_list.itemClicked.connect(self.thumb_clicked)

        # Container widget for the right side (buttons + image)
        self.right_container = QWidget()
        right_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.page_label)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addWidget(self.page_input)
        btn_layout.addWidget(self.btn_go)
        btn_layout.addWidget(self.btn_zoom_out)
        btn_layout.addWidget(self.btn_zoom_in)

        right_layout.addLayout(btn_layout)
        right_layout.addWidget(self.image_label)

        self.right_container.setLayout(right_layout)

        # Add to splitter
        self.splitter.addWidget(self.thumb_list)
        self.splitter.addWidget(self.right_container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)
        # main_layout.addWidget(self.image_label)

        self.setLayout(main_layout)

        # Events
        self.btn_open.clicked.connect(self.open_pdf)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_go.clicked.connect(self.go_to_page)

        # PDF State
        self.doc = None
        self.page_num = 0

        # Drag & Drop
        self.setAcceptDrops(True)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        # if file_path:
        #     self.doc = fitz.open(file_path)
        #     self.page_num = 0
        #     self.show_page()
        #     self.btn_prev.setEnabled(True)
        #     self.btn_next.setEnabled(True)

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
        self.page_input.setValue(self.page_num + 1)
        self.thumb_list.setCurrentRow(self.page_num)

    def load_pdf(self, file_path):
        try:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.page_input.setMaximum(len(self.doc))
            self.page_input.setValue(1)
            self.show_page()
            self.btn_prev.setEnabled(True)
            self.btn_next.setEnabled(True)
            self.load_thumbnails()
        except Exception as e:
            print("Failed to load PDF:", e)

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(".pdf"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(".pdf"):
                self.load_pdf(file_path)

    def go_to_page(self):
        page_index = self.page_input.value() - 1
        if self.doc and 0 <= page_index < len(self.doc):
            self.page_num = page_index
            self.show_page()

    def load_thumbnails(self):
        self.thumb_list.clear()
        if not self.doc:
            return

        for i in range(len(self.doc)):
            page = self.doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))  # Small scale
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            qt_pixmap = self.pil2pixmap(image)

            item = QListWidgetItem()
            # item.setIcon(qt_pixmap)
            item.setIcon(QIcon(qt_pixmap))
            item.setData(Qt.UserRole, i)  # Store page index
            item.setToolTip(f"Page {i + 1}")
            self.thumb_list.addItem(item)

    def thumb_clicked(self, item):
        page_index = item.data(Qt.UserRole)
        if page_index is not None:
            self.page_num = page_index
            self.show_page()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    # sys.exit(app.exec_())
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("Application closed by user.")