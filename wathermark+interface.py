import sys
import cv2
import uuid
import os
import numpy as np
import pywt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout,
    QHBoxLayout, QLineEdit, QComboBox, QColorDialog, QStackedWidget, QSlider, QMessageBox
)
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtCore import Qt

# -------- TEXT BINARY UTILS --------
def text_to_binary(text):
    return ''.join([format(ord(c), '08b') for c in text])

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(c, 2)) for c in chars if int(c, 2) != 0])

# -------- LSB WATERMARKING --------
def encode_message_lsb(image_path, message, output_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found.")
    binary_message = text_to_binary(message) + '1111111111111110'
    data_index = 0
    binary_len = len(binary_message)
    for row in image:
        for pixel in row:
            for i in range(3):
                if data_index < binary_len:
                    pixel[i] = (pixel[i] & ~1) | int(binary_message[data_index])
                    data_index += 1
    if data_index < binary_len:
        raise ValueError("Message too long for image.")
    cv2.imwrite(output_path, image)

def decode_message_lsb(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found.")
    binary_data = ""
    for row in image:
        for pixel in row:
            for i in range(3):
                binary_data += str(pixel[i] & 1)
    end_marker = '1111111111111110'
    end_index = binary_data.find(end_marker)
    if end_index != -1:
        binary_data = binary_data[:end_index]
    return binary_to_text(binary_data)

# -------- DCT WATERMARKING --------
def dct2(block):
    return cv2.dct(np.float32(block))

def idct2(block):
    return cv2.idct(np.float32(block))

def embed_dct_watermark(image_path, message, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image non trouvée")
    msg_bin = text_to_binary(message) + '1111111111111110'
    h, w = img.shape
    watermarked = np.copy(img)
    data_index = 0
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            if data_index >= len(msg_bin):
                break
            block = img[i:i+8, j:j+8]
            if block.shape != (8, 8):
                continue
            dct_block = dct2(block)
            bit = int(msg_bin[data_index])
            coeff = int(dct_block[4, 4])
            coeff = (coeff & ~1) | bit
            dct_block[4, 4] = float(coeff)
            watermarked[i:i+8, j:j+8] = idct2(dct_block)
            data_index += 1
    cv2.imwrite(output_path, watermarked)

def extract_dct_watermark(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image non trouvée")
    h, w = img.shape
    binary_msg = ""
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = img[i:i+8, j:j+8]
            if block.shape != (8, 8):
                continue
            dct_block = dct2(block)
            bit = int(dct_block[4, 4]) & 1
            binary_msg += str(bit)
            if binary_msg.endswith('1111111111111110'):
                binary_msg = binary_msg[:-16]
                return binary_to_text(binary_msg)
    return binary_to_text(binary_msg)

# -------- DWT WATERMARKING --------
def embed_dwt_watermark(image_path, message, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image non trouvée.")
    coeffs = pywt.dwt2(img, 'haar')
    LL, (LH, HL, HH) = coeffs
    msg_bin = text_to_binary(message) + '1111111111111110'
    data_index = 0
    LL_flat = LL.flatten()
    for i in range(len(LL_flat)):
        if data_index >= len(msg_bin):
            break
        LL_flat[i] = (int(LL_flat[i]) & ~1) | int(msg_bin[data_index])
        data_index += 1
    if data_index < len(msg_bin):
        raise ValueError("Message trop long pour l’image DWT.")
    LL_mod = LL_flat.reshape(LL.shape)
    coeffs_modified = (LL_mod, (LH, HL, HH))
    img_reconstructed = pywt.idwt2(coeffs_modified, 'haar')
    img_reconstructed = np.uint8(np.clip(img_reconstructed, 0, 255))
    cv2.imwrite(output_path, img_reconstructed)

def extract_dwt_watermark(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image non trouvée.")
    LL, _ = pywt.dwt2(img, 'haar')
    LL_flat = LL.flatten()
    binary_msg = ""
    for val in LL_flat:
        bit = int(val) & 1
        binary_msg += str(bit)
        if binary_msg.endswith('1111111111111110'):
            binary_msg = binary_msg[:-16]
            return binary_to_text(binary_msg)
    return binary_to_text(binary_msg)

# -------- VISIBLE WATERMARK --------
def apply_text_watermark(image_path, output_path, text, position, font_scale, color, thickness, full_surface=False):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found.")

    font = cv2.FONT_HERSHEY_SIMPLEX

    if full_surface:
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        for y in range(0, image.shape[0], text_size[1] + 20):
            for x in range(0, image.shape[1], text_size[0] + 40):
                cv2.putText(image, text, (x, y + text_size[1]), font, font_scale, color, thickness, cv2.LINE_AA)
    else:
        cv2.putText(image, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

    cv2.imwrite(output_path, image)

# -------- PYQT5 GUI --------
class WatermarkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watermark Tool")
        self.stacked = QStackedWidget()

        self.init_main_menu()
        self.init_visible_interface()
        self.init_result_interface()
        self.init_invisible_interface()
        self.init_decode_interface()
        self.init_result_interface_inv()


        layout = QVBoxLayout()
        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def init_main_menu(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.make_nav_button("Visible Watermark", 1))
        layout.addWidget(self.make_nav_button("Invisible Watermark", 3))
        layout.addWidget(self.make_nav_button("Decode Hidden Message", 4))
        page.setLayout(layout)
        self.stacked.addWidget(page)

    def init_invisible_interface(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.invis_image_path = ''
        self.invis_text = QLineEdit()
        self.invis_image_path_label = QLabel("No image selected")

        self.method_combo = QComboBox()
        self.method_combo.addItems(["LSB", "DCT", "DWT"])
        layout.addWidget(QLabel("Message to Hide:"))
        layout.addWidget(self.invis_text)
        layout.addWidget(QLabel("Method:"))
        layout.addWidget(self.method_combo)

        layout.addWidget(self.make_button("Select Image", self.load_invis_image))
        layout.addWidget(self.invis_image_path_label)

        layout.addWidget(self.make_button("Hide Message", self.apply_invisible))
        layout.addWidget(self.make_nav_button("← Back", 0))
        page.setLayout(layout)
        self.stacked.addWidget(page)

    def init_decode_interface(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.decode_path = ''
        self.decode_result = QLabel("Hidden message will appear here:")
        self.method_combo_decode = QComboBox()
        self.method_combo_decode.addItems(["LSB", "DCT", "DWT"])
        layout.addWidget(QLabel("Method:"))
        layout.addWidget(self.method_combo_decode)
       
        self.decode_image_path_label = QLabel("No image selected")
        layout.addWidget(self.make_button("Select Image", self.load_decode_image))
        layout.addWidget(self.decode_image_path_label)
        layout.addWidget(self.make_button("Decode Message", self.decode_hidden_message))
        layout.addWidget(self.decode_result)
        layout.addWidget(self.make_nav_button("← Menu", 0))
        page.setLayout(layout)
        self.stacked.addWidget(page)

    def init_visible_interface(self):
        page = QWidget()
        layout = QVBoxLayout()

        self.vis_image_path = ''
        self.vis_text = QLineEdit()
        self.position_combo = QComboBox()
        self.position_combo.addItems(["High Left", "High Right", "Low Left", "Low Right", "Center", "Full Surface"])

        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.color_display = QLabel("Selected Color")
        self.color_display.setStyleSheet("background-color: white; border: 1px solid black;")
        self.color = (255, 255, 255)

        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(50)
        self.transparency_label = QLabel("Transparency: 50%")
        self.transparency_slider.valueChanged.connect(self.update_transparency_label)

        self.font_size = QLineEdit("2")
        self.thickness = QLineEdit("2")

        self.image_path_label = QLabel("No image selected")

        layout.addWidget(QLabel("Watermark Text:"))
        layout.addWidget(self.vis_text)
        layout.addWidget(QLabel("Position:"))
        layout.addWidget(self.position_combo)
        layout.addWidget(self.color_btn)
        layout.addWidget(self.color_display)
        layout.addWidget(self.transparency_label)
        layout.addWidget(self.transparency_slider)
        layout.addWidget(QLabel("Font Scale:"))
        layout.addWidget(self.font_size)
        layout.addWidget(QLabel("Thickness:"))
        layout.addWidget(self.thickness)
        layout.addWidget(self.make_button("Select Image", self.load_vis_image))
        layout.addWidget(self.image_path_label)
        layout.addWidget(self.make_button("Apply Watermark", self.apply_visible))
        layout.addWidget(self.make_nav_button("← Back", 0))
        page.setLayout(layout)
        self.stacked.addWidget(page)

    def init_result_interface(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.result_label = QLabel("Preview done. Save or go back.")
        self.original_image = QLabel()
        self.modified_image = QLabel()

        layout.addWidget(self.result_label)
        layout.addWidget(QLabel("Original Image:"))
        layout.addWidget(self.original_image)
        layout.addWidget(QLabel("Modified Image:"))
        layout.addWidget(self.modified_image)
        layout.addWidget(self.make_button("Save Image", self.save_image))
        layout.addWidget(self.make_nav_button("← Back", 1))
        layout.addWidget(self.make_nav_button("← Menu", 0))
        page.setLayout(layout)
        self.stacked.addWidget(page)
    def init_result_interface_inv(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.result_label = QLabel("Preview done. Save or go back.")
        self.original_image = QLabel()
        self.modified_image = QLabel()

        layout.addWidget(self.result_label)
        layout.addWidget(QLabel("Original Image:"))
        layout.addWidget(self.original_image)
        layout.addWidget(QLabel("Modified Image:"))
        layout.addWidget(self.modified_image)
        layout.addWidget(self.make_button("Save Image", self.save_image))
        layout.addWidget(self.make_nav_button("← Back", 3))
        layout.addWidget(self.make_nav_button("← Menu", 0))
        page.setLayout(layout)
        self.stacked.addWidget(page)
    def make_nav_button(self, label, index):
        btn = QPushButton(label)
        btn.clicked.connect(lambda: self.stacked.setCurrentIndex(index))
        return btn

    def make_button(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        return btn

    def load_invis_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image to Hide Message In")
        if path:
            self.invis_image_path = path
            self.invis_image_path_label.setText(f"Image: {os.path.basename(path)}")


    def apply_invisible(self):
        if not self.invis_image_path:
            QMessageBox.warning(self, "Error", "No image selected.")
            return
        method = self.method_combo.currentText()
        msg = self.invis_text.text()
        try:
            if method == "LSB":
                output = f"invisible_LSB_output_{uuid.uuid4().hex}.png"
                encode_message_lsb(self.invis_image_path, msg, output)

            elif method == "DCT":
                output = f"invisible_DCT_output_{uuid.uuid4().hex}.png"
                embed_dct_watermark(self.invis_image_path, msg, output)

            elif method == "DWT":
                output = f"invisible_DWT_output_{uuid.uuid4().hex}.png"
                embed_dwt_watermark(self.invis_image_path, msg, output)
            self.output_path = output
            self.vis_image_path = self.invis_image_path
            QMessageBox.information(self, "Done", f"Message hidden using {method} in: {output}")
            self.show_images()
            self.stacked.setCurrentIndex(5)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_decode_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if path:
            self.decode_path = path
            self.decode_image_path_label.setText(f"Image: {os.path.basename(path)}")


    def decode_hidden_message(self):
        if not self.decode_path:
            QMessageBox.warning(self, "Error", "No image selected.")
            return
        method = self.method_combo_decode.currentText()
        try:
            if method == "LSB":
                message = decode_message_lsb(self.decode_path)
            elif method == "DCT":
                message = extract_dct_watermark(self.decode_path)
            elif method == "DWT":
                message = extract_dwt_watermark(self.decode_path)
            self.decode_result.setText(f"Hidden Message: {message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = (color.red(), color.green(), color.blue())
            self.color_display.setStyleSheet(f"background-color: {color.name()};")

    def update_transparency_label(self):
        value = self.transparency_slider.value()
        self.transparency_label.setText(f"Transparency: {value}%")

    def load_vis_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if path:
            self.vis_image_path = path
            self.image_path_label.setText(f"Image: {os.path.basename(path)}")

    def apply_visible(self):
        if not self.vis_image_path:
            QMessageBox.warning(self, "Error", "No image selected.")
            return

        image = cv2.imread(self.vis_image_path)
        if image is None:
            return

        h, w = image.shape[:2]
        font_scale = float(self.font_size.text())
        thickness = int(self.thickness.text())
        text = self.vis_text.text()
        size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        pos_map = {
            "High Left": (10, size[1] + 10),
            "High Right": (w - size[0] - 10, size[1] + 10),
            "Low Left": (10, h - 10),
            "Low Right": (w - size[0] - 10, h - 10),
            "Center": ((w - size[0]) // 2, (h + size[1]) // 2),
            "Full Surface": (0, 0)
        }
        pos = pos_map[self.position_combo.currentText()]
        transparency = self.transparency_slider.value()
        color = tuple([int(c * (100 - transparency) / 100) for c in self.color])
        output = f"visible_output_{uuid.uuid4().hex}.jpg"

        apply_text_watermark(self.vis_image_path, output, text, pos, font_scale, color, thickness, self.position_combo.currentText() == "Full Surface")
        self.output_path = output
        self.show_images()
        self.stacked.setCurrentIndex(2)
    def show_images(self):
        def convert(img_path):
            img = cv2.imread(img_path)
            if img is None:
                return QPixmap()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img.shape
            bytes_per_line = ch * w
            return QPixmap.fromImage(QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).scaledToWidth(300))

        self.original_image.setPixmap(convert(self.vis_image_path))
        self.modified_image.setPixmap(convert(self.output_path))

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Image")
        if path:
            image = cv2.imread(self.output_path)
            if image is not None:
                if not os.path.splitext(path)[1]:
                    path += ".png"
                cv2.imwrite(path, image)
                QMessageBox.information(self, "Saved", f"Image saved successfully: {path}")

# -------- MAIN LAUNCH --------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.resize(400, 600)
    window.show()
    sys.exit(app.exec_())
