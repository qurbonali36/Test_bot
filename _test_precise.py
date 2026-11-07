import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import qrcode
from datetime import datetime
import string, random

def gid():
    return "TCA-20260823-JFTBXW"  # Exact same cert ID as user's image

def run_exact_test():
    name = "Qurbonali Ergashev"
    test_title = "ingiliz_tili"
    percent_float = 100.0  # FLOAT like user reported, will be rounded to int

    cert_id = gid()
    date_str = datetime.now().strftime("%d/%m/%Y")
    img = Image.open("Telegram Test Achievement Certificate.png").convert('RGB')
    draw = ImageDraw.Draw(img)
    W, H = img.size
    print(f"Template: {W}x{H}")

    # ═══════════════════ EXACT CODE FROM certificate.py ═══════════════════
    percent = int(round(percent_float))
    print(f"[FIXED percent] {percent_float} -> {percent}  (text: '{percent}%')")

    bg_main   = img.getpixel((800, 500))
    bg_course = img.getpixel((800, 700))
    bg_bottom = img.getpixel((1000, 1090))
    bg_medal  = img.getpixel((1470, 585))
    bg_qr     = img.getpixel((1463, 900))
    print(f"Sampled colors: main={bg_main} course={bg_course} bottom={bg_bottom} medal={bg_medal} qr={bg_qr}")

    draw.rectangle([265, 425, 1285, 595], fill=bg_main)
    draw.rectangle([265, 615, 1285, 780], fill=bg_course)
    draw.rectangle([1368, 522, 1568, 655], fill=bg_medal)
    draw.rectangle([475, 1063, 695, 1118], fill=bg_bottom)
    draw.rectangle([1120, 1060, 1460, 1125], fill=bg_bottom)
    draw.rectangle([1348, 700, 1580, 1100], fill=bg_qr)
    print("Masks applied (precise version)")

    def lf(p,s,dp=None,ds=None):
        for pp,ss in [(p,s),(dp,ds)]:
            if pp:
                try: return ImageFont.truetype(pp, ss)
                except: pass
        return ImageFont.load_default()

    font_small      = lf("C:\\Windows\\Fonts\\arialbd.ttf", 35)
    font_name_fb    = lf("C:\\Windows\\Fonts\\arialbd.ttf", 90)
    font_course_fb  = lf("C:\\Windows\\Fonts\\georgiai.ttf", 55)
    font_score      = lf("C:\\Windows\\Fonts\\arialbd.ttf", 110)
    temp_name_font  = lf("fonts/GreatVibes-Regular.ttf", 160, "C:\\Windows\\Fonts\\arialbd.ttf", 90)
    temp_course_font= lf("fonts/Lora-Italic.ttf", 50, "C:\\Windows\\Fonts\\georgiai.ttf", 55)

    full_course = f"For Outstanding Performance in the\n{test_title}"

    # Shrink name font
    name_size = 160
    while True:
        try: cf = ImageFont.truetype("fonts/GreatVibes-Regular.ttf", name_size)
        except: cf = temp_name_font; break
        if draw.textlength(name, font=cf) <= 1020 or name_size <= 50:
            temp_name_font = cf; break
        name_size -= 5
    print(f"[NAME] {name}  size={name_size}  w={draw.textlength(name, font=temp_name_font):.0f}  center=(775, 510)")

    # Shrink course
    course_size = 50
    while True:
        try: cc = ImageFont.truetype("fonts/Lora-Italic.ttf", course_size)
        except: cc = temp_course_font; break
        longest = max(draw.textlength(l, font=cc) for l in full_course.split('\n'))
        if longest <= 1020 or course_size <= 25:
            temp_course_font = cc; break
        course_size -= 3
    print(f"[COURSE] 2 lines, size={course_size}, center=(775, 698)")

    # Shrink score
    score_t = f"{percent}%"
    score_size = 110
    while True:
        try: sf = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", score_size)
        except: sf = font_score; break
        if draw.textlength(score_t, font=sf) <= 160 or score_size <= 50:
            score_font = sf; break
        score_size -= 5
    print(f"[SCORE] {score_t} size={score_size} w={draw.textlength(score_t, font=score_font):.0f} center=(1468, 589)")

    draw.text((775, 510), name, font=temp_name_font, fill='#F3D78E', anchor="mm")
    draw.multiline_text((775, 698), full_course, font=temp_course_font, fill='#C8A55E', align='center', anchor="mm", spacing=6)
    draw.text((1468, 589), score_t, font=score_font, fill='#2C1A04', anchor="mm")
    draw.text((490, 1090), date_str, font=font_small, fill='#C8A55E', anchor="lm")
    draw.text((1132, 1092), cert_id, font=font_small, fill='#C8A55E', anchor="lm")

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(f"https://example.com/certificate/{cert_id}")
    qr.make(fit=True)
    qi = qr.make_image(fill_color="black", back_color="white")
    qw, qh = 1580-1348, 1100-700
    qs = min(qw, qh)-140
    qi = qi.resize((qs,qs), Image.LANCZOS)
    qx, qy = 1348+(qw-qs)//2, 700+(qh-qs)//2
    img.paste(qi, (qx, qy))
    print(f"[QR] {qs}x{qs} at ({qx},{qy}) inside mask [1348,700,1580,1100]")

    out = f"certificates/png/PRECISE-TEST-{cert_id}.png"
    img.save(out)
    print(f"\n[✅] SAVED -> {out}")

if __name__ == "__main__":
    run_exact_test()
