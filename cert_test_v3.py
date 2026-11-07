from PIL import Image, ImageDraw, ImageFont

img_path = 'Telegram Test Achievement Certificate.png'
out_path = 'cert_masked_v3.png'

img = Image.open(img_path)
draw = ImageDraw.Draw(img)

# Recipient Name box
r_box = [200, 430, 1300, 580]
draw.rectangle(r_box, fill=(17, 16, 21))

# Course Name box (whole line)
c_box = [200, 670, 1300, 755]
draw.rectangle(c_box, fill=(17, 16, 21))

# Score Box - very tight over [XX]%
s_box = [1390, 550, 1545, 625]
draw.rectangle(s_box, fill=(160, 120, 35)) # approximate center medal color

# Date Box (only [DD/MM/YYYY])
d_box = [435, 1065, 670, 1115]
draw.rectangle(d_box, fill=(13, 11, 12))

# ID Box (only [UNIQUE ID])
i_box = [1110, 1065, 1370, 1115]
draw.rectangle(i_box, fill=(13, 11, 12))

# QR Box + text below
qr_box = [1355, 825, 1572, 1090]
draw.rectangle(qr_box, fill=(17, 16, 21))

img.save(out_path)
print("Saved v3")
