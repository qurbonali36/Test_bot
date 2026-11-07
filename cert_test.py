from PIL import Image, ImageDraw, ImageFont
import os

img_path = 'Telegram Test Achievement Certificate.png'
out_path = 'cert_markup.png'

img = Image.open(img_path)
draw = ImageDraw.Draw(img)
W, H = img.size

# Try to draw some test shapes and text
def draw_marker(draw, x, y, label):
    draw.ellipse((x-10, y-10, x+10, y+10), fill='red')
    draw.text((x+15, y-10), label, fill='red', font=ImageFont.load_default(size=40))

draw_marker(draw, W//2, H//2, "Center")
draw_marker(draw, W//2, H//2 - 100, "Recipient Y")
draw_marker(draw, W//2, H//2 + 100, "Course Y")

# Score area
draw_marker(draw, int(W * 0.84), int(H * 0.48), "Score Center")

# QR Code area
draw_marker(draw, int(W * 0.84), int(H * 0.75), "QR Center")

# Date area
draw_marker(draw, int(W * 0.33), int(H * 0.88), "Date")

# ID area
draw_marker(draw, int(W * 0.65), int(H * 0.88), "ID")

img.save(out_path)
print("Saved markup to", out_path)
