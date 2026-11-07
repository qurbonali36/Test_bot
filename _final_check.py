import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import qrcode
from datetime import datetime

def run_final_test():
    name = "Qurbonali Ergashev"
    test_title = "ingiliz_tili"
    percent_float = 100.0
    cert_id = "TCA-20260823-JFTBXW"
    date_str = "23/08/2026"

    img = Image.open("Telegram Test Achievement Certificate.png").convert('RGB')
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # ══ EXACT certificate.py LOGIC ══
    percent = int(round(percent_float))
    print(f"[FIXED percent] {percent_float} -> {percent}")

    bg_main   = img.getpixel((800, 590))
    bg_course = img.getpixel((800, 775))
    bg_bottom = img.getpixel((820, 1085))
    bg_medal  = img.getpixel((1470, 575))
    bg_qr     = img.getpixel((1460, 900))
    print(f"Sampled bg_main  = {bg_main}  (800, 590)")
    print(f"Sampled bg_course= {bg_course} (800, 775)")
    print(f"Sampled bg_bottom= {bg_bottom} (820, 1085) <-- MUST BE DARK, NOT GOLD!")
    print(f"Sampled bg_medal = {bg_medal}  (1470, 575)")
    print(f"Sampled bg_qr    = {bg_qr}    (1460, 900)")

    # Masks
    draw.rectangle([280, 428, 1270, 592], fill=bg_main)
    draw.rectangle([280, 618, 1270, 778], fill=bg_course)
    draw.rectangle([1380, 525, 1560, 620], fill=bg_medal)
    draw.rectangle([478, 1066, 692, 1116], fill=bg_bottom)
    draw.rectangle([1125, 1062, 1458, 1122], fill=bg_bottom)
    draw.rectangle([1352, 778, 1578, 1050], fill=bg_qr)
    print("All 6 masks applied (precise)")

    def lf(p,s,dp=None,ds=None):
        for pp,ss in [(p,s),(dp,ds)]:
            if pp:
                try: return ImageFont.truetype(pp, ss)
                except: pass
        return ImageFont.load_default()

    font_small  = lf("C:\\Windows\\Fonts\\arialbd.ttf", 35)
    font_score  = lf("C:\\Windows\\Fonts\\arialbd.ttf", 110)
    fn          = lf("fonts/GreatVibes-Regular.ttf", 160, "C:\\Windows\\Fonts\\arialbd.ttf", 90)
    fc          = lf("fonts/Lora-Italic.ttf", 50, "C:\\Windows\\Fonts\\georgiai.ttf", 55)

    full_course = f"For Outstanding Performance in the\n{test_title}"

    # Dynamic sizes
    name_size, max_w = 160, 990
    while True:
        try: cf = ImageFont.truetype("fonts/GreatVibes-Regular.ttf", name_size)
        except: cf = fn; break
        if draw.textlength(name, font=cf) <= max_w or name_size <= 50: fn=cf; break
        name_size -= 5
    course_size, max_cw = 50, 990
    while True:
        try: cc = ImageFont.truetype("fonts/Lora-Italic.ttf", course_size)
        except: cc = fc; break
        longest = max(draw.textlength(l, font=cc) for l in full_course.split('\n'))
        if longest <= max_cw or course_size <= 25: fc=cc; break
        course_size -= 3
    score_t = f"{percent}%"
    score_size, max_sw = 110, 155
    while True:
        try: sf = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", score_size)
        except: sf = font_score; break
        if draw.textlength(score_t, font=sf) <= max_sw or score_size <= 50: font_score=sf; break
        score_size -= 5

    # TEXT DRAW
    draw.text((775, 510), name, font=fn, fill='#F3D78E', anchor="mm")
    draw.multiline_text((775, 698), full_course, font=fc, fill='#C8A55E', align='center', anchor="mm", spacing=6)
    draw.text((1470, 573), score_t, font=font_score, fill='#2C1A04', anchor="mm")
    draw.text((492, 1091), date_str, font=font_small, fill='#C8A55E', anchor="lm")
    draw.text((1138, 1092), cert_id, font=font_small, fill='#C8A55E', anchor="lm")

    # QR
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(f"https://example.com/c/{cert_id}")
    qr.make(fit=True)
    qi = qr.make_image(fill_color="black", back_color="white")
    qw, qh = 1578-1352, 1050-778
    qs = min(qw, qh)-24
    qi = qi.resize((qs,qs), Image.LANCZOS)
    img.paste(qi, (1352+(qw-qs)//2, 778+(qh-qs)//2))
    print(f"QR size {qs}x{qs}")

    out = f"certificates/png/LAST-{cert_id}.png"
    img.save(out)
    print(f"\n[✅ OK] saved -> {out}")

if __name__ == "__main__":
    run_final_test()
