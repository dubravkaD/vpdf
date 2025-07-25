import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import io

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lightweight PDF Viewer")

        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill="both", expand=True)

        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side="top", fill="x")

        self.btn_open = tk.Button(self.toolbar, text="Open PDF", command=self.open_pdf)
        self.btn_open.pack(side="left")

        self.btn_prev = tk.Button(self.toolbar, text="← Prev", command=self.prev_page, state="disabled")
        self.btn_prev.pack(side="left")

        self.btn_next = tk.Button(self.toolbar, text="Next →", command=self.next_page, state="disabled")
        self.btn_next.pack(side="left")

        self.page_label = tk.Label(self.toolbar, text="Page: 0 / 0")
        self.page_label.pack(side="left")

        self.doc = None
        self.page_num = 0
        self.photo = None

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.show_page()
            self.btn_prev.config(state="normal")
            self.btn_next.config(state="normal")

    def show_page(self):
        if self.doc is None:
            return

        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # scale up for quality
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        self.photo = ImageTk.PhotoImage(image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.page_label.config(text=f"Page: {self.page_num + 1} / {len(self.doc)}")

    def prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def next_page(self):
        if self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

if __name__ == "__main__":
    root = tk.Tk()
    viewer = PDFViewer(root)
    root.mainloop()