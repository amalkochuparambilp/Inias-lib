import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os

st.set_page_config(
    page_title="Library Barcode Generator",
    layout="centered"
)

st.title("Library Barcode Generator")

library_name = st.text_input(
    "Library Name",
    "JNIAS COLLEGE LIBRARY"
)

start_number = st.number_input(
    "Starting Barcode Number",
    min_value=1,
    value=1
)

count = st.number_input(
    "Total Labels to Generate",
    min_value=1,
    max_value=5000,
    value=1000
)

generate = st.button("Generate Avery PDF")

LABEL_WIDTH = 3.625 * inch
LABEL_HEIGHT = 1 * inch
COLS = 3
ROWS = 10
LEFT_MARGIN = 0.3 * inch
TOP_MARGIN = 0.5 * inch


def create_label_image(header, value):
    barcode = Code128(str(value), writer=ImageWriter())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    barcode_path = barcode.save(tmp.name, options={"write_text": False})

    barcode_img = Image.open(barcode_path)

    canvas_img = Image.new("RGB", (600, 250), "white")
    draw = ImageDraw.Draw(canvas_img)

    try:
        font_top = ImageFont.truetype("arial.ttf", 34)
        font_bottom = ImageFont.truetype("arial.ttf", 30)
    except:
        font_top = font_bottom = ImageFont.load_default()

    tw = draw.textlength(header, font=font_top)
    draw.text(((600 - tw) / 2, 10), header, fill="black", font=font_top)

    barcode_img = barcode_img.resize((520, 120))
    canvas_img.paste(barcode_img, (40, 70))

    bw = draw.textlength(str(value), font=font_bottom)
    draw.text(((600 - bw) / 2, 200), str(value), fill="black", font=font_bottom)

    return canvas_img


def generate_pdf(start, total):
    pdf_path = os.path.join(
        tempfile.gettempdir(),
        "library_barcodes.pdf"
    )

    c = canvas.Canvas(pdf_path, pagesize=A4)

    x = LEFT_MARGIN
    y = A4[1] - TOP_MARGIN - LABEL_HEIGHT
    label_index = 0

    for i in range(total):
        number = start + i
        label_img = create_label_image(library_name, number)

        tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        label_img.save(tmp_img.name)

        c.drawImage(
            tmp_img.name,
            x,
            y,
            width=LABEL_WIDTH,
            height=LABEL_HEIGHT
        )

        label_index += 1
        x += LABEL_WIDTH

        if label_index % COLS == 0:
            x = LEFT_MARGIN
            y -= LABEL_HEIGHT

        if label_index % (COLS * ROWS) == 0:
            c.showPage()
            x = LEFT_MARGIN
            y = A4[1] - TOP_MARGIN - LABEL_HEIGHT

    c.save()
    return pdf_path


if generate:
    with st.spinner("Generating barcode labels..."):
        pdf = generate_pdf(start_number, count)

    with open(pdf, "rb") as f:
        st.success("PDF generated successfully")
        st.download_button(
            "Download Barcode Labels (PDF)",
            f,
            file_name="library_barcode_labels.pdf",
            mime="application/pdf"
)
