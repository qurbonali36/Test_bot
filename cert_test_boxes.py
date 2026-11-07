from PIL import Image, ImageDraw, ImageFont
import os

img_path = 'Telegram Test Achievement Certificate.png'
out_path = 'cert_boxes.png'

img = Image.open(img_path)
draw = ImageDraw.Draw(img)
W, H = img.size

# Recipient Name box
draw.rectangle([250, 430, 1200, 600], outline='green', width=3)

# Course Name box (Outstanding Performance in [Test/Course Name])
draw.rectangle([250, 680, 1200, 780], outline='green', width=3)

# Score Box
draw.rectangle([1380, 520, 1550, 640], outline='green', width=3)

# Date Box
draw.rectangle([390, 1070, 630, 1110], outline='green', width=3)

# ID Box
draw.rectangle([1080, 1070, 1310, 1110], outline='green', width=3)

# QR Box
# X from ~1360 to ~1570
# Y from ~830 to ~1040
qr_box = [1355, 825, 1572, 1042]
draw.rectangle(qr_box, outline='green', width=3)

img.save(out_path)
print("Saved boxes to", out_path)
