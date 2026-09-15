from PIL import Image, ImageDraw, ImageFont
import os, sqlite3

BASE = os.path.expanduser("~/lucas-shop")
DB = os.path.join(BASE, "lucas_shop.db")
TEMPLATE = os.path.join(BASE, "ad_template.jpg")
OUT = os.path.join(BASE, "posters")
os.makedirs(OUT, exist_ok=True)

FONT_PATHS = [
    "/system/fonts/NotoSansArabic-Regular.ttf",
    "/system/fonts/NotoSans-Regular.ttf",
]

def font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def make_poster(ad_id, image_path, data, number):
    if not os.path.exists(TEMPLATE):
        print("❌ ad_template.jpg پیدا نشد")
        return None

    bg = Image.open(TEMPLATE).convert("RGB")
    bg = bg.resize((1080, 1350))
    draw = ImageDraw.Draw(bg)

    # عکس اکانت
    if image_path and os.path.exists(image_path):
        try:
            acc = Image.open(image_path).convert("RGB")
            acc.thumbnail((900, 500))
            x = (1080 - acc.width) // 2
            y = 90
            bg.paste(acc, (x, y))
        except:
            pass

    # شماره آگهی
    f_big = font(48)
    draw.text((55, 35), f"#{number}", font=f_big, fill="white")

    # اطلاعات
    f = font(34)
    lines = [
        f"🏰 TH: {data.get('townhall','-')}",
        f"🏗 BH: {data.get('builderhall','-')}",
        f"👑 King: {data.get('king','-')}",
        f"👸 Queen: {data.get('queen','-')}",
        f"🧙 Warden: {data.get('warden','-')}",
        f"⚔️ Royal Champion: {data.get('royal','-')}",
        f"📝 Name Change: {data.get('name_change','-')}",
        f"🆔 Supercell ID: {data.get('supercell_id','-')}",
        f"⭐ Level: {data.get('account_level','-')}",
        f"💰 Price: {data.get('price','-')}",
    ]

    y = 650
    for line in lines:
        draw.rounded_rectangle(
            (45, y-5, 1035, y+48),
            radius=12,
            fill=(10,10,20)
        )
        draw.text((70, y), line, font=f, fill="white")
        y += 62

    path = os.path.join(OUT, f"ad_{ad_id}_{number}.jpg")
    bg.save(path, quality=95)
    return path


def generate_for_ad(ad_id):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT * FROM ads WHERE id=?",
        (ad_id,)
    ).fetchone()
    con.close()

    if not row:
        print("❌ آگهی پیدا نشد")
        return

    data = dict(row)

    images = [
        data.get("image1"),
        data.get("image2"),
        data.get("image3")
    ]

    images = [x for x in images if x and os.path.exists(x)]

    # اگر عکس‌ها مسیر کامل ندارند
    fixed = []
    for x in images:
        if not os.path.isabs(x):
            x = os.path.join(BASE, x)
        if os.path.exists(x):
            fixed.append(x)

    images = fixed[:3]

    # حداقل یک پوستر حتی بدون عکس
    if not images:
        images = [None]

    # شماره واقعی آگهی = ID دیتابیس
    for i, img in enumerate(images, 1):
        result = make_poster(
            ad_id,
            img,
            data,
            ad_id
        )
        if result:
            print("✅ پوستر ساخته شد:", result)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("استفاده:")
        print("python poster_generator.py ID")
        raise SystemExit

    generate_for_ad(int(sys.argv[1]))
