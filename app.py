import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os

# ----------------- PAGE SETUP -----------------
st.set_page_config(
    page_title="Library Bulk Barcode Generator",
    layout="centered"
)

st.title("📚 Library Bulk Barcode Generator")

st.markdown(
    "Generate **Code 128 library barcodes** in bulk and export them as "
    "**Avery-style printable PDF label sheets**."
)

# ----------------- USER INPUT -----------------
library_name = st.text_input(
    "Library Name (Top Text)",
    "JNIAS COLLEGE LIBRARY"
)

start_number = st.number_input(
    "Starting Barcode Number",
    min_value=1,
    value=1
)

total_labels = st.number_input(
    "Total Labels to Generate",
    min_value=1,
    max_value=5000,
    value=1000
)

generate_btn = st.button("Generate Barcode PDF")

# ----------------- AVERY 5160 CONFIG -----------------
LABEL_WIDTH = 2.625 * inch
LABEL_HEIGHT = 1 * inch
COLS = 3
ROWS = 10
LEFT_MARGIN = 0.3 * inch
TOP_MARGIN = 0.5 * inch

# ----------------- BARCODE LABEL IMAGE -----------------
def create_label_image(header_text, barcode_value):
    barcode = Code128(
        str(barcode_value),
        writer=ImageWriter()
    )

    tmp_barcode = tempfile.NamedTemporaryFile(delete=False, suffix=".png")

    barcode_path = barcode.save(
        tmp_barcode.name,
        options={
            "write_text": False,
            "module_width": 0.6,     # thick bars (matches sample)
            "module_height": 18.0,   # tall barcode
            "quiet_zone": 2.0
        }
    )

    barcode_img = Image.open(barcode_path)

    label_img = Image.new("RGB", (700, 300), "white")
    draw = ImageDraw.Draw(label_img)

    try:
        font_top = ImageFont.truetype("arial.ttf", 36)
        font_bottom = ImageFont.truetype("arial.ttf", 34)
    except:
        font_top = font_bottom = ImageFont.load_default()

    # Header text
    header_width = draw.textlength(header_text, font=font_top)
    draw.text(
        ((700 - header_width) / 2, 10),
        header_text,
        fill="black",
        font=font_top
    )

    # Barcode (no resize distortion)
    label_img.paste(
        barcode_img,
        ((700 - barcode_img.width) // 2, 70)
    )

    # Bottom number
    value_width = draw.textlength(str(barcode_value), font=font_bottom)
    draw.text(
        ((700 - value_width) / 2, 250),
        str(barcode_value),
        fill="black",
        font=font_bottom
    )

    return label_img

# ----------------- PDF GENERATION -----------------
def generate_pdf(start, count):
    pdf_path = os.path.join(
        tempfile.gettempdir(),
        "library_barcode_labels.pdf"
    )

    c = canvas.Canvas(pdf_path, pagesize=A4)

    x = LEFT_MARGIN
    y = A4[1] - TOP_MARGIN - LABEL_HEIGHT
    label_index = 0

    for i in range(count):
        barcode_number = start + i

        label_img = create_label_image(
            library_name,
            barcode_number
        )

        tmp_label = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        label_img.save(tmp_label.name)

        c.drawImage(
            tmp_label.name,
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

# ----------------- RUN -----------------
if generate_btn:
    with st.spinner("Generating barcode labels..."):
        pdf_file = generate_pdf(start_number, total_labels)

    with open(pdf_file, "rb") as f:
        st.success("Barcode PDF generated successfully")
        st.download_button(
            "Download Barcode Labels (PDF)",
            f,
            file_name="library_barcode_labels.pdf",
            mime="application/pdf"
        )