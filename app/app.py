from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from io import BytesIO
from pdf2image import convert_from_path
import os
import sys

app = Flask(__name__)

try:
    with open('secret.key', 'r') as f:
        app.secret_key = f.read().strip()
except FileNotFoundError:
    print("❌ secret.key not found. Please mount it as a volume.")
    sys.exit(1)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'watermarked'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def create_watermark(text, page_index=0):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 11)
    width, height = A4

    step_y = 180
    long_text = (text + " · ") * 40
    y_offset = -100 + (page_index * (step_y // 2))

    for y in range(y_offset, int(height) + step_y * 2, step_y):
        can.saveState()
        can.translate(-100, y)
        can.rotate(25)
        can.setFillColor(Color(0.25, 0.25, 0.25, alpha=0.4))
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
        c = canvas.Canvas(page_buf, pagesize=A4)
        c.drawImage(ImageReader(img_buffer), 0, 0, *A4)
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

    for i, page in enumerate(reader.pages):
        watermark = create_watermark(watermark_text, page_index=i).pages[0]
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
        merged_input_path = os.path.join(UPLOAD_FOLDER, "merged_input.pdf")
        output_name = f"{pdfs[0].filename.rsplit('.', 1)[0]}_filigrane.pdf" if len(pdfs) == 1 else "grouped_filigrane.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        merger = PdfWriter()
        for pdf in pdfs:
            filename = os.path.join(UPLOAD_FOLDER, pdf.filename)
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
