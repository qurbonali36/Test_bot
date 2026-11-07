import os
import math
import random
import urllib.request
from datetime import datetime

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
CERT_BASE_URL = os.getenv("CERTIFICATE_BASE_URL", "http://127.0.0.1:5000")

db = Database("tg_bot.db")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ───────────────────────── SOZLAMALAR ─────────────────────────
W, H = 1748, 1240          
S = 2                      

QR_SIZE = 190              
QR_POS = (1395, 830)       

GOLD = (193, 154, 74)
GOLD_L = (240, 205, 120)
GOLD_D = (128, 92, 34)
BG = (17, 17, 17)
LIGHT = (205, 205, 198)

FONT_DIR = os.path.join(BASE_DIR, "fonts")
os.makedirs(FONT_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "certificates", "png"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "certificates", "pdf"), exist_ok=True)

FONT_URLS = {
    "serif": ("PlayfairDisplay.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"),
    "cond": ("RobotoCondensed.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/robotocondensed/RobotoCondensed%5Bwght%5D.ttf"),
}
FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf", 
    "/Library/Fonts/Arial Bold.ttf"
]

def generate_cert_id():
    date_str = datetime.now().strftime("%Y%m%d")
    import string
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TCA-{date_str}-{random_str}"

# ───────────────────────── YORDAMCHILAR ─────────────────────────
def sc(v):
    return int(round(v * S))

def font_path(kind):
    name, url = FONT_URLS[kind]
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path):
        try:
            urllib.request.urlretrieve(url, path)
        except Exception:
            pass
    if os.path.exists(path):
        return path
    for f in FALLBACKS:
        if os.path.exists(f):
            return f
    return None

def load_font(kind, size, weight=None):
    p = font_path(kind)
    f = ImageFont.truetype(p, sc(size)) if p else ImageFont.load_default()
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f

def ramp(h, stops):
    img = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0 or 1)
                img.putpixel((0, y), tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)))
                break
    return img

GOLD_STOPS = [(0, GOLD_L), (0.5, GOLD), (1, GOLD_D)]

def text_mask(text, font, tracking=0, xscale=1.0):
    asc, desc = font.getmetrics()
    widths = [font.getlength(ch) + sc(tracking) for ch in text]
    w = int(sum(widths)) + sc(8)
    m = Image.new("L", (w, asc + desc + sc(8)), 0)
    d = ImageDraw.Draw(m)
    x = sc(4)
    for ch, cw in zip(text, widths):
        d.text((x, sc(4)), ch, font=font, fill=255)
        x += cw
    if xscale != 1.0:
        m = m.resize((max(1, int(m.width * xscale)), m.height), Image.LANCZOS)
    return m, asc + sc(4)

def fit_size(text, kind, size, max_w, weight=None, tracking=0, xscale=1.0, min_size=20):
    while size > min_size:
        f = load_font(kind, size, weight)
        m, _ = text_mask(text, f, tracking, xscale)
        if m.width <= sc(max_w):
            return f
        size -= 2
    return load_font(kind, min_size, weight)

def draw_text(img, x, baseline, text, font, fill=None, gradient=False, tracking=0, xscale=1.0, anchor="l", shadow=False):
    m, base = text_mask(text, font, tracking, xscale)
    if anchor == "m":
        px = sc(x) - m.width // 2
    elif anchor == "r":
        px = sc(x) - m.width
    else:
        px = sc(x)
    py = sc(baseline) - base
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sm = Image.new("L", img.size, 0)
        sm.paste(m, (px + sc(3), py + sc(4)))
        sm = sm.filter(ImageFilter.GaussianBlur(sc(4)))
        img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sm.point(lambda v: int(v * .8)))
    if gradient:
        g = ramp(m.height, GOLD_STOPS).resize(m.size)
        img.paste(g, (px, py), m)
    else:
        img.paste(Image.new("RGB", m.size, fill), (px, py), m)
    return m.width / S

def line(d, pts, color, width):
    d.line([(sc(x), sc(y)) for x, y in pts], fill=color, width=sc(width), joint="curve")

def diamond(d, cx, cy, r, outline=None, fill=None, width=1.5):
    pts = [(sc(cx), sc(cy - r)), (sc(cx + r), sc(cy)), (sc(cx), sc(cy + r)), (sc(cx - r), sc(cy))]
    d.polygon(pts, fill=fill, outline=outline)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=sc(width))

def chamfer(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c), (x0 + c, y0)]

# ───────────────────────── FON ─────────────────────────
def make_background():
    img = Image.new("RGB", (sc(W), sc(H)), BG)
    rg = Image.radial_gradient("L").resize((sc(W), sc(H)))
    glow = ImageOps.colorize(rg, black=(30, 30, 30), white=(10, 10, 10))
    img = glow
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(sc(40), sc(520)), (sc(230), sc(700)), (sc(40), sc(900))], fill=(255, 255, 255, 7))
    d.polygon([(sc(40), sc(830)), (sc(420), sc(1060)), (sc(250), sc(1200)), (sc(40), sc(1050))], fill=(255, 255, 255, 6))
    d.polygon([(sc(1700), sc(300)), (sc(1500), sc(120)), (sc(1700), sc(60))], fill=(255, 255, 255, 6))
    d.polygon([(sc(1390), sc(760)), (sc(1000), sc(1180)), (sc(1250), sc(1180)), (sc(1500), sc(900))], fill=(255, 255, 255, 5))
    line(d, [(45, 840), (210, 1000), (250, 1130)], GOLD + (90,), 1.5)
    line(d, [(60, 520), (210, 690)], GOLD + (60,), 1.2)
    rnd = random.Random(7)
    for (bx, by, bw, bh) in [(70, 300, 130, 190), (60, 780, 220, 260)]:
        for _ in range(260):
            x, y = bx + rnd.random() * bw, by + rnd.random() * bh
            d.ellipse([sc(x), sc(y), sc(x + 1.6), sc(y + 1.6)], fill=GOLD + (rnd.randint(25, 70),))
    return img

# ───────────────────────── RAMKA ─────────────────────────
def draw_frame(img):
    d = ImageDraw.Draw(img)
    line(d, chamfer(22, 22, W - 22, H - 22, 70), GOLD, 7)
    line(d, chamfer(22, 22, W - 22, H - 22, 70), GOLD_L, 2)
    line(d, chamfer(46, 46, W - 46, H - 46, 105), GOLD_D, 2)
    line(d, chamfer(56, 56, W - 56, H - 56, 112), GOLD, 1.2)
    for sx, sy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        ox = 22 if sx == 1 else W - 22
        oy = 22 if sy == 1 else H - 22
        pts = [(ox + sx * 70, oy), (ox + sx * 210, oy)]
        line(d, pts, GOLD_L, 10)
        line(d, [(ox, oy + sy * 70), (ox, oy + sy * 210)], GOLD_L, 10)
        line(d, [(ox + sx * 70, oy), (ox, oy + sy * 70)], GOLD_L, 10)
        line(d, [(ox + sx * 28, oy + sy * 120), (ox + sx * 110, oy + sy * 38)], GOLD, 2.5)
    for y, s in [(34, 1), (H - 34, -1)]:
        d.polygon([(sc(600), sc(y - 8 * s)), (sc(1150), sc(y - 8 * s)), (sc(1120), sc(y + 8 * s)), (sc(630), sc(y + 8 * s))], fill=GOLD)
        d.polygon([(sc(880), sc(y - 9 * s)), (sc(990), sc(y - 9 * s)), (sc(975), sc(y + 9 * s)), (sc(895), sc(y + 9 * s))], fill=GOLD_L)
    for i in range(5):
        a = 125 + i * 14
        line(d, [(a, 120 - i * 4 + 20), (a + 20, 100 - i * 4)], GOLD_L, 5)
        line(d, [(W - a, 120 - i * 4 + 20), (W - a - 20, 100 - i * 4)], GOLD_L, 5)

# ───────────────────────── AJRATGICHLAR ─────────────────────────
def divider_top(d, cx, y):
    line(d, [(cx - 205, y), (cx - 30, y)], GOLD, 1.8)
    line(d, [(cx + 30, y), (cx + 205, y)], GOLD, 1.8)
    diamond(d, cx, y, 17, outline=GOLD, width=2)
    diamond(d, cx, y, 8, fill=GOLD)
    for k in (-1, 1):
        diamond(d, cx + k * 214, y, 3.5, fill=GOLD)
        for j in (1, 2):
            line(d, [(cx + k * (36 + j * 8), y - 4), (cx + k * (42 + j * 8), y), (cx + k * (36 + j * 8), y + 4)], GOLD, 1.5)

def divider_v(d, x0, x1, y, size, depth, filled):
    cx = (x0 + x1) // 2
    line(d, [(x0, y), (cx - size, y)], GOLD, 1.8)
    line(d, [(cx + size, y), (x1, y)], GOLD, 1.8)
    tri = [(cx - size, y), (cx, y + depth), (cx + size, y)]
    if filled:
        d.polygon([(sc(a), sc(b)) for a, b in tri], fill=GOLD)
    else:
        line(d, tri, GOLD, 2.2)
    diamond(d, x0, y, 5, outline=GOLD, width=1.5)
    diamond(d, x1, y, 5, outline=GOLD, width=1.5)

# ───────────────────────── MEDAL ─────────────────────────
def draw_medal(img, cx, cy, R, score_text):
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).ellipse([sc(cx - R + 8), sc(cy - R + 18), sc(cx + R + 8), sc(cy + R + 18)], fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(sc(14)))
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sh)

    def disc(r, c_in, c_out, off=(0, 0)):
        size = sc(2 * r)
        g = Image.radial_gradient("L").resize((size, size))
        g = ImageOps.colorize(g, black=c_in, white=c_out)
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
        img.paste(g, (sc(cx + off[0] - r), sc(cy + off[1] - r)), m)

    disc(R, (250, 220, 140), (118, 82, 28), (-4, -5))      
    disc(R - 9, (150, 108, 40), (232, 190, 100), (1, 2))     
    disc(R - 14, (224, 182, 92), (150, 108, 44), (-3, -4)) 
    d = ImageDraw.Draw(img)
    for r, col, w in [(R - 1, GOLD_L, 2), (R - 16, GOLD_D, 2), (R - 56, GOLD_D, 1.5)]:
        d.ellipse([sc(cx - r), sc(cy - r), sc(cx + r), sc(cy + r)], outline=col, width=sc(w))

    def leaf(px, py, ang, L=30, Wd=12, col=(112, 78, 24)):
        t = Image.new("L", (sc(L * 2), sc(L * 2)), 0)
        ImageDraw.Draw(t).ellipse([sc(L - L / 2), sc(L - Wd / 2), sc(L + L / 2), sc(L + Wd / 2)], fill=255)
        t = t.rotate(-ang, resample=Image.BICUBIC)
        img.paste(Image.new("RGB", t.size, col), (sc(px) - t.width // 2, sc(py) - t.height // 2), t)

    r_l = R - 40
    N = 13
    for side in (-1, 1):
        for i in range(N):
            th = math.radians(28 + i * (118 / (N - 1)))      
            px = cx + side * r_l * math.sin(th)
            py = cy + r_l * math.cos(th)
            tang = math.degrees(math.atan2(-math.sin(th), side * math.cos(th)))
            leaf(px, py, tang + side * 28, L=30, Wd=11, col=(106, 74, 22) if i % 2 else (126, 90, 30))

    def star(x, y, r, col):
        pts = []
        for k in range(10):
            rr = r if k % 2 == 0 else r * 0.42
            a = math.radians(-90 + k * 36)
            pts.append((sc(x + rr * math.cos(a)), sc(y + rr * math.sin(a))))
        d.polygon(pts, fill=col)

    for dx, dy, r in [(-26, -128, 9), (0, -138, 12), (26, -128, 9)]:
        star(cx + dx, cy + dy, r, (110, 76, 22))
    for dx, dy, r in [(-34, 150, 8), (0, 156, 10), (34, 150, 8)]:
        star(cx + dx, cy + dy, r, (110, 76, 22))

    f1 = load_font("cond", 40, 700)
    draw_text(img, cx + 1, cy - 55 + 2, "SCORE", f1, fill=(245, 215, 130), anchor="m", tracking=2)
    draw_text(img, cx, cy - 55, "SCORE", f1, fill=(104, 72, 20), anchor="m", tracking=2)
    f2 = fit_size(score_text, "cond", 150, 2 * (R - 62), weight=700)
    draw_text(img, cx + 3, cy + 82 + 3, score_text, f2, fill=(246, 216, 132), anchor="m")
    draw_text(img, cx, cy + 82, score_text, f2, fill=(96, 66, 16), anchor="m")


# ───────────────────────── QR KOD ─────────────────────────
def make_qr_image(data, size_px):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0, box_size=1)
    qr.add_data(data)
    qr.make(fit=True)
    n = qr.modules_count
    margin_modules = 2                                  
    mod = max(1, size_px // (n + 2 * margin_modules))   
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((n * mod, n * mod), Image.NEAREST)
    canvas = Image.new("RGB", (size_px, size_px), "white")  
    off = (size_px - n * mod) // 2
    canvas.paste(qr_img, (off, off))
    return canvas

def draw_qr_block(img, data, caption):
    d = ImageDraw.Draw(img)
    x, y = QR_POS
    pad = 28
    ox0, oy0, ox1, oy1 = x - pad - 10, y - pad - 4, x + QR_SIZE + pad + 10, y + QR_SIZE + pad + 70
    d.rectangle([sc(ox0), sc(oy0), sc(ox1), sc(oy1)], outline=GOLD, width=sc(4))
    d.rectangle([sc(ox0 + 9), sc(oy0 + 9), sc(ox1 - 9), sc(oy1 - 9)], outline=GOLD_D, width=sc(1.5))
    qr_img = make_qr_image(data, sc(QR_SIZE))
    img.paste(qr_img, (sc(x), sc(y)))                    
    f = load_font("cond", 30, 600)
    draw_text(img, x + QR_SIZE / 2, y + QR_SIZE + 52, caption, f, fill=GOLD_L, anchor="m")

# ───────────────────────── IKONKALAR ─────────────────────────
def icon_calendar(d, x, y):
    d.rounded_rectangle([sc(x), sc(y + 6), sc(x + 40), sc(y + 46)], radius=sc(4), outline=GOLD, width=sc(2.5))
    d.rectangle([sc(x), sc(y + 6), sc(x + 40), sc(y + 16)], fill=GOLD)
    for px in (x + 9, x + 29):
        d.rectangle([sc(px - 1.5), sc(y), sc(px + 1.5), sc(y + 10)], fill=GOLD_L)
    for r in range(3):
        for c in range(4):
            d.rectangle([sc(x + 5 + c * 8), sc(y + 22 + r * 8), sc(x + 9 + c * 8), sc(y + 26 + r * 8)], fill=GOLD)

def icon_shield(d, x, y):
    outer = [(x, y + 5), (x + 20, y), (x + 40, y + 5), (x + 40, y + 27), (x + 20, y + 48), (x, y + 27)]
    d.polygon([(sc(a), sc(b)) for a, b in outer], fill=GOLD)
    inner = [(x + 4.5, y + 8.5), (x + 20, y + 4.5), (x + 35.5, y + 8.5), (x + 35.5, y + 26), (x + 20, y + 43), (x + 4.5, y + 26)]
    d.polygon([(sc(a), sc(b)) for a, b in inner], fill=BG)
    left = [(x + 7, y + 10), (x + 20, y + 7), (x + 20, y + 24), (x + 7, y + 24)]
    d.polygon([(sc(a), sc(b)) for a, b in left], fill=GOLD)
    right = [(x + 20, y + 24), (x + 33, y + 24), (x + 33, y + 26), (x + 20, y + 39)]
    d.polygon([(sc(a), sc(b)) for a, b in right], fill=GOLD)


def make_certificate(name, score, course, cert_id, verify_url, issue_date=None):
    score = float(score)
    score_str = f"{int(score)}%" if score == int(score) else f"{score:g}%"
    issue_date = issue_date or datetime.now().strftime("%d/%m/%Y")

    img = make_background()
    draw_frame(img)
    d = ImageDraw.Draw(img)

    f_title = load_font("serif", 168, 500)
    draw_text(img, 273, 296, "Certificate of Achievement", f_title, gradient=True, xscale=0.62, shadow=True)
    divider_top(d, 812, 394)

    f_name = fit_size(name, "cond", 150, 960, weight=400, tracking=5)
    draw_text(img, 273, 575, name, f_name, fill=(255, 255, 255), tracking=5)
    divider_v(d, 275, 1235, 648, 22, 24, filled=True)

    sub = f"Outstanding Performance in {course}"
    f_sub = fit_size(sub, "serif", 78, 960, weight=500, xscale=0.66)
    draw_text(img, 268, 765, sub, f_sub, gradient=True, xscale=0.66)
    divider_v(d, 270, 1238, 808, 38, 42, filled=False)

    draw_medal(img, 1483, 585, 188, score_str)

    draw_qr_block(img, f"{verify_url}", "SCAN TO VERIFY")

    icon_calendar(d, 274, 1074)
    f_foot = load_font("cond", 32, 700)
    draw_text(img, 330, 1105, f"ISSUE DATE: {issue_date}", f_foot, fill=LIGHT, tracking=1.2)
    line(d, [(753, 1045), (753, 1145)], GOLD_D, 1.5)
    diamond(d, 753, 1095, 5, outline=GOLD, width=1.5)
    icon_shield(d, 808, 1072)
    id_txt = f"CERTIFICATE ID: {cert_id}"
    f_id = fit_size(id_txt, "cond", 32, 1330 - 868, weight=700, tracking=1.2)   
    draw_text(img, 868, 1106, id_txt, f_id, fill=LIGHT, tracking=1.2)

    img = img.resize((W, H), Image.LANCZOS)
    return img


def generate_certificate_files(chat_id, test_id, correct, total, user_point, percent, lang_id, bot_username=None):
    if percent < 80:
        return None, None, None, globals.TEXT_CERT_NOT_ELIGIBLE.get(lang_id, globals.TEXT_CERT_NOT_ELIGIBLE[1])

    db_user = db.get_user_by_chat_id(chat_id)
    name = f"{db_user.get('first_name', '')} {db_user.get('last_name', '')}".strip() if db_user else "User"
    
    if len(name) > 30:
        name = name[:27] + "..."

    test_meta = db.get_test_meta(test_id)
    test_title = test_meta.get('title', test_id) if test_meta else test_id

    cert_id = generate_cert_id()
    date_str = datetime.now().strftime("%d/%m/%Y")
    percent = int(round(percent))

    if bot_username:
        verify_url = f"https://t.me/{bot_username}?start=cert_{cert_id}"
    else:
        verify_url = f"https://t.me/YourBot?start=cert_{cert_id}" 

    img = make_certificate(name, percent, test_title, cert_id, verify_url, issue_date=date_str)

    png_path = os.path.join(BASE_DIR, "certificates", "png", f"{cert_id}.png")
    pdf_path = os.path.join(BASE_DIR, "certificates", "pdf", f"{cert_id}.pdf")

    img.save(png_path, dpi=(150, 150))
    img.save(pdf_path, "PDF", resolution=100.0)

    db.save_certificate(cert_id, chat_id, test_id, name, test_title, percent, date_str, png_path, pdf_path)

    return png_path, pdf_path, cert_id, None


def send_certificate(context, chat_id, test_id, correct, total, user_point, percent, lang_id):
    bot_username = context.bot.username if hasattr(context.bot, 'username') else None
    png_path, pdf_path, cert_id, error = generate_certificate_files(chat_id, test_id, correct, total, user_point, percent, lang_id, bot_username=bot_username)

    if error:
        return

    if png_path and os.path.exists(png_path):
        bot_username = context.bot.username

        texts = {
            1: (f"🎉 <b>Tabriklaymiz!</b>\n\n"
                f"Siz testdan muvaffaqiyatli o'tdingiz!\n"
                f"📊 <b>Natija:</b> {percent}%\n"
                f"🆔 <b>ID:</b> <code>{cert_id}</code>\n\n"
                f"🏆 <i>Sertifikatingiz quyida taqdim etildi. Uni QR kod orqali istalgan vaqtda tasdiqlashingiz mumkin.</i>"),
            2: (f"🎉 <b>Поздравляем!</b>\n\n"
                f"Вы успешно прошли тест!\n"
                f"📊 <b>Результат:</b> {percent}%\n"
                f"🆔 <b>ID:</b> <code>{cert_id}</code>\n\n"
                f"🏆 <i>Ваш сертификат представлен ниже. Вы можете подтвердить его в любое время с помощью QR-кода.</i>"),
            3: (f"🎉 <b>Congratulations!</b>\n\n"
                f"You successfully passed the test!\n"
                f"📊 <b>Score:</b> {percent}%\n"
                f"🆔 <b>ID:</b> <code>{cert_id}</code>\n\n"
                f"🏆 <i>Your certificate is provided below. You can verify it anytime using the QR code.</i>")
        }
        caption = texts.get(lang_id, texts[1])

        share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=cert_{cert_id}&text=🏆 Men sertifikat oldim!"

        keyboard = [
            [InlineKeyboardButton(globals.BTN_SHARE_CERT.get(lang_id, globals.BTN_SHARE_CERT[1]), url=share_url)],
            [InlineKeyboardButton(globals.BTN_HOME.get(lang_id, globals.BTN_HOME[1]), callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as doc:
                    context.bot.send_document(
                        chat_id=chat_id, 
                        document=doc, 
                        filename=os.path.basename(pdf_path),
                        caption=caption,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                return  
            except Exception as e:
                print(f"Error sending PDF certificate: {e}")

        try:
            with open(png_path, 'rb') as photo:
                context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"Error sending certificate: {e}")
