from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from io import BytesIO
from pdf2image import convert_from_path
from math import sin, cos, radians
import os
import uuid


app = Flask(__name__)


try:
    with open('.secret.key', 'r') as f:
        app.secret_key = f.read().strip()
except FileNotFoundError:
    print(".secret.key not found. Please mount it at /app/.secret.key")
    exit(1)


UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'watermarked'


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def create_portrait_watermark(text, width, height):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica", 11)

    step_y = 140
    long_text = (text + " · ") * 120
    x_shift = -500
    y_offset = -400

    for y in range(int(y_offset), int(height) + 800, step_y):
        can.saveState()
        can.translate(x_shift, y)
        can.rotate(25)
        can.setFillColor(Color(0.3, 0.3, 0.3, alpha=0.4))
        can.drawString(0, 0, long_text)
        can.restoreState()

    can.save()
    packet.seek(0)
    return PdfReader(packet)


def create_landscape_watermark(text, width, height):
    angle_deg = 25
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    font_size = 15
    can.setFont("Helvetica", font_size)
    can.setFillColor(Color(0.3, 0.3, 0.3, alpha=0.4))

    step_y = int(height * 0.14)
    long_text = (text + " · ") * 80
    x_shift = -int(width * 0.6)
    y_offset = -int(height * 1.5)

    for y in range(y_offset, int(height * 2), step_y):
        can.saveState()
        can.translate(x_shift, y)
        can.rotate(angle_deg)
        can.drawString(0, 0, long_text)
        can.restoreState()

    can.save()
    packet.seek(0)
    return PdfReader(packet)


def flatten_pdf(input_pdf_path, output_pdf_path):
    images = convert_from_path(input_pdf_path, dpi=200)
    writer = PdfWriter()

    for img in images:
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        page_buf = BytesIO()
        c = canvas.Canvas(page_buf, pagesize=img.size)
        c.drawImage(ImageReader(img_buffer), 0, 0, width=img.size[0], height=img.size[1])
        c.showPage()
        c.save()
        page_buf.seek(0)

        reader = PdfReader(page_buf)
        writer.add_page(reader.pages[0])

    with open(output_pdf_path, "wb") as f:
        writer.write(f)


def apply_watermark(input_path, output_path, watermark_text):
    temp_output = output_path.replace(".pdf", "_temp.pdf")
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        if width > height:
            watermark = create_landscape_watermark(watermark_text, width, height).pages[0]
        else:
            watermark = create_portrait_watermark(watermark_text, width, height).pages[0]

        page.merge_page(watermark)
        writer.add_page(page)

    with open(temp_output, "wb") as f:
        writer.write(f)

    flatten_pdf(temp_output, output_path)
    os.remove(temp_output)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdfs = request.files.getlist('pdfs')
        watermark_text = request.form['text']
        unique_id = uuid.uuid4().hex

        merged_input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_merged.pdf")
        output_name = f"{unique_id}_filigrane.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        merger = PdfWriter()
        for pdf in pdfs:
            filename = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{pdf.filename}")
            pdf.save(filename)
            reader = PdfReader(filename)
            for page in reader.pages:
                merger.add_page(page)
        with open(merged_input_path, "wb") as f:
            merger.write(f)

        apply_watermark(merged_input_path, output_path, watermark_text)
        session['watermarked_file'] = output_name
        return redirect(url_for('result'))

    return render_template('index.html', watermarked_file=None)

@app.route('/result')
def result():
    watermarked_file = session.pop('watermarked_file', None)
    return render_template('index.html', watermarked_file=watermarked_file)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/preview/<filename>')
def preview_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
