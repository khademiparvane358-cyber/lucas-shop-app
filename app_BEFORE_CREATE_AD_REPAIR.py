from flask import render_template_string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import time
import secrets
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lucas.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

app = Flask(__name__)

# =========================================================
# LUCAS_SESSION_48_HOURS
# =========================================================

from datetime import timedelta

app.permanent_session_lifetime = timedelta(hours=48)




# =========================================================
# LUCAS SHOP AUTH SYSTEM - FINAL
# =========================================================

def init_auth_db():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)

    conn.commit()

    # حساب اصلی
    username = "ahmadreza"
    password = "amoahmad1a"

    row = conn.execute(
        "SELECT id FROM accounts WHERE username=?",
        (username,)
    ).fetchone()

    if row:
        conn.execute(
            "UPDATE accounts SET password=? WHERE username=?",
            (generate_password_hash(password), username)
        )
    else:
        conn.execute(
            """
            INSERT INTO accounts
            (username,password,created_at)
            VALUES (?,?,?)
            """,
            (
                username,
                generate_password_hash(password),
                int(time.time())
            )
        )

    conn.commit()
    conn.close()


def auth_page(title, content):

    return f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>{title} — LUCAS SHOP</title>

<style>

* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    min-height:100vh;
    background:
        radial-gradient(circle at top,#111c35,#03050a 55%);
    color:white;
    font-family:
        Tahoma,
        Arial,
        sans-serif;

    display:flex;
    justify-content:center;
    align-items:center;
}}

.card {{
    width:min(430px,92%);
    padding:35px;
    border-radius:25px;

    background:
        rgba(15,20,35,.88);

    border:1px solid rgba(255,255,255,.08);

    box-shadow:
        0 30px 80px rgba(0,0,0,.5);
}}

.logo {{
    text-align:center;
    font-size:28px;
    font-weight:900;
    margin-bottom:8px;
}}

.logo span {{
    color:#6ea8ff;
}}

.subtitle {{
    text-align:center;
    color:#8f9ab2;
    margin-bottom:28px;
}}

label {{
    display:block;
    margin-bottom:8px;
    color:#cbd5e1;
}}

input {{
    width:100%;
    padding:15px;
    margin-bottom:18px;

    border-radius:13px;
    border:1px solid #27324a;

    background:#080d18;
    color:white;

    outline:none;
    font-size:15px;
}}

input:focus {{
    border-color:#4f8cff;
}}

button {{
    width:100%;
    border:0;
    padding:15px;

    border-radius:13px;

    background:
        linear-gradient(135deg,#3478ff,#6b4cff);

    color:white;
    font-weight:bold;
    font-size:16px;

    cursor:pointer;
}}

.error {{
    background:#3b1118;
    border:1px solid #7f2432;
    color:#ff9ca8;

    padding:13px;
    border-radius:12px;

    margin-bottom:18px;

    text-align:center;
}}

.success {{
    background:#0b3325;
    border:1px solid #176b4b;
    color:#76e4b5;

    padding:13px;
    border-radius:12px;

    margin-bottom:18px;

    text-align:center;
}}

.link {{
    text-align:center;
    margin-top:22px;
    color:#8f9ab2;
}}

.link a {{
    color:#76aaff;
    text-decoration:none;
}}

</style>
</head>

<body>

<div class="card">

<div class="logo">
LUCAS <span>SHOP</span>
</div>

<div class="subtitle">
{title}
</div>

{content}

</div>

</body>
</html>
"""


@app.route("/login", methods=["GET","POST"])
def lucas_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            return auth_page(
                "ورود به حساب",
                """
                <div class="error">
                نام کاربری و رمز عبور را وارد کنید.
                </div>
                """ + login_form_html()
            )

        conn = db()

        user = conn.execute(
            """
            SELECT id,username,password
            FROM accounts
            WHERE username=?
            """,
            (username,)
        ).fetchone()

        conn.close()

        # حساب وجود ندارد
        if not user:

            return auth_page(
                "ورود به حساب",
                """
                <div class="error">
                حسابی با این نام کاربری ساخته نشده است.
                </div>
                """ + login_form_html()
            )

        # رمز اشتباه
        try:
            valid = check_password_hash(
                user["password"],
                password
            )
        except Exception:
            valid = False

        if not valid:

            return auth_page(
                "ورود به حساب",
                """
                <div class="error">
                رمز عبور اشتباه است.
                </div>
                """ + login_form_html()
            )

        session["user_id"] = user["id"]
        session.permanent = True
        session["lucas_login_time"] = int(time.time())
        session["username"] = user["username"]

        next_url = request.args.get("next", "/")

        if not next_url or not next_url.startswith("/"):
            next_url = "/"

        return redirect(next_url)

    return auth_page(
        "ورود به حساب",
        login_form_html()
    )


def login_form_html():

    return """
<form method="POST">

<label>نام کاربری</label>

<input
type="text"
name="username"
placeholder="نام کاربری"
autocomplete="username"
required
>

<label>رمز عبور</label>

<input
type="password"
name="password"
placeholder="رمز عبور"
autocomplete="current-password"
required
>

<button type="submit">
ورود به حساب
</button>

</form>

<div class="link">
حساب نداری؟
<a href="/register">
ساخت حساب جدید
</a>
</div>
"""


@app.route("/register", methods=["GET","POST"])
def lucas_register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        password2 = request.form.get(
            "password2",
            ""
        )

        if len(username) < 3:

            return auth_page(
                "ساخت حساب",
                """
                <div class="error">
                نام کاربری باید حداقل ۳ حرف باشد.
                </div>
                """ + register_form_html()
            )

        if len(password) < 6:

            return auth_page(
                "ساخت حساب",
                """
                <div class="error">
                رمز عبور باید حداقل ۶ کاراکتر باشد.
                </div>
                """ + register_form_html()
            )

        if password != password2:

            return auth_page(
                "ساخت حساب",
                """
                <div class="error">
                رمزهای عبور یکسان نیستند.
                </div>
                """ + register_form_html()
            )

        conn = db()

        exists = conn.execute(
            """
            SELECT id
            FROM accounts
            WHERE username=?
            """,
            (username,)
        ).fetchone()

        if exists:

            conn.close()

            return auth_page(
                "ساخت حساب",
                """
                <div class="error">
                این نام کاربری قبلاً ثبت شده است.
                </div>
                """ + register_form_html()
            )

        conn.execute(
            """
            INSERT INTO accounts
            (username,password,created_at)
            VALUES (?,?,?)
            """,
            (
                username,
                generate_password_hash(password),
                int(time.time())
            )
        )

        conn.commit()
        conn.close()

        return auth_page(
            "حساب ساخته شد",
            """
            <div class="success">
            حساب شما با موفقیت ساخته شد.
            </div>

            <div class="link">
            <a href="/login">
            ورود به حساب
            </a>
            </div>
            """
        )

    return auth_page(
        "ساخت حساب",
        register_form_html()
    )


def register_form_html():

    return """
<form method="POST">

<label>نام کاربری</label>

<input
type="text"
name="username"
placeholder="مثلاً ahmadreza"
autocomplete="username"
required
>

<label>رمز عبور</label>

<input
type="password"
name="password"
placeholder="حداقل ۶ کاراکتر"
autocomplete="new-password"
required
>

<label>تکرار رمز عبور</label>

<input
type="password"
name="password2"
placeholder="رمز عبور را دوباره وارد کنید"
autocomplete="new-password"
required
>

<button type="submit">
ساخت حساب
</button>

</form>

<div class="link">
حساب داری؟
<a href="/login">
ورود
</a>
</div>
"""


@app.route("/logout")
def lucas_logout():

    session.pop("user_id",None)
    session.pop("username",None)

    return redirect("/")


# اجرای ساخت جدول در اولین درخواست
@app.before_request
def ensure_auth_database():

    if not getattr(app,"_auth_ready",False):

        try:
            init_auth_db()
            app._auth_ready=True
        except Exception as e:
            print("AUTH DATABASE ERROR:",e)

# =========================================================
# END AUTH SYSTEM
# =========================================================


# =========================================================
# LUCAS SHOP ACCOUNT DASHBOARD
# =========================================================

@app.route("/account")
def lucas_account_dashboard():

    uid = session.get("user_id")

    if not uid:
        return redirect(
            url_for(
                "lucas_login",
                next="/account"
            )
        )

    conn = db()

    user = conn.execute(
        """
        SELECT id,username,created_at
        FROM accounts
        WHERE id=?
        """,
        (uid,)
    ).fetchone()

    if not user:
        conn.close()
        session.clear()
        return redirect("/login")

    # تعداد آگهی‌های کاربر
    ads_count = 0

    try:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM ads WHERE seller_id=?",
            (uid,)
        ).fetchone()

        if row:
            ads_count = row["c"]

    except Exception:
        ads_count = 0

    # تعداد سفارش‌ها
    orders_count = 0

    try:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM orders WHERE user_id=?",
            (uid,)
        ).fetchone()

        if row:
            orders_count = row["c"]

    except Exception:
        orders_count = 0

    conn.close()

    is_admin = (
        user["username"].lower() == "ahmadreza"
    )

    admin_box = ""

    if is_admin:

        admin_box = """
        <div class="admin">

            <div class="admin-title">
                🛡️ پنل مدیریت
            </div>

            <div class="admin-text">
                شما با حساب مدیر وارد شده‌اید.
            </div>

            <div class="admin-buttons">

                <a href="/admin">
                    مدیریت سایت
                </a>

                <a href="/">
                    مشاهده سایت
                </a>

            </div>

        </div>
        """

    html = f"""
<!doctype html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>حساب کاربری — LUCAS SHOP</title>

<style>

* {{
box-sizing:border-box;
}}

body {{
margin:0;
background:#03050a;
color:#fff;
font-family:Tahoma,Arial,sans-serif;
}}

.container {{
width:min(1100px,92%);
margin:auto;
padding:35px 0 80px;
}}

.header {{
display:flex;
justify-content:space-between;
align-items:center;
gap:15px;
margin-bottom:30px;
}}

.logo {{
font-size:26px;
font-weight:900;
}}

.logo span {{
color:#5d9bff;
}}

.back {{
text-decoration:none;
color:#fff;
background:#10182a;
padding:12px 18px;
border-radius:12px;
}}

.card {{
background:#0a0f1b;
border:1px solid #18233a;
border-radius:24px;
padding:28px;
margin-bottom:20px;
box-shadow:0 20px 60px rgba(0,0,0,.25);
}}

.user {{
font-size:25px;
font-weight:bold;
margin-bottom:8px;
}}

.muted {{
color:#8793aa;
}}

.stats {{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:15px;
margin-top:25px;
}}

.stat {{
background:#0f1727;
border:1px solid #1b2942;
border-radius:18px;
padding:22px;
}}

.stat-number {{
font-size:30px;
font-weight:900;
color:#75a9ff;
}}

.stat-title {{
color:#8c98ad;
margin-top:8px;
}}

.buttons {{
display:grid;
grid-template-columns:repeat(2,1fr);
gap:14px;
margin-top:20px;
}}

.buttons a {{
display:block;
padding:16px;
border-radius:14px;
text-align:center;
text-decoration:none;
color:white;
background:#111b30;
border:1px solid #21304d;
}}

.buttons a.primary {{
background:linear-gradient(135deg,#3478ff,#684cff);
border:0;
}}

.admin {{
padding:25px;
border-radius:22px;
background:
linear-gradient(135deg,#111d38,#090e19);
border:1px solid #315ca8;
}}

.admin-title {{
font-size:22px;
font-weight:bold;
margin-bottom:10px;
}}

.admin-text {{
color:#9ba9c0;
margin-bottom:20px;
}}

.admin-buttons {{
display:flex;
gap:12px;
flex-wrap:wrap;
}}

.admin-buttons a {{
color:white;
text-decoration:none;
background:#172542;
padding:13px 20px;
border-radius:12px;
}}

@media(max-width:650px) {{

.stats {{
grid-template-columns:1fr;
}}

.buttons {{
grid-template-columns:1fr;
}}

.header {{
align-items:flex-start;
flex-direction:column;
}}

}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<div class="logo">
LUCAS <span>SHOP</span>
</div>

<a class="back" href="/">
بازگشت به سایت
</a>

</div>

<div class="card">

<div class="user">
👤 {user["username"]}
</div>

<div class="muted">
حساب کاربری شما
</div>

<div class="stats">

<div class="stat">

<div class="stat-number">
{ads_count}
</div>

<div class="stat-title">
آگهی‌های من
</div>

</div>

<div class="stat">

<div class="stat-number">
{orders_count}
</div>

<div class="stat-title">
سفارش‌های من
</div>

</div>

<div class="stat">

<div class="stat-number">
فعال
</div>

<div class="stat-title">
وضعیت حساب
</div>

</div>

</div>

<div class="buttons">

<a class="primary" href="/create-ad">
➕ ثبت آگهی جدید
</a>

<a href="/my-ads">
📋 آگهی‌های من
</a>

<a href="/profile">
👤 پروفایل
</a>

<a href="/logout">
🚪 خروج از حساب
</a>

</div>

</div>

{admin_box}

</div>

</body>
</html>
"""

    return html

# =========================================================
# END ACCOUNT DASHBOARD
# =========================================================


# OLD_DUPLICATE_AUTH_BLOCK
# @app.route("/register", methods=["GET","POST"])
# def register():
#     if request.method == "POST":
#         username=request.form.get("username","").strip()
#         password=request.form.get("password","")
# 
#         if len(username)<3:
#             return account_page(
#                 "ساخت حساب",
#                 "<div class='error'>نام کاربری باید حداقل ۳ حرف باشد.</div>"+register_form()
#             )
# 
#         if len(password)<6:
#             return account_page(
#                 "ساخت حساب",
#                 "<div class='error'>رمز عبور باید حداقل ۶ کاراکتر باشد.</div>"+register_form()
#             )
# 
#         c=db()
# 
#         try:
#             c.execute(
#                 "INSERT INTO accounts(username,password,created_at) VALUES(?,?,?)",
#                 (username,generate_password_hash(password),int(time.time()))
#             )
#             c.commit()
# 
#             user=c.execute(
#                 "SELECT id FROM accounts WHERE username=?",
#                 (username,)
#             ).fetchone()
# 
#             c.close()
# 
#             session["user_id"]=user[0]
#             session.permanent = True
#             session["lucas_login_time"] = int(time.time())
# 
#             return redirect("/account")
# 
#         except sqlite3.IntegrityError:
#             c.close()
#             return account_page(
#                 "ساخت حساب",
#                 "<div class='error'>این نام کاربری قبلاً استفاده شده است.</div>"+register_form()
#             )
# 
#     return account_page("ساخت حساب",register_form())
# 
# 
# def register_form():
#     return """
# <h1>ساخت حساب جدید</h1>
# 
# <form method="POST">
# 
# <label>نام کاربری</label>
# <input
#  name="username"
#  placeholder="مثلاً lucas123"
#  autocomplete="username"
#  required>
# 
# <label>رمز عبور</label>
# <input
#  type="password"
#  name="password"
#  placeholder="حداقل ۶ کاراکتر"
#  autocomplete="new-password"
#  required>
# 
# <button type="submit">
# ساخت حساب
# </button>
# 
# </form>
# 
# <div style="margin-top:20px;color:#8490a5">
# قبلاً حساب ساخته‌ای؟
# <a href="/login" style="color:#76aaff">ورود به حساب</a>
# </div>
# """
# 
# 
# @app.route("/login", methods=["GET","POST"])
# def login():
#     if request.method=="POST":
#         username=request.form.get("username","").strip()
#         password=request.form.get("password","")
# 
#         c=db()
#         user=c.execute(
#             "SELECT id,username,password FROM accounts WHERE username=?",
#             (username,)
#         ).fetchone()
#         c.close()
# 
#         if not user or not check_password_hash(user[2],password):
#             return account_page(
#                 "ورود",
#                 "<div class='error'>نام کاربری یا رمز عبور اشتباه است.</div>"+login_form()
#             )
# 
#         session["user_id"]=user[0]
#         session.permanent = True
#         session["lucas_login_time"] = int(time.time())
# 
#         return redirect("/account")
# 
#     return account_page("ورود",login_form())
# 
# 
# def login_form():
#     return """
# <h1>ورود به LUCAS SHOP</h1>
# 
# <form method="POST">
# 
# <label>نام کاربری</label>
# <input
#  name="username"
#  autocomplete="username"
#  required>
# 
# <label>رمز عبور</label>
# <input
#  type="password"
#  name="password"
#  autocomplete="current-password"
#  required>
# 
# <button type="submit">
# ورود
# </button>
# 
# </form>
# 
# <div style="margin-top:20px;color:#8490a5">
# حساب نداری؟
# <a href="/register" style="color:#76aaff">ساخت حساب</a>
# </div>
# """
# 
# 
# @app.route("/logout")
# def logout():
#     session.pop("user_id",None)
#     return redirect("/")
# 
# 
# @app.route("/account")
# def account():
#     user=current_user()
# 
#     if not user:
#         return redirect("/login")
# 
#     c=db()
# 
#     # تلاش برای استفاده از جدول ads قبلی
#     try:
#         ads=c.execute(
#             "SELECT id,title,price,description FROM ads WHERE seller_id=? ORDER BY id DESC",
#             (user[0],)
#         ).fetchall()
#     except Exception:
#         ads=[]
# 
#     c.close()
# 
#     ads_html=""
# 
#     for ad in ads:
#         ads_html += f"""
# <div class="ad">
# <div class="ad-title">{ad[1]}</div>
# <div class="ad-meta">قیمت: {ad[2]}</div>
# <div style="color:#8995a9;margin-bottom:14px">
# {ad[3] or ''}
# </div>
# <div class="actions">
# <a class="btn" href="/edit-ad/{ad[0]}">ویرایش آگهی</a>
# <a class="btn danger"
# href="/delete-ad/{ad[0]}"
# onclick="return confirm('آگهی حذف شود؟')">
# حذف
# </a>
# </div>
# </div>
# """
# 
#     if not ads_html:
#         ads_html="""
# <div class="ad">
# <div class="ad-title">هنوز آگهی‌ای ثبت نکرده‌ای</div>
# <div class="ad-meta">
# اولین آگهی خودت را در LUCAS SHOP ثبت کن.
# </div>
# <a class="btn" href="/create-ad">ثبت آگهی</a>
# </div>
# """
# 
#     body=f"""
# <h1>حساب کاربری</h1>
# 
# <div style="color:#8490a5;margin-bottom:20px">
# خوش آمدی، <strong style="color:white">{user[1]}</strong>
# </div>
# 
# <div class="grid">
# 
# <div class="stat">
# <strong>{len(ads)}</strong>
# <span>تعداد آگهی‌ها</span>
# </div>
# 
# <div class="stat">
# <strong>فعال</strong>
# <span>وضعیت حساب</span>
# </div>
# 
# <div class="stat">
# <strong>LUCAS</strong>
# <span>عضویت در فروشگاه</span>
# </div>
# 
# </div>
# 
# <div class="actions" style="margin-bottom:30px">
# <a class="btn" href="/create-ad">＋ ثبت آگهی جدید</a>
# <a class="btn" href="/logout">خروج از حساب</a>
# </div>
# 
# <h2>آگهی‌های من</h2>
# 
# {ads_html}
# """
# 
#     return account_page("حساب کاربری",body)
# 
# 
# 

@app.route("/create-ad", methods=["GET","POST"])
def create_ad():

    user = current_user()

    # اگر وارد نیست، دقیقاً بعد از ورود برگردد به ثبت آگهی
    if not user:
        return redirect(url_for("lucas_login", next="/create-ad"))

    # اطمینان از وجود جدول کامل آگهی‌ها
    try:
        lucas_prepare_ads_table()
    except Exception as e:
        print("ADS TABLE ERROR:", e)

    if request.method == "POST":

        title = request.form.get("title","").strip()
        price = request.form.get("price","").strip()
        description = request.form.get("description","").strip()

        town_hall = request.form.get("town_hall","").strip()
        builder_hall = request.form.get("builder_hall","").strip()

        barbarian_king = request.form.get("barbarian_king","").strip()
        archer_queen = request.form.get("archer_queen","").strip()
        grand_warden = request.form.get("grand_warden","").strip()
        royal_champion = request.form.get("royal_champion","").strip()

        telegram = request.form.get("telegram","").strip()

        if not title:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>عنوان آگهی را وارد کن.</div>" + ad_form()
            )

        if not price:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>قیمت را وارد کن.</div>" + ad_form()
            )

        # فقط عدد برای قیمت
        try:
            price_int = int(
                price.replace(",","").replace("٬","").replace(" ","")
            )
        except:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>قیمت باید عددی باشد.</div>" + ad_form()
            )

        # ----------------------------------------------------
        # آپلود عکس
        # ----------------------------------------------------
        image_name = ""

        try:
            photo = request.files.get("image")

            if photo and photo.filename:
                filename = photo.filename.strip()

                if allowed_file(filename):
                    import uuid
                    ext = filename.rsplit(".",1)[1].lower()
                    image_name = uuid.uuid4().hex + "." + ext

                    photo.save(
                        str(Path(UPLOAD_DIR) / image_name)
                    )
        except Exception as e:
            print("IMAGE ERROR:", e)

        # ----------------------------------------------------
        # ذخیره آگهی
        # ----------------------------------------------------
        c = db()

        c.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                title TEXT NOT NULL,
                price INTEGER DEFAULT 0,
                description TEXT DEFAULT '',
                image TEXT DEFAULT '',
                town_hall TEXT DEFAULT '',
                builder_hall TEXT DEFAULT '',
                barbarian_king TEXT DEFAULT '',
                archer_queen TEXT DEFAULT '',
                grand_warden TEXT DEFAULT '',
                royal_champion TEXT DEFAULT '',
                telegram TEXT DEFAULT '',
                created_at INTEGER DEFAULT 0
            )
        """)

        # ستون‌های احتمالی قدیمی را هم اضافه کن
        existing = {
            row[1]
            for row in c.execute("PRAGMA table_info(ads)").fetchall()
        }

        extra_fields = {
            "image":"TEXT DEFAULT ''",
            "town_hall":"TEXT DEFAULT ''",
            "builder_hall":"TEXT DEFAULT ''",
            "barbarian_king":"TEXT DEFAULT ''",
            "archer_queen":"TEXT DEFAULT ''",
            "grand_warden":"TEXT DEFAULT ''",
            "royal_champion":"TEXT DEFAULT ''",
            "telegram":"TEXT DEFAULT ''",
            "created_at":"INTEGER DEFAULT 0"
        }

        for name, definition in extra_fields.items():
            if name not in existing:
                c.execute(
                    f"ALTER TABLE ads ADD COLUMN {name} {definition}"
                )

        c.execute("""
            INSERT INTO ads (
                seller_id,
                title,
                price,
                description,
                image,
                town_hall,
                builder_hall,
                barbarian_king,
                archer_queen,
                grand_warden,
                royal_champion,
                telegram,
                created_at
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            user[0],
            title,
            price_int,
            description,
            image_name,
            town_hall,
            builder_hall,
            barbarian_king,
            archer_queen,
            grand_warden,
            royal_champion,
            telegram,
            int(time.time())
        ))

        c.commit()
        c.close()

        return redirect("/account")

    return account_page(
        "ثبت آگهی",
        ad_form()
    )


def ad_form(ad=None):

    def val(index, default=""):
        if not ad:
            return default
        try:
            return ad[index] or default
        except:
            return default

    title = val(1)
    price = val(2)
    description = val(3)

    # اگر ردیف قدیمی باشد، خطا نمی‌دهد
    image = val(4)
    town_hall = val(5)
    builder_hall = val(6)
    barbarian_king = val(7)
    archer_queen = val(8)
    grand_warden = val(9)
    royal_champion = val(10)
    telegram = val(11)

    return f"""
<style>
.adbox {{
    max-width:760px;
    margin:auto;
}}
.adbox h1 {{
    margin-bottom:8px;
}}
.adhint {{
    color:#8d9ab0;
    margin-bottom:22px;
    line-height:1.8;
}}
.adgrid {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:14px;
}}
.adfield {{
    margin-bottom:16px;
}}
.adfield.full {{
    grid-column:1/-1;
}}
.adfield label {{
    display:block;
    margin-bottom:8px;
    font-weight:800;
}}
.adfield input,
.adfield textarea,
.adfield select {{
    width:100%;
    padding:13px 14px;
    border-radius:12px;
    border:1px solid #26354d;
    background:#0b1422;
    color:white;
    outline:none;
}}
.adfield textarea {{
    min-height:130px;
    resize:vertical;
}}
.levels {{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
}}
.levels input {{
    display:none;
}}
.levels label {{
    margin:0;
    padding:10px 13px;
    border:1px solid #26354d;
    border-radius:10px;
    background:#0b1422;
    cursor:pointer;
}}
.levels input:checked + label {{
    background:#2563eb;
    border-color:#2563eb;
}}
.adactions {{
    display:flex;
    gap:10px;
    margin-top:10px;
}}
@media(max-width:650px){{
    .adgrid{{grid-template-columns:1fr}}
}}
</style>

<div class="adbox">

<h1>📢 ثبت آگهی اکانت</h1>

<div class="adhint">
اطلاعات اکانت را کامل وارد کن تا آگهی در LUCAS SHOP نمایش داده شود.
</div>

<form method="POST" enctype="multipart/form-data">

<div class="adgrid">

<div class="adfield full">
<label>عنوان آگهی</label>
<input
name="title"
value="{title}"
placeholder="مثلاً اکانت تاون هال 17 فول"
required>
</div>

<div class="adfield">
<label>🏰 تاون هال</label>
<select name="town_hall">
<option value="">انتخاب تاون هال</option>
{''.join(
    f'<option value="{i}" {"selected" if str(town_hall)==str(i) else ""}>TH {i}</option>'
    for i in range(1,19)
)}
</select>
</div>

<div class="adfield">
<label>🔨 بیلدر هال</label>
<select name="builder_hall">
<option value="">انتخاب بیلدر هال</option>
{''.join(
    f'<option value="{i}" {"selected" if str(builder_hall)==str(i) else ""}>BH {i}</option>'
    for i in range(1,12)
)}
</select>
</div>

<div class="adfield full">
<label>🦸 سطح هیروها</label>

<div class="levels">

<input id="bk" name="barbarian_king" value="{barbarian_king}" placeholder="شاه بربر">
<label for="bk">👑 شاه بربر</label>

<input id="aq" name="archer_queen" value="{archer_queen}" placeholder="ملکه کماندار">
<label for="aq">🏹 ملکه کماندار</label>

<input id="gw" name="grand_warden" value="{grand_warden}" placeholder="گرند واردن">
<label for="gw">🧙 گرند واردن</label>

<input id="rc" name="royal_champion" value="{royal_champion}" placeholder="رویال چمپیون">
<label for="rc">⚔️ رویال چمپیون</label>

</div>

<div style="color:#728199;font-size:12px;margin-top:8px">
سطح هر هیرو را داخل کادر مربوط به خودش وارد کن.
</div>
</div>

<div class="adfield">
<label>💰 قیمت</label>
<input
name="price"
value="{price}"
inputmode="numeric"
placeholder="مثلاً 500000"
required>
</div>

<div class="adfield">
<label>📱 آیدی تلگرام</label>
<input
name="telegram"
value="{telegram}"
placeholder="@username">
</div>

<div class="adfield full">
<label>📝 توضیحات کامل</label>
<textarea
name="description"
placeholder="توضیحات کامل اکانت...">{description}</textarea>
</div>

<div class="adfield full">
<label>🖼️ عکس اکانت</label>
<input
type="file"
name="image"
accept="image/png,image/jpeg,image/webp,image/gif">
<div style="color:#728199;font-size:12px;margin-top:7px">
عکس مناسب اکانت را انتخاب کن.
</div>
</div>

</div>

<div class="adactions">
<button class="btn primary" type="submit">
📢 ثبت آگهی
</button>

<a class="btn" href="/account">
انصراف
</a>
</div>

</form>
</div>
"""


@app.route("/edit-ad/<int:ad_id>", methods=["GET","POST"])
def edit_ad(ad_id):
    user=current_user()

    if not user:
        return redirect("/login")

    c=db()

    try:
        ad=c.execute(
            "SELECT id,title,price,description FROM ads WHERE id=? AND seller_id=?",
            (ad_id,user[0])
        ).fetchone()
    except Exception:
        ad=None

    if not ad:
        c.close()
        return account_page(
            "خطا",
            "<div class='error'>این آگهی وجود ندارد یا متعلق به حساب شما نیست.</div>"
            "<a class='btn' href='/account'>بازگشت</a>"
        )

    if request.method=="POST":

        title=request.form.get("title","").strip()
        price=request.form.get("price","").strip()
        description=request.form.get("description","").strip()

        c.execute("""
            UPDATE ads
            SET title=?,price=?,description=?
            WHERE id=? AND seller_id=?
        """,(title,price,description,ad_id,user[0]))

        c.commit()
        c.close()

        return redirect("/account")

    c.close()

    return account_page(
        "ویرایش آگهی",
        "<h1>ویرایش آگهی</h1>"+ad_form(ad)
    )


@app.route("/delete-ad/<int:ad_id>")
def delete_ad(ad_id):
    user=current_user()

    if not user:
        return redirect("/login")

    c=db()

    try:
        c.execute(
            "DELETE FROM ads WHERE id=? AND seller_id=?",
            (ad_id,user[0])
        )
        c.commit()
    except Exception:
        pass

    c.close()

    return redirect("/account")


app.secret_key = "LUCAS_SHOP_SESSION_KEY_1598"

os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "webp", "gif", "svg"
}


# ============================================================
# DATABASE
# ============================================================

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn




# =========================================================
# LUCAS_ADS_TABLE_READY
# =========================================================

def lucas_prepare_ads_table():

    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            title TEXT NOT NULL,
            price INTEGER DEFAULT 0,
            description TEXT DEFAULT '',
            image TEXT DEFAULT '',
            town_hall TEXT DEFAULT '',
            builder_hall TEXT DEFAULT '',
            barbarian_king TEXT DEFAULT '',
            archer_queen TEXT DEFAULT '',
            grand_warden TEXT DEFAULT '',
            royal_champion TEXT DEFAULT '',
            telegram TEXT DEFAULT '',
            created_at INTEGER DEFAULT 0
        )
    """)

    existing = {
        x[1]
        for x in conn.execute(
            "PRAGMA table_info(ads)"
        ).fetchall()
    }

    fields = {
        "seller_id": "INTEGER",
        "title": "TEXT",
        "price": "INTEGER DEFAULT 0",
        "description": "TEXT DEFAULT ''",
        "image": "TEXT DEFAULT ''",
        "town_hall": "TEXT DEFAULT ''",
        "builder_hall": "TEXT DEFAULT ''",
        "barbarian_king": "TEXT DEFAULT ''",
        "archer_queen": "TEXT DEFAULT ''",
        "grand_warden": "TEXT DEFAULT ''",
        "royal_champion": "TEXT DEFAULT ''",
        "telegram": "TEXT DEFAULT ''",
        "created_at": "INTEGER DEFAULT 0"
    }

    for name, definition in fields.items():

        if name not in existing:

            conn.execute(
                f"ALTER TABLE ads ADD COLUMN {name} {definition}"
            )

    conn.commit()
    conn.close()


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            password TEXT DEFAULT '',
            avatar TEXT DEFAULT '',
            created_at INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            price INTEGER DEFAULT 0,
            old_price INTEGER DEFAULT 0,
            category TEXT DEFAULT 'عمومی',
            image TEXT DEFAULT '',
            badge TEXT DEFAULT '',
            rating REAL DEFAULT 5,
            stock INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            featured INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            total INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            UNIQUE(user_id, product_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)

    defaults = {
        "site_name": "NOVA",
        "site_description": "تجربه‌ای متفاوت در دنیای دیجیتال",
        "currency": "تومان",
        "announcement": "به نسل جدید تجربه دیجیتال خوش آمدید",
    }

    for key, value in defaults.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",
            (key, value)
        )

    conn.commit()
    conn.close()


def get_setting(key, default=""):
    conn = db()
    row = conn.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    ).fetchone()
    conn.close()

    if row:
        return row["value"]

    return default


def set_setting(key, value):
    conn = db()
    conn.execute("""
        INSERT INTO settings(key,value)
        VALUES(?,?)
        ON CONFLICT(key)
        DO UPDATE SET value=excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def money(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


@app.template_filter("money")
def money_filter(value):
    return money(value)




# =========================================================
# LUCAS ADS LOGIN CHECK
# =========================================================


def lucas_valid_ad_session():

    user = current_user()

    if not user:
        return False

    login_time = session.get("lucas_login_time")

    if not login_time:
        return True

    # 48 ساعت اعتبار برای ثبت/مدیریت آگهی
    return (int(time.time()) - int(login_time)) < (48 * 60 * 60)


def lucas_mark_login():

    session.permanent = True
    session["lucas_login_time"] = int(time.time())


def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    conn = db()

    try:
        # سیستم ورود LUCAS SHOP از accounts استفاده می‌کند
        user = conn.execute(
            """
            SELECT id, username, password, created_at
            FROM accounts
            WHERE id=?
            """,
            (user_id,)
        ).fetchone()
    except Exception:
        user = None

    conn.close()

    return user


@app.context_processor
def global_context():
    return {
        "current_user": current_user(),
        "site_name": get_setting("site_name", "LUCAS SHOP"),
        "announcement": get_setting(
            "announcement",
            "به LUCAS SHOP خوش آمدید"
        ),
        "currency": get_setting("currency", "تومان")
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    conn = db()

    featured = conn.execute("""
        SELECT *
        FROM products
        WHERE active=1 AND featured=1
        ORDER BY id DESC
        LIMIT 12
    """).fetchall()

    latest = conn.execute("""
        SELECT *
        FROM products
        WHERE active=1
        ORDER BY id DESC
        LIMIT 16
    """).fetchall()

    categories = conn.execute("""
        SELECT category, COUNT(*) AS total
        FROM products
        WHERE active=1
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template(
        "home.html",
        featured=featured,
        latest=latest,
        categories=categories
    )


# ============================================================
# EXPLORE
# ============================================================

@app.route("/explore")
def explore():
    try:
        conn = db()
        rows = conn.execute("""
            SELECT
                id,
                title,
                description,
                price,
                image,
                category,
                created_at
            FROM products
            WHERE active = 1
            ORDER BY id DESC
        """).fetchall()
        conn.close()
        products = rows
    except Exception:
        try:
            conn = db()
            products = conn.execute("""
                SELECT * FROM products
                ORDER BY id DESC
            """).fetchall()
            conn.close()
        except Exception:
            products = []

    return render_template(
        "explore.html",
        products=products,
        site_name="LUCAS SHOP"
    )

@app.route("/product/<int:product_id>")
def product(product_id):

    conn = db()

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id=? AND active=1
    """, (product_id,)).fetchone()

    if not product:
        conn.close()
        abort(404)

    conn.execute("""
        UPDATE products
        SET views=views+1
        WHERE id=?
    """, (product_id,))

    related = conn.execute("""
        SELECT *
        FROM products
        WHERE active=1
        AND category=?
        AND id!=?
        ORDER BY RANDOM()
        LIMIT 4
    """, (product["category"], product_id)).fetchall()

    conn.commit()
    conn.close()

    return render_template(
        "product.html",
        product=product,
        related=related
    )


# ============================================================
# FAVORITES
# ============================================================

@app.post("/favorite/<int:product_id>")
def favorite(product_id):

    user = current_user()

    if not user:
        return jsonify({
            "ok": False,
            "login": True
        })

    conn = db()

    exists = conn.execute("""
        SELECT id
        FROM favorites
        WHERE user_id=? AND product_id=?
    """, (user["id"], product_id)).fetchone()

    if exists:

        conn.execute("""
            DELETE FROM favorites
            WHERE user_id=? AND product_id=?
        """, (user["id"], product_id))

        state = False

    else:

        conn.execute("""
            INSERT OR IGNORE INTO favorites(user_id,product_id)
            VALUES(?,?)
        """, (user["id"], product_id))

        state = True

    conn.commit()
    conn.close()

    return jsonify({
        "ok": True,
        "favorite": state
    })


# SEARCH API
# ============================================================

@app.get("/api/search")
def api_search():

    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    conn = db()

    rows = conn.execute("""
        SELECT
            id,
            title,
            price,
            image,
            category
        FROM products
        WHERE active=1
        AND (
            title LIKE ?
            OR description LIKE ?
            OR category LIKE ?
        )
        ORDER BY views DESC
        LIMIT 10
    """, (
        f"%{q}%",
        f"%{q}%",
        f"%{q}%"
    )).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# PRODUCTS API
# ============================================================

@app.get("/api/products")
def api_products():

    conn = db()

    rows = conn.execute("""
        SELECT *
        FROM products
        WHERE active=1
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return jsonify({
        "status": "ok",
        "site": get_setting("site_name", "NOVA"),
        "time": int(time.time())
    })


# ============================================================
# 404
# ============================================================


@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.errorhandler(404)
def not_found(error):

    return render_template(
        "404.html"
    ), 404



# ===== LUCAS FULL UPGRADE START =====

@app.route("/profile")
def lucas_profile():
    user = current_user()

    if not user:
        return redirect(url_for("lucas_login", next="/profile"))

    conn = db()

    row = conn.execute("""
        SELECT id, username, created_at
        FROM accounts
        WHERE id=?
    """, (user["id"],)).fetchone()

    ads_count = conn.execute("""
        SELECT COUNT(*) AS c
        FROM ads
        WHERE seller_id=?
    """, (user["id"],)).fetchone()["c"]

    conn.close()

    created = time.strftime(
        "%Y/%m/%d",
        time.localtime(row["created_at"])
    )

    return render_template_string("""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>پروفایل — LUCAS SHOP</title>
<style>
body{margin:0;background:#03050a;color:#fff;font-family:Tahoma,Arial}
.wrap{width:min(850px,92%);margin:50px auto}
.card{background:#0a1020;border:1px solid #1b3157;border-radius:25px;padding:30px;box-shadow:0 20px 70px #0008}
.logo{font-size:27px;font-weight:900;margin-bottom:25px}
.logo span{color:#4d91ff}
.avatar{width:90px;height:90px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2878ff,#593dff);font-size:35px;font-weight:900;margin-bottom:20px}
h1{margin:0 0 8px}
.muted{color:#8290a8}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-top:25px}
.stat{background:#0e1729;border:1px solid #1d3151;border-radius:17px;padding:20px}
.num{font-size:27px;font-weight:900;color:#6ba6ff}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:25px}
a{color:white;text-decoration:none;background:#15233b;padding:13px 18px;border-radius:12px}
.primary{background:linear-gradient(135deg,#2878ff,#6048ff)}
@media(max-width:600px){.stats{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo">LUCAS <span>SHOP</span></div>
<div class="card">
<div class="avatar">L</div>
<h1>{{ row["username"] }}</h1>
<div class="muted">عضو LUCAS SHOP</div>
<div class="stats">
<div class="stat">
<div class="num">{{ ads_count }}</div>
<div class="muted">آگهی‌های من</div>
</div>
<div class="stat">
<div class="num">{{ created }}</div>
<div class="muted">تاریخ عضویت</div>
</div>
</div>
<div class="actions">
<a class="primary" href="/create-ad">➕ ثبت آگهی</a>
<a href="/my-ads">📋 آگهی‌های من</a>
<a href="/">🏠 صفحه اصلی</a>
<a href="/logout">🚪 خروج</a>
</div>
</div>
</div>
</body>
</html>
""", row=row, ads_count=ads_count, created=created)


@app.route("/my-ads")
def lucas_my_ads():
    user = current_user()

    if not user:
        return redirect(url_for("lucas_login", next="/my-ads"))

    conn = db()

    ads = conn.execute("""
        SELECT *
        FROM ads
        WHERE seller_id=?
        ORDER BY id DESC
    """, (user["id"],)).fetchall()

    conn.close()

    return render_template_string("""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>آگهی‌های من — LUCAS SHOP</title>
<style>
body{margin:0;background:#03050a;color:white;font-family:Tahoma,Arial}
.wrap{width:min(1100px,92%);margin:35px auto}
.logo{font-size:28px;font-weight:900;margin-bottom:25px}
.logo span{color:#4e92ff}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
a{color:white;text-decoration:none}
.btn{background:#13223a;padding:12px 17px;border-radius:12px}
.primary{background:linear-gradient(135deg,#2679ff,#6048ff)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:#0a1020;border:1px solid #1b3155;border-radius:20px;overflow:hidden}
.pic{width:100%;height:180px;object-fit:cover;background:#101a2d}
.noimg{height:180px;display:flex;align-items:center;justify-content:center;color:#60708b}
.body{padding:18px}
.title{font-size:18px;font-weight:900;margin-bottom:12px}
.price{color:#65a0ff;font-size:20px;font-weight:900}
.meta{color:#8390a7;font-size:13px;margin-top:10px;line-height:1.8}
.actions{display:flex;gap:8px;margin-top:15px}
.danger{background:#431824}
@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}}
@media(max-width:550px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<div class="top">
<div class="logo">LUCAS <span>SHOP</span></div>
<a class="btn primary" href="/create-ad">➕ ثبت آگهی</a>
</div>

{% if not ads %}
<div class="card" style="padding:30px">
هنوز آگهی‌ای ثبت نکرده‌ای.
</div>
{% endif %}

<div class="grid">
{% for ad in ads %}
<div class="card">
{% if ad["image"] %}
<img class="pic" src="/uploads/{{ ad['image'] }}">
{% else %}
<div class="noimg">بدون تصویر</div>
{% endif %}
<div class="body">
<div class="title">{{ ad["title"] }}</div>
<div class="price">{{ "{:,}".format(ad["price"] or 0) }} تومان</div>
<div class="meta">
🏰 TH {{ ad["town_hall"] or "—" }}<br>
🔨 BH {{ ad["builder_hall"] or "—" }}<br>
👑 شاه بربر: {{ ad["barbarian_king"] or "—" }}<br>
🏹 ملکه: {{ ad["archer_queen"] or "—" }}<br>
🧙 واردن: {{ ad["grand_warden"] or "—" }}<br>
⚔️ رویال: {{ ad["royal_champion"] or "—" }}
</div>
<div class="actions">
<a class="btn" href="/ad/{{ ad['id'] }}">مشاهده</a>
<a class="btn" href="/edit-ad/{{ ad['id'] }}">ویرایش</a>
<a class="btn danger" href="/delete-ad/{{ ad['id'] }}" onclick="return confirm('آگهی حذف شود؟')">حذف</a>
</div>
</div>
</div>
{% endfor %}
</div>
</div>
</body>
</html>
""", ads=ads)


@app.route("/ad/<int:ad_id>")
def lucas_ad_detail(ad_id):
    conn = db()

    ad = conn.execute("""
        SELECT *
        FROM ads
        WHERE id=?
    """, (ad_id,)).fetchone()

    conn.close()

    if not ad:
        abort(404)

    telegram = ad["telegram"] or "@LUCAS_SHOP_1"

    if not telegram.startswith("@"):
        telegram = "@" + telegram

    return render_template_string("""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ ad["title"] }} — LUCAS SHOP</title>
<style>
body{margin:0;background:#02050a;color:#fff;font-family:Tahoma,Arial}
.wrap{width:min(1050px,92%);margin:35px auto}
.logo{font-size:28px;font-weight:900;margin-bottom:25px}
.logo span{color:#4c91ff}
.card{background:#090f1c;border:1px solid #1b3155;border-radius:25px;overflow:hidden}
.hero{width:100%;max-height:520px;object-fit:contain;background:#050914}
.noimg{height:280px;display:flex;align-items:center;justify-content:center;color:#62708a;background:#070c16}
.body{padding:28px}
h1{margin-top:0}
.price{font-size:28px;color:#69a4ff;font-weight:900;margin:15px 0}
.specs{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:25px 0}
.spec{padding:16px;background:#0e1728;border:1px solid #1c3151;border-radius:15px}
.spec b{color:#68a3ff}
.desc{white-space:pre-line;color:#b4bfd0;line-height:2}
.contact{display:inline-block;background:linear-gradient(135deg,#287cff,#6048ff);padding:15px 24px;border-radius:14px;color:white;text-decoration:none;font-weight:bold;margin-top:20px}
.back{display:inline-block;margin-bottom:20px;color:#8eaeff;text-decoration:none}
@media(max-width:600px){.specs{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo">LUCAS <span>SHOP</span></div>
<a class="back" href="/explore">← برگشت به آگهی‌ها</a>
<div class="card">
{% if ad["image"] %}
<img class="hero" src="/uploads/{{ ad['image'] }}">
{% else %}
<div class="noimg">این آگهی تصویر ندارد</div>
{% endif %}
<div class="body">
<h1>{{ ad["title"] }}</h1>
<div class="price">{{ "{:,}".format(ad["price"] or 0) }} تومان</div>

<div class="specs">
<div class="spec">🏰 <b>Town Hall:</b> {{ ad["town_hall"] or "—" }}</div>
<div class="spec">🔨 <b>Builder Hall:</b> {{ ad["builder_hall"] or "—" }}</div>
<div class="spec">👑 <b>شاه بربر:</b> {{ ad["barbarian_king"] or "—" }}</div>
<div class="spec">🏹 <b>ملکه کماندار:</b> {{ ad["archer_queen"] or "—" }}</div>
<div class="spec">🧙 <b>گرند واردن:</b> {{ ad["grand_warden"] or "—" }}</div>
<div class="spec">⚔️ <b>رویال چمپیون:</b> {{ ad["royal_champion"] or "—" }}</div>
</div>

<h3>📝 توضیحات</h3>
<div class="desc">{{ ad["description"] or "توضیحی ثبت نشده است." }}</div>

<a class="contact" href="https://t.me/{{ telegram[1:] }}" target="_blank">
💬 تماس با فروشنده {{ telegram }}
</a>
</div>
</div>
</div>
</body>
</html>
""", ad=ad, telegram=telegram)


@app.route("/admin")
def lucas_admin():
    user = current_user()

    if not user or user["username"].lower() != "ahmadreza":
        return redirect(url_for("lucas_login", next="/admin"))

    conn = db()

    users_count = conn.execute(
        "SELECT COUNT(*) AS c FROM accounts"
    ).fetchone()["c"]

    ads_count = conn.execute(
        "SELECT COUNT(*) AS c FROM ads"
    ).fetchone()["c"]

    ads = conn.execute("""
        SELECT ads.*, accounts.username AS seller
        FROM ads
        LEFT JOIN accounts ON accounts.id=ads.seller_id
        ORDER BY ads.id DESC
    """).fetchall()

    conn.close()

    return render_template_string("""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>پنل مدیریت — LUCAS SHOP</title>
<style>
body{margin:0;background:#03050a;color:white;font-family:Tahoma,Arial}
.wrap{width:min(1200px,94%);margin:30px auto}
.logo{font-size:28px;font-weight:900;margin-bottom:25px}
.logo span{color:#4d91ff}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-bottom:25px}
.stat{background:#0b1220;border:1px solid #1b3153;border-radius:18px;padding:22px}
.num{font-size:30px;color:#65a1ff;font-weight:900}
.table{overflow:auto;background:#090f1b;border:1px solid #1b3153;border-radius:18px}
table{width:100%;border-collapse:collapse;min-width:700px}
th,td{padding:14px;border-bottom:1px solid #18263d;text-align:right}
th{color:#72a9ff}
a{color:white;text-decoration:none}
.btn{background:#162640;padding:9px 13px;border-radius:10px}
.danger{background:#4a1924}
.top{display:flex;justify-content:space-between;align-items:center}
</style>
</head>
<body>
<div class="wrap">
<div class="top">
<div class="logo">LUCAS <span>SHOP</span> — ADMIN</div>
<a class="btn" href="/">🏠 سایت</a>
</div>

<div class="stats">
<div class="stat">
<div class="num">{{ users_count }}</div>
<div>کاربران</div>
</div>
<div class="stat">
<div class="num">{{ ads_count }}</div>
<div>آگهی‌ها</div>
</div>
</div>

<div class="table">
<table>
<tr>
<th>ID</th>
<th>عنوان</th>
<th>فروشنده</th>
<th>قیمت</th>
<th>TH</th>
<th>BH</th>
<th>عملیات</th>
</tr>
{% for ad in ads %}
<tr>
<td>{{ ad["id"] }}</td>
<td>{{ ad["title"] }}</td>
<td>{{ ad["seller"] or "—" }}</td>
<td>{{ "{:,}".format(ad["price"] or 0) }}</td>
<td>{{ ad["town_hall"] or "—" }}</td>
<td>{{ ad["builder_hall"] or "—" }}</td>
<td>
<a class="btn" href="/ad/{{ ad['id'] }}">مشاهده</a>
<a class="btn danger" href="/admin/delete-ad/{{ ad['id'] }}" onclick="return confirm('حذف شود؟')">حذف</a>
</td>
</tr>
{% endfor %}
</table>
</div>
</div>
</body>
</html>
""", users_count=users_count, ads_count=ads_count, ads=ads)


@app.route("/admin/delete-ad/<int:ad_id>")
def lucas_admin_delete_ad(ad_id):
    user = current_user()

    if not user or user["username"].lower() != "ahmadreza":
        return redirect("/login")

    conn = db()

    row = conn.execute(
        "SELECT image FROM ads WHERE id=?",
        (ad_id,)
    ).fetchone()

    conn.execute(
        "DELETE FROM ads WHERE id=?",
        (ad_id,)
    )

    conn.commit()
    conn.close()

    if row and row["image"]:
        try:
            Path(UPLOAD_DIR, row["image"]).unlink(missing_ok=True)
        except Exception:
            pass

    return redirect("/admin")


@app.route("/explore")
def lucas_explore_full():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "newest")

    conn = db()

    order = "id DESC"

    if sort == "cheap":
        order = "price ASC"
    elif sort == "expensive":
        order = "price DESC"

    if q:
        ads = conn.execute(f"""
            SELECT *
            FROM ads
            WHERE title LIKE ?
               OR description LIKE ?
               OR town_hall LIKE ?
               OR builder_hall LIKE ?
            ORDER BY {order}
        """, (f"%{q}%",f"%{q}%",f"%{q}%",f"%{q}%")).fetchall()
    else:
        ads = conn.execute(f"""
            SELECT *
            FROM ads
            ORDER BY {order}
        """).fetchall()

    conn.close()

    return render_template_string("""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>آگهی‌ها — LUCAS SHOP</title>
<style>
body{margin:0;background:#03050a;color:#fff;font-family:Tahoma,Arial}
.wrap{width:min(1200px,94%);margin:30px auto}
.logo{font-size:28px;font-weight:900;margin-bottom:22px}
.logo span{color:#4d91ff}
.search{display:flex;gap:10px;margin-bottom:20px}
.search input{flex:1;padding:15px;border-radius:13px;border:1px solid #243a5e;background:#0a1220;color:white}
button{padding:15px 20px;border:0;border-radius:13px;background:#347fff;color:white;font-weight:bold}
.sort{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px}
.sort a{color:white;text-decoration:none;background:#101b2e;padding:10px 14px;border-radius:10px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:#09101d;border:1px solid #1a3154;border-radius:20px;overflow:hidden}
.pic{width:100%;height:190px;object-fit:cover;background:#0c1525}
.noimg{height:190px;display:flex;align-items:center;justify-content:center;color:#60708a}
.body{padding:18px}
.title{font-weight:900;font-size:18px}
.price{color:#67a3ff;font-size:20px;font-weight:900;margin:10px 0}
.meta{color:#a1adbf;font-size:13px;line-height:2}
.blue{color:#65a3ff}
.details{display:block;text-align:center;margin-top:14px;background:linear-gradient(135deg,#277aff,#6149ff);padding:12px;border-radius:12px;color:white;text-decoration:none}
@media(max-width:850px){.grid{grid-template-columns:1fr 1fr}}
@media(max-width:550px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo">LUCAS <span>SHOP</span></div>

<form class="search" method="GET">
<input name="q" value="{{ q }}" placeholder="جست‌وجوی اکانت، تاون هال، بیلدر هال...">
<button>🔎 جستجو</button>
</form>

<div class="sort">
<a href="/explore?sort=newest">جدیدترین</a>
<a href="/explore?sort=cheap">ارزان‌ترین</a>
<a href="/explore?sort=expensive">گران‌ترین</a>
<a href="/">🏠 خانه</a>
</div>

<div class="grid">
{% for ad in ads %}
<div class="card">
{% if ad["image"] %}
<img class="pic" src="/uploads/{{ ad['image'] }}">
{% else %}
<div class="noimg">بدون تصویر</div>
{% endif %}
<div class="body">
<div class="title">{{ ad["title"] }}</div>
<div class="price">{{ "{:,}".format(ad["price"] or 0) }} تومان</div>
<div class="meta">
<span class="blue">🏰 TH {{ ad["town_hall"] or "—" }}</span><br>
<span class="blue">🔨 BH {{ ad["builder_hall"] or "—" }}</span><br>
👑 {{ ad["barbarian_king"] or "—" }}
&nbsp; 🏹 {{ ad["archer_queen"] or "—" }}<br>
🧙 {{ ad["grand_warden"] or "—" }}
&nbsp; ⚔️ {{ ad["royal_champion"] or "—" }}
</div>
<a class="details" href="/ad/{{ ad['id'] }}">مشاهده جزئیات</a>
</div>
</div>
{% endfor %}
</div>

{% if not ads %}
<div style="padding:30px;color:#8290a8">
هیچ آگهی‌ای پیدا نشد.
</div>
{% endif %}
</div>
</body>
</html>
""", ads=ads, q=q)


@app.route("/api/ads")
def lucas_ads_api():
    conn = db()
    ads = conn.execute("""
        SELECT id,title,price,image,town_hall,builder_hall,
               barbarian_king,archer_queen,grand_warden,
               royal_champion,telegram,created_at
        FROM ads
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return jsonify([dict(x) for x in ads])


# ===== LUCAS FULL UPGRADE END =====


# ============================================================
# START
# ============================================================

init_db()
lucas_prepare_ads_table()

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("              NOVA DIGITAL PLATFORM")
    print("=" * 60)
    print()
    print("  Local:  http://127.0.0.1:8080")
    print("  Health: http://127.0.0.1:8080/health")
    print()
    print("=" * 60)
    print()

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
