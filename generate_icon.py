"""Generate app.ico with a book symbol on a brand-colored background."""

from PIL import Image, ImageDraw, ImageFont

SIZE = 256
BG_COLOR = (44, 62, 80)      # dark blue-grey
BOOK_COLOR = (236, 240, 241)  # light grey-white
SPINE_COLOR = (189, 195, 199) # slightly darker


def draw_book_icon(size):
    img = Image.new("RGBA", (size, size), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    margin = size * 0.18
    cx = size / 2

    # Left page
    left = margin
    right = cx - size * 0.02
    top = margin
    bottom = size - margin
    draw.rounded_rectangle([left, top, right, bottom], radius=size * 0.03, fill=BOOK_COLOR)

    # Right page
    left2 = cx + size * 0.02
    right2 = size - margin
    draw.rounded_rectangle([left2, top, right2, bottom], radius=size * 0.03, fill=BOOK_COLOR)

    # Spine line
    spine_w = max(2, size * 0.02)
    draw.rectangle([cx - spine_w / 2, top, cx + spine_w / 2, bottom], fill=SPINE_COLOR)

    # Text lines on left page
    line_color = (149, 165, 176)
    lx1 = margin + size * 0.06
    lx2 = cx - size * 0.06
    line_h = size * 0.015
    for i in range(5):
        ly = top + size * 0.12 + i * size * 0.09
        draw.rounded_rectangle([lx1, ly, lx2, ly + line_h], radius=line_h / 2, fill=line_color)

    # Text lines on right page
    rx1 = cx + size * 0.06
    rx2 = size - margin - size * 0.06
    for i in range(5):
        ry = top + size * 0.12 + i * size * 0.09
        draw.rounded_rectangle([rx1, ry, rx2, ry + line_h], radius=line_h / 2, fill=line_color)

    return img


if __name__ == "__main__":
    base = draw_book_icon(256)
    sizes = [16, 32, 48, 64, 128, 256]
    frames = [base.resize((s, s), Image.LANCZOS) for s in sizes]
    frames[0].save("app.ico", format="ICO", sizes=[(s, s) for s in sizes], append_images=frames[1:])
    print("Created app.ico")
