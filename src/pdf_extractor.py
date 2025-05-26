class PDFExtractor:
    def __init__(self, filepath):
        self.filepath = filepath

    def extract_text(self):
        import fitz  # PyMuPDF
        text = ""
        with fitz.open(self.filepath) as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    def extract_images(self):
        import fitz  # PyMuPDF
        images = []
        with fitz.open(self.filepath) as pdf:
            for page in pdf:
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf.extract_image(xref)
                    images.append(base_image["image"])
        return images