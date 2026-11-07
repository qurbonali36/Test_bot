from PIL import Image, ImageDraw, ImageFont

img_path = 'Telegram Test Achievement Certificate.png'
out_path = 'cert_masked_v2.png'

img = Image.open(img_path)
draw = ImageDraw.Draw(img)
W, H = img.size

# Hardcoded background color for main area
bg_main = img.getpixel((W//2, H//2 - 50))
bg_bottom = img.getpixel((W//2, H - 150))
bg_medal = img.getpixel((1465, 590))
bg_qr = img.getpixel((1465, 800))

# Recipient Name box
r_box = [230, 430, 1260, 600]
draw.rectangle(r_box, fill=bg_main)

# Course Name box (whole line)
c_box = [230, 680, 1260, 770]
draw.rectangle(c_box, fill=bg_main)

# Score Box
s_box = [1385, 525, 1550, 640]
draw.rectangle(s_box, fill=bg_medal)

# Date Box (only [DD/MM/YYYY])
d_box = [435, 1065, 670, 1115]
draw.rectangle(d_box, fill=bg_bottom)

# ID Box (only [UNIQUE ID])
i_box = [1110, 1065, 1370, 1115]
draw.rectangle(i_box, fill=bg_bottom)

# QR Box + text below
qr_box = [1352, 822, 1575, 1090]
draw.rectangle(qr_box, fill=bg_qr)

# Draw new text for testing
font_name = ImageFont.truetype("arialbd.ttf", 100)
font_course = ImageFont.truetype("georgiai.ttf", 50)
font_score = ImageFont.truetype("arialbd.ttf", 80)
font_small = ImageFont.truetype("arial.ttf", 30)

draw.text((745, 515), "Ali Valiyev", font=font_name, fill='white', anchor="mm")
draw.text((745, 725), "Outstanding Performance in Python Basics", font=font_course, fill='#C8A55E', anchor="mm")
draw.text((1465, 580), "95%", font=font_score, fill='#6B4912', anchor="mm")
draw.text((440, 1090), "22/08/2026", font=font_small, fill='#C8A55E', anchor="lm")
draw.text((1115, 1090), "TCA-20260822-7F4K9X", font=font_small, fill='#C8A55E', anchor="lm")

# Paste a dummy red square for QR
qr_dummy = Image.new('RGB', (210, 210), color='red')
img.paste(qr_dummy, (1358, 828))

img.save(out_path)
print("Saved v2 to", out_path)
