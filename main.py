from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image
import io

app = FastAPI()


@app.post("/hide/")
async def hide_image(cover: UploadFile = File(...), secret: UploadFile = File(...)):
    cover_img = Image.open(cover.file).convert("RGB")
    secret_img = Image.open(secret.file).convert("RGB").resize(cover_img.size)

    cover_pixels = cover_img.load()
    secret_pixels = secret_img.load()

    for x in range(cover_img.width):
        for y in range(cover_img.height):
            r1, g1, b1 = cover_pixels[x, y]
            r2, g2, b2 = secret_pixels[x, y]

            r = (r1 & 0b11110000) | (r2 >> 4)
            g = (g1 & 0b11110000) | (g2 >> 4)
            b = (b1 & 0b11110000) | (b2 >> 4)

            cover_pixels[x, y] = (r, g, b)

    buf = io.BytesIO()
    cover_img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.post("/extract/")
async def extract_image(stego: UploadFile = File(...)):
    stego_img = Image.open(stego.file).convert("RGB")
    stego_pixels = stego_img.load()

    extracted = Image.new("RGB", stego_img.size)
    extracted_pixels = extracted.load()

    for x in range(stego_img.width):
        for y in range(stego_img.height):
            r, g, b = stego_pixels[x, y]

            r2 = (r & 0b00001111) << 4
            g2 = (g & 0b00001111) << 4
            b2 = (b & 0b00001111) << 4

            extracted_pixels[x, y] = (r2, g2, b2)

    # ---- Improve quality ----
    # enhancer = ImageEnhance.Brightness(extracted)
    # extracted = enhancer.enhance(1.5)  # brighter

    # enhancer = ImageEnhance.Contrast(extracted)
    # extracted = enhancer.enhance(1.5)  # more contrast

    buf = io.BytesIO()
    extracted.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
