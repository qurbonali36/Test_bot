from PIL import Image, ImageDraw, ImageFont
import os

img_path = 'Telegram Test Achievement Certificate.png'
out_path = 'cert_masked.png'

img = Image.open(img_path)
draw = ImageDraw.Draw(img)
W, H = img.size

# Function to fill a box with the average color of its top/bottom borders
def get_bg_color(img, box):
    x1, y1, x2, y2 = box
    colors = []
    # Sample top edge
    for x in range(x1, x2, 5):
        colors.append(img.getpixel((x, y1-5)))
    # Sample bottom edge
    for x in range(x1, x2, 5):
        colors.append(img.getpixel((x, y2+5)))
    
    r = sum(c[0] for c in colors) // len(colors)
    g = sum(c[1] for c in colors) // len(colors)
    b = sum(c[2] for c in colors) // len(colors)
    return (r, g, b)

# Recipient Name box
r_box = [200, 420, 1300, 620]
draw.rectangle(r_box, fill=get_bg_color(img, r_box))

# Course Name box (whole line)
c_box = [250, 680, 1250, 770]
draw.rectangle(c_box, fill=get_bg_color(img, c_box))

# Score Box (gold color approximation)
s_box = [1385, 525, 1590, 640]
# For gold, sample from a specific pixel inside the medal but outside text
gold_color = img.getpixel((1380, 580))
draw.rectangle(s_box, fill=gold_color)

# Date Box
d_box = [385, 1065, 640, 1115]
draw.rectangle(d_box, fill=get_bg_color(img, d_box))

# ID Box
i_box = [1075, 1065, 1330, 1115]
draw.rectangle(i_box, fill=get_bg_color(img, i_box))

# QR Box + text below
qr_box = [1355, 825, 1572, 1090]
draw.rectangle(qr_box, fill=get_bg_color(img, qr_box))

img.save(out_path)
print("Saved masked to", out_path)
