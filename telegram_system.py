import os
import time
import math
import json
import requests
import sqlite3
from PIL import Image, ImageDraw, ImageFont, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display


TELEGRAM_BOT_TOKEN = os.getenv("LUCAS_TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL = "@LUCAS_SHOP_LS1"
TELEGRAM_ADMIN = "@LUCAS_SHOP_1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "telegram_template.jpg")
TELEGRAM_DIR = os.path.join(BASE_DIR, "uploads", "telegram_generated")

FONT_REG = "/system/fonts/NotoNaskhArabic-Regular.ttf"
FONT_BOLD = "/system/fonts/NotoNaskhArabic-Bold.ttf"

os.makedirs(TELEGRAM_DIR, exist_ok=True)


def fa(text):
    text = str(text if text is not None else "")
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)


def fit_font(draw, text, max_width, start=48, minimum=20, bold=False):
    text = fa(text)

    for size in range(start, minimum - 1, -2):
        f = font(size, bold)
        box = draw.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f

    return font(minimum, bold)


def center_text(draw, text, box, size=42, bold=True):
    x1, y1, x2, y2 = box
    text = fa(text)

    f = fit_font(
        draw,
        text,
        max(50, x2 - x1 - 30),
        start=size,
        minimum=20,
        bold=bold
    )

    bb = draw.textbbox((0, 0), text, font=f)

    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]

    x = x1 + ((x2 - x1) - tw) / 2
    y = y1 + ((y2 - y1) - th) / 2 - bb[1]

    draw.text(
        (x, y),
        text,
        font=f,
        fill=(245, 250, 255),
        stroke_width=1,
        stroke_fill=(0, 0, 0)
    )


def cover_image(path, size):
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(
        im,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )


def paste_photo(base, path, box, radius=18):
    if not path:
        return

    full = os.path.join(BASE_DIR, "uploads", str(path))

    if not os.path.exists(full):
        return

    x1, y1, x2, y2 = box
    w = max(1, x2 - x1)
    h = max(1, y2 - y1)

    try:
        photo = cover_image(full, (w, h))

        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle(
            (0, 0, w - 1, h - 1),
            radius=radius,
            fill=255
        )

        base.paste(photo, (x1, y1), mask)

    except Exception as e:
        print("TELEGRAM PHOTO ERROR:", repr(e))


def make_telegram_image(ad):
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("telegram_template.jpg پیدا نشد")

    base = Image.open(TEMPLATE_PATH).convert("RGB")
    base = base.resize((1536, 1536), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(base)

    # =====================================================
    # ۳ عکس اول داخل قاب سمت چپ
    # =====================================================

    image_names = []

    for key in [
        "image",
        "image2",
        "image3"
    ]:
        try:
            value = ad[key]
        except Exception:
            value = ""

        if value:
            image_names.append(str(value))

    # قاب اصلی سمت چپ
    if len(image_names) == 1:
        paste_photo(
            base,
            image_names[0],
            (24, 25, 900, 1280),
            18
        )

    elif len(image_names) == 2:
        # دو عکس کاملاً مساوی: یکی بالا، یکی پایین
        paste_photo(
            base,
            image_names[0],
            (24, 25, 900, 652),
            18
        )

        paste_photo(
            base,
            image_names[1],
            (24, 665, 900, 1280),
            18
        )

    elif len(image_names) >= 3:
        paste_photo(
            base,
            image_names[0],
            (24, 25, 900, 825),
            18
        )

        paste_photo(
            base,
            image_names[1],
            (24, 840, 455, 1280),
            18
        )

        paste_photo(
            base,
            image_names[2],
            (470, 840, 900, 1280),
            18
        )

    # =====================================================
    # مقادیر قالب
    # =====================================================

    listing_code = ad["listing_code"] or "-"

    town_hall = ad["town_hall"] or "-"
    builder_hall = ad["builder_hall"] or "-"
    king = ad["barbarian_king"] or "-"
    queen = ad["archer_queen"] or "-"
    warden = ad["grand_warden"] or "-"
    champion = ad["royal_champion"] or "-"

    name_change = ad["name_change"] or ""

    if str(name_change) == "با جم":
        gems = ad["name_change_gems"] or ""
        if gems:
            name_change_value = f"{gems} جم"
        else:
            name_change_value = "با جم"
    else:
        name_change_value = "رایگان"

    supercell = ad["supercell_status"] or "-"
    account_level = ad["account_level"] or "-"

    price = int(ad["price"] or 0)
    price_text = f"{price:,} تومان"

    # =====================================================
    # جای مقدارها در کادرهای قالب
    # =====================================================

    center_text(
        draw,
        listing_code,
        (1210, 30, 1485, 100),
        44,
        True
    )

    center_text(
        draw,
        town_hall,
        (1210, 135, 1480, 215),
        42,
        True
    )

    center_text(
        draw,
        builder_hall,
        (1210, 255, 1480, 335),
        42,
        True
    )

    center_text(
        draw,
        king,
        (1210, 375, 1480, 455),
        40,
        True
    )

    center_text(
        draw,
        queen,
        (1210, 495, 1480, 575),
        40,
        True
    )

    center_text(
        draw,
        warden,
        (1210, 615, 1480, 695),
        40,
        True
    )

    center_text(
        draw,
        champion,
        (1210, 735, 1480, 815),
        40,
        True
    )

    center_text(
        draw,
        name_change_value,
        (1210, 805, 1480, 885),
        34,
        True
    )

    center_text(
        draw,
        supercell,
        (1210, 905, 1480, 985),
        34,
        True
    )

    center_text(
        draw,
        account_level,
        (1210, 1000, 1480, 1080),
        38,
        True
    )

    center_text(
        draw,
        price_text,
        (900, 1110, 1480, 1215),
        38,
        True
    )

    output = os.path.join(
        TELEGRAM_DIR,
        f"{listing_code}.jpg"
    )

    base.save(
        output,
        "JPEG",
        quality=94,
        optimize=True
    )

    return output


def telegram_api(method, data=None, files=None):
    if not TELEGRAM_BOT_TOKEN:
        return {
            "ok": False,
            "description": "LUCAS_TELEGRAM_BOT_TOKEN تنظیم نشده"
        }

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/{method}"
    )

    try:
        response = requests.post(
            url,
            data=data or {},
            files=files,
            timeout=30
        )

        try:
            return response.json()
        except Exception:
            return {
                "ok": False,
                "description": response.text
            }

    except Exception as e:
        return {
            "ok": False,
            "description": repr(e)
        }


def make_normal_caption(ad, edited=False):
    code = ad["listing_code"] or "-"

    description = (
        ad["description"]
        or "توضیحی توسط فروشنده ثبت نشده است."
    )

    price = int(ad["price"] or 0)

    prefix = ""

    if edited:
        prefix = "✏️ این آگهی ویرایش شد.\n\n"

    text = (
        prefix
        + f"🔴{code} کد آگهی  #\n\n"
        + "توضیحات فروشنده :\n"
        + f"{description}\n\n"
        + f"💰قیمت 👈 {price:,} تومان"
    )

    return text[:1000]


def send_ad_to_channel(ad, db_conn, edited=False):
    try:
        image_path = make_telegram_image(ad)

        caption = make_normal_caption(
            ad,
            edited=edited
        )

        site_url = os.getenv(
            "LUCAS_SITE_URL",
            ""
        ).strip().rstrip("/")

        if not site_url:
            site_url = ""

        ad_url = ""

        if site_url:
            ad_url = (
                site_url
                + "/ad/"
                + str(ad["listing_code"])
            )

        # لینک آگهی داخل متن هم نمایش داده شود
        if ad_url:
            caption += (
                "\n\n🔗 لینک آگهی:\n"
                + ad_url
            )

        data = {
            "chat_id": TELEGRAM_CHANNEL,
            "caption": caption
        }

        if ad_url:
            data["reply_markup"] = json.dumps({
                "inline_keyboard": [[
                    {
                        "text": "برای مشاهده آگهی و عکس های دقیق کلیک کنید",
                        "url": ad_url
                    }
                ]]
            })

        with open(image_path, "rb") as f:
            result = telegram_api(
                "sendPhoto",
                data=data,
                files={
                    "photo": f
                }
            )

        if not result.get("ok"):
            print(
                "TELEGRAM SEND ERROR:",
                result
            )
            return False, None

        message_id = (
            result
            .get("result", {})
            .get("message_id")
        )

        if not message_id:
            return False, None

        db_conn.execute("""
            INSERT INTO telegram_posts
            (ad_id,message_id,kind,created_at)
            VALUES (?,?,?,?)
        """, (
            int(ad["id"]),
            int(message_id),
            "edit" if edited else "ad",
            int(time.time())
        ))

        db_conn.commit()

        print(
            "✅ TELEGRAM POSTED:",
            ad["listing_code"],
            message_id
        )

        return True, message_id

    except Exception as e:
        print(
            "TELEGRAM SEND EXCEPTION:",
            repr(e)
        )
        return False, None


def send_sold_to_channel(ad, db_conn):
    try:
        image_path = make_telegram_image(ad)

        price = int(ad["price"] or 0)

        created_at = int(
            ad["created_at"] or time.time()
        )

        elapsed = max(
            1,
            int(
                math.ceil(
                    (time.time() - created_at)
                    / 86400
                )
            )
        )

        code = ad["listing_code"] or "-"

        caption = (
            "🔻🔻🔻🔻🔻\n"
            f"✅ اکانت با کد {code} خریداری شد .\n\n"
            f"💵 اکانت فوق با قیمت {price:,} تومان فروخته شد.\n\n"
            f"⏳ این آگهی در کمتر از {elapsed} روز پس از ثبت به فروش رسید .\n\n"
            f"{TELEGRAM_CHANNEL}\n"
            "🔺🔺🔺🔺🔺"
        )

        data = {
            "chat_id": TELEGRAM_CHANNEL,
            "caption": caption[:1000]
        }

        with open(image_path, "rb") as f:
            result = telegram_api(
                "sendPhoto",
                data=data,
                files={
                    "photo": f
                }
            )

        if not result.get("ok"):
            print(
                "TELEGRAM SOLD ERROR:",
                result
            )
            return False, None

        message_id = (
            result
            .get("result", {})
            .get("message_id")
        )

        if not message_id:
            return False, None

        db_conn.execute("""
            INSERT INTO telegram_posts
            (ad_id,message_id,kind,created_at)
            VALUES (?,?,?,?)
        """, (
            int(ad["id"]),
            int(message_id),
            "sold",
            int(time.time())
        ))

        db_conn.commit()

        print(
            "✅ TELEGRAM SOLD POSTED:",
            code,
            message_id
        )

        return True, message_id

    except Exception as e:
        print(
            "TELEGRAM SOLD EXCEPTION:",
            repr(e)
        )
        return False, None


def delete_telegram_posts(ad_id, db_conn):
    rows = db_conn.execute("""
        SELECT message_id
        FROM telegram_posts
        WHERE ad_id=?
    """, (int(ad_id),)).fetchall()

    deleted = 0

    for row in rows:
        message_id = row[0]

        result = telegram_api(
            "deleteMessage",
            data={
                "chat_id": TELEGRAM_CHANNEL,
                "message_id": int(message_id)
            }
        )

        if result.get("ok"):
            deleted += 1
        else:
            print(
                "TELEGRAM DELETE WARNING:",
                message_id,
                result.get("description")
            )

    db_conn.execute(
        "DELETE FROM telegram_posts WHERE ad_id=?",
        (int(ad_id),)
    )

    db_conn.commit()

    return deleted


def ensure_telegram_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telegram_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)

    cols = [
        r[1]
        for r in conn.execute(
            "PRAGMA table_info(ads)"
        ).fetchall()
    ]

    if "telegram_edit_pending" not in cols:
        conn.execute("""
            ALTER TABLE ads
            ADD COLUMN telegram_edit_pending
            INTEGER DEFAULT 0
        """)

    conn.commit()
