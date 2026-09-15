from flask import render_template_string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, send_from_directory
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



# ===== LUCAS UPLOAD ROUTE =====

@app.route("/uploads/<path:filename>")
def lucas_uploaded_file(filename):

    return send_from_directory(
        UPLOAD_DIR,
        filename
    )


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


@app.route("/create-ad", methods=["GET", "POST"])
def create_ad():

    user = current_user()

    if not user:
        return redirect(url_for("lucas_login", next="/create-ad"))

    lucas_prepare_ads_table()

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()

        town_hall = request.form.get("town_hall", "").strip()
        builder_hall = request.form.get("builder_hall", "").strip()

        barbarian_king = request.form.get(
            "barbarian_king", ""
        ).strip()

        archer_queen = request.form.get(
            "archer_queen", ""
        ).strip()

        grand_warden = request.form.get(
            "grand_warden", ""
        ).strip()

        royal_champion = request.form.get(
            "royal_champion", ""
        ).strip()

        telegram = request.form.get(
            "telegram", ""
        ).strip()

        # -----------------------------
        # validation
        # -----------------------------

        if not title:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>عنوان آگهی را وارد کن.</div>"
                + ad_form()
            )

        if not price:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>قیمت را وارد کن.</div>"
                + ad_form()
            )

        try:
            price_int = int(
                price.replace(",", "")
                     .replace("٬", "")
                     .replace(" ", "")
            )
        except Exception:

            return account_page(
                "ثبت آگهی",
                "<div class='error'>قیمت باید عددی باشد.</div>"
                + ad_form()
            )

        if price_int < 0:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>قیمت نمی‌تواند منفی باشد.</div>"
                + ad_form()
            )

        # -----------------------------
        # image
        # -----------------------------

        image_name = ""

        try:

            photo = request.files.get("image")

            if photo and photo.filename:

                original = secure_filename(
                    photo.filename
                )

                if allowed_file(original):

                    import uuid

                    ext = original.rsplit(
                        ".", 1
                    )[1].lower()

                    image_name = (
                        uuid.uuid4().hex
                        + "."
                        + ext
                    )

                    os.makedirs(
                        UPLOAD_DIR,
                        exist_ok=True
                    )

                    photo.save(
                        os.path.join(
                            UPLOAD_DIR,
                            image_name
                        )
                    )

        except Exception as e:

            print(
                "IMAGE UPLOAD ERROR:",
                repr(e)
            )

            image_name = ""

        # -----------------------------
        # save ad
        # -----------------------------

        conn = db()

        try:

            conn.execute("""
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
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?
                )
            """, (
                user["id"],
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

            conn.commit()

        except Exception as e:

            conn.rollback()

            print(
                "CREATE AD ERROR:",
                repr(e)
            )

            conn.close()

            return account_page(
                "خطا",
                """
                <div class="error">
                هنگام ثبت آگهی خطایی رخ داد.
                </div>

                <div style="margin-top:15px">
                دوباره تلاش کن.
                </div>

                <div style="margin-top:20px">
                <a class="btn" href="/create-ad">
                بازگشت
                </a>
                </div>
                """
            )

        conn.close()

        return redirect("/my-ads")

    return account_page(
        "ثبت آگهی",
        ad_form()
    )



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






# ============================================================
# START
# ============================================================

init_db()
lucas_prepare_ads_table()


# ===== LUCAS EMERGENCY ROUTES FIX =====

from flask import render_template_string

def lucas_create_ad_fixed():
    user = current_user()

    if not user:
        return redirect(url_for("lucas_login", next="/create-ad"))

    lucas_prepare_ads_table()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price_text = request.form.get("price", "0").strip()
        description = request.form.get("description", "").strip()

        town_hall = request.form.get("town_hall", "1")
        builder_hall = request.form.get("builder_hall", "1")

        barbarian_king = request.form.get("barbarian_king", "0")
        archer_queen = request.form.get("archer_queen", "0")
        grand_warden = request.form.get("grand_warden", "0")
        royal_champion = request.form.get("royal_champion", "0")

        telegram = request.form.get(
            "telegram",
            "@LUCAS_SHOP_1"
        ).strip()

        if not title:
            return """
            <div style="background:#050816;color:white;padding:40px;text-align:center">
                <h2>❌ عنوان آگهی را وارد کن</h2>
                <a href="/create-ad">بازگشت</a>
            </div>
            """

        try:
            price = int(
                price_text
                .replace(",", "")
                .replace("٬", "")
                .replace(" ", "")
            )
        except:
            price = 0

        image_name = ""

        uploaded = request.files.get("image")

        if uploaded and uploaded.filename:
            filename = secure_filename(uploaded.filename)

            if filename:
                ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

                if ext in ALLOWED_EXTENSIONS:
                    image_name = (
                        str(int(time.time()))
                        + "_"
                        + secrets.token_hex(5)
                        + "_"
                        + filename
                    )

                    os.makedirs(UPLOAD_DIR, exist_ok=True)

                    uploaded.save(
                        os.path.join(
                            UPLOAD_DIR,
                            image_name
                        )
                    )

        conn = db()

        conn.execute(
            """
            INSERT INTO ads
            (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                title,
                price,
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
            )
        )

        conn.commit()
        conn.close()

        return redirect("/my-ads")

    return render_template_string(
        """
        <!doctype html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="utf-8">
            <meta name="viewport"
                  content="width=device-width,initial-scale=1">

            <title>LUCAS SHOP - ثبت آگهی</title>

            <style>
                *{
                    box-sizing:border-box;
                }

                body{
                    margin:0;
                    background:#050816;
                    color:white;
                    font-family:Arial,sans-serif;
                }

                .container{
                    max-width:850px;
                    margin:30px auto;
                    padding:20px;
                }

                .box{
                    background:#0d1424;
                    border:1px solid #26354d;
                    border-radius:22px;
                    padding:25px;
                }

                h1{
                    color:#3b82f6;
                    margin-top:0;
                }

                input,
                textarea,
                select{
                    width:100%;
                    padding:14px;
                    margin:7px 0 15px;
                    border-radius:11px;
                    border:1px solid #334155;
                    background:#111827;
                    color:white;
                    font-size:15px;
                }

                label{
                    display:block;
                    margin-top:8px;
                    color:#cbd5e1;
                }

                button{
                    width:100%;
                    border:0;
                    border-radius:12px;
                    padding:16px;
                    background:#2563eb;
                    color:white;
                    font-size:17px;
                    font-weight:bold;
                    margin-top:10px;
                }

                a{
                    color:#60a5fa;
                    text-decoration:none;
                }

                .links{
                    margin-top:22px;
                    line-height:2.5;
                }
            </style>
        </head>

        <body>

        <div class="container">

            <div class="box">

                <h1>🛒 ثبت آگهی LUCAS SHOP</h1>

                <p style="color:#94a3b8">
                    مشخصات اکانت Clash of Clans را وارد کن.
                </p>

                <form method="POST"
                      enctype="multipart/form-data">

                    <label>عنوان آگهی</label>
                    <input
                        name="title"
                        placeholder="مثلاً TH18 فول"
                        required
                    >

                    <label>قیمت</label>
                    <input
                        name="price"
                        type="number"
                        placeholder="مثلاً 500000"
                    >

                    <label>Town Hall</label>
                    <select name="town_hall">
                        {% for x in range(1,19) %}
                        <option value="{{x}}">
                            Town Hall {{x}}
                        </option>
                        {% endfor %}
                    </select>

                    <label>Builder Hall</label>
                    <select name="builder_hall">
                        {% for x in range(1,12) %}
                        <option value="{{x}}">
                            Builder Hall {{x}}
                        </option>
                        {% endfor %}
                    </select>

                    <label>Barbarian King</label>
                    <input
                        name="barbarian_king"
                        placeholder="سطح کینگ"
                    >

                    <label>Archer Queen</label>
                    <input
                        name="archer_queen"
                        placeholder="سطح کویین"
                    >

                    <label>Grand Warden</label>
                    <input
                        name="grand_warden"
                        placeholder="سطح واردن"
                    >

                    <label>Royal Champion</label>
                    <input
                        name="royal_champion"
                        placeholder="سطح رویال چمپیون"
                    >

                    <label>آیدی تلگرام</label>
                    <input
                        name="telegram"
                        value="@LUCAS_SHOP_1"
                    >

                    <label>توضیحات</label>
                    <textarea
                        name="description"
                        rows="6"
                        placeholder="توضیحات اکانت..."
                    ></textarea>

                    <label>عکس اکانت</label>
                    <input
                        type="file"
                        name="image"
                        accept=".png,.jpg,.jpeg,.webp,.gif,.svg"
                    >

                    <button type="submit">
                        🚀 ثبت آگهی
                    </button>

                </form>

                <div class="links">
                    <a href="/account">👤 حساب من</a>
                    &nbsp; | &nbsp;
                    <a href="/my-ads">📦 آگهی‌های من</a>
                    &nbsp; | &nbsp;
                    <a href="/explore">🛍 بازار</a>
                </div>

            </div>

        </div>

        </body>
        </html>
        """,
        current_user=user
    )


# مسیر واقعی جدید برای ثبت آگهی
app.add_url_rule(
    "/create-ad-fixed",
    endpoint="lucas_create_ad_fixed",
    view_func=lucas_create_ad_fixed,
    methods=["GET", "POST"]
)

# مهم:
# مسیر قدیمی create_ad را با تابع سالم عوض می‌کنیم
app.view_functions["create_ad"] = lucas_create_ad_fixed


def lucas_my_ads_fixed():

    user = current_user()

    if not user:
        return redirect(url_for("lucas_login", next="/my-ads"))

    lucas_prepare_ads_table()

    conn = db()

    rows = conn.execute(
        """
        SELECT
            id,
            title,
            price,
            description,
            image,
            town_hall,
            builder_hall,
            created_at
        FROM ads
        WHERE seller_id = ?
        ORDER BY id DESC
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    cards = ""

    for ad in rows:

        ad_id = ad["id"]
        title = ad["title"]
        price = ad["price"]
        description = ad["description"] or ""
        image = ad["image"] or ""

        image_html = ""

        if image:
            image_html = f"""
            <img
                src="/uploads/{image}"
                style="
                    width:100%;
                    height:190px;
                    object-fit:cover;
                    border-radius:14px;
                    margin-bottom:12px;
                "
            >
            """

        cards += f"""
        <div style="
            background:#0d1424;
            border:1px solid #26354d;
            border-radius:18px;
            padding:18px;
            margin-bottom:18px;
        ">

            {image_html}

            <h2>{title}</h2>

            <div style="
                color:#60a5fa;
                font-size:21px;
                font-weight:bold;
            ">
                💰 {price:,}
            </div>

            <p style="color:#94a3b8">
                {description}
            </p>

            <a href="/ad/{ad_id}">
                👁 مشاهده آگهی
            </a>

        </div>
        """

    if not cards:
        cards = """
        <div style="
            background:#0d1424;
            padding:35px;
            border-radius:18px;
            text-align:center;
        ">
            <h2>📭 هنوز آگهی نداری</h2>

            <p style="color:#94a3b8">
                اولین آگهی خودت را ثبت کن.
            </p>

            <a href="/create-ad">
                ➕ ثبت آگهی
            </a>
        </div>
        """

    return render_template_string(
        """
        <!doctype html>
        <html lang="fa" dir="rtl">

        <head>
            <meta charset="utf-8">
            <meta name="viewport"
                  content="width=device-width,initial-scale=1">

            <title>LUCAS SHOP - آگهی‌های من</title>

            <style>
                body{
                    margin:0;
                    background:#050816;
                    color:white;
                    font-family:Arial,sans-serif;
                }

                .container{
                    max-width:850px;
                    margin:30px auto;
                    padding:20px;
                }

                a{
                    color:#60a5fa;
                    text-decoration:none;
                }
            </style>
        </head>

        <body>

        <div class="container">

            <h1 style="color:#3b82f6">
                📦 آگهی‌های من
            </h1>

            {{ cards|safe }}

            <div style="
                margin-top:25px;
                line-height:2.5;
            ">
                <a href="/create-ad">
                    ➕ ثبت آگهی جدید
                </a>
                &nbsp; | &nbsp;
                <a href="/account">
                    👤 حساب
                </a>
                &nbsp; | &nbsp;
                <a href="/explore">
                    🛍 بازار
                </a>
            </div>

        </div>

        </body>
        </html>
        """,
        cards=cards
    )


# آگهی‌های من
app.add_url_rule(
    "/my-ads-fixed",
    endpoint="lucas_my_ads_fixed",
    view_func=lucas_my_ads_fixed,
    methods=["GET"]
)

# آدرس اصلی /my-ads را به تابع سالم وصل می‌کنیم
app.view_functions["my_ads"] = lucas_my_ads_fixed if "my_ads" in app.view_functions else lucas_my_ads_fixed

if not any(str(rule) == "/my-ads" for rule in app.url_map.iter_rules()):
    app.add_url_rule(
        "/my-ads",
        endpoint="lucas_my_ads_real",
        view_func=lucas_my_ads_fixed,
        methods=["GET"]
    )


# آپلود تصاویر
def lucas_uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if not any(str(rule) == "/uploads/<path:filename>" for rule in app.url_map.iter_rules()):
    app.add_url_rule(
        "/uploads/<path:filename>",
        endpoint="lucas_uploaded_file",
        view_func=lucas_uploaded_file
    )

print("LUCAS EMERGENCY ROUTES READY")



# ===== REAL LUCAS CREATE AD V2 =====

def lucas_price(value):
    try:
        return f"{int(value):,} تومان"
    except:
        return "0 تومان"


def lucas_save_listing_images():
    result = []

    files = request.files.getlist("images")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    for f in files[:3]:

        if not f or not f.filename:
            continue

        filename = secure_filename(f.filename)

        if not filename:
            continue

        ext = filename.rsplit(".", 1)[-1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            continue

        final_name = (
            str(int(time.time()))
            + "_"
            + secrets.token_hex(5)
            + "_"
            + filename
        )

        f.save(
            os.path.join(
                UPLOAD_DIR,
                final_name
            )
        )

        result.append(final_name)

    while len(result) < 3:
        result.append("")

    return result


def REAL_LUCAS_CREATE_AD():

    user = current_user()

    if not user:
        return redirect(
            url_for(
                "lucas_login",
                next="/create-ad"
            )
        )

    lucas_prepare_ads_table()

    # ==========================================
    # SAVE
    # ==========================================

    if request.method == "POST":

        account_name = request.form.get(
            "account_name", ""
        ).strip()

        player_tag = request.form.get(
            "player_tag", ""
        ).strip()

        supercell_id = request.form.get(
            "supercell_id", ""
        ).strip()

        town_hall = request.form.get(
            "town_hall", "1"
        )

        builder_hall = request.form.get(
            "builder_hall", "1"
        )

        def getint(name):

            try:
                return int(
                    request.form.get(name, "0")
                )
            except:
                return 0

        barbarian_king = getint(
            "barbarian_king"
        )

        archer_queen = getint(
            "archer_queen"
        )

        grand_warden = getint(
            "grand_warden"
        )

        royal_champion = getint(
            "royal_champion"
        )

        try:
            price = int(
                request.form
                .get("price", "0")
                .replace(",", "")
                .replace("٬", "")
                .replace(" ", "")
                .replace("تومان", "")
                .strip()
            )
        except:
            price = 0

        telegram = request.form.get(
            "telegram",
            "@LUCAS_SHOP_1"
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        name_change = request.form.get(
            "name_change",
            "ندارد"
        )

        name_change_gems = request.form.get(
            "name_change_gems",
            "ندارد"
        )

        images = lucas_save_listing_images()

        title = account_name or "اکانت کلش آف کلنز"

        conn = db()

        conn.execute(
            """
            INSERT INTO ads
            (
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
                created_at,
                account_name,
                player_tag,
                supercell_id,
                name_change,
                name_change_gems,
                image2,
                image3
            )
            VALUES
            (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
            """,
            (
                user["id"],
                title,
                price,
                description,
                images[0],
                int(town_hall),
                int(builder_hall),
                barbarian_king,
                archer_queen,
                grand_warden,
                royal_champion,
                telegram,
                int(time.time()),
                account_name,
                player_tag,
                supercell_id,
                name_change,
                name_change_gems,
                images[1],
                images[2]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/my-ads")

    # ==========================================
    # FORM
    # ==========================================

    return render_template_string(
r"""
<!DOCTYPE html>

<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>LUCAS SHOP | ثبت آگهی</title>

<style>

*{
box-sizing:border-box;
}

body{
margin:0;
background:#050816;
color:white;
font-family:Arial,sans-serif;
}

.wrap{
max-width:950px;
margin:auto;
padding:18px;
}

.card{
background:#0d1424;
border:1px solid #26354d;
border-radius:22px;
padding:20px;
margin-bottom:18px;
}

h1{
color:#3b82f6;
}

h2{
color:#60a5fa;
}

label{
display:block;
margin:12px 0 6px;
color:#cbd5e1;
}

input,
textarea{
width:100%;
padding:14px;
border-radius:12px;
border:1px solid #334155;
background:#111827;
color:white;
font-size:15px;
}

textarea{
min-height:130px;
}

.btns{
display:flex;
flex-wrap:wrap;
gap:8px;
}

.pick{
border:1px solid #334155;
background:#111827;
color:#ddd;
padding:11px 15px;
border-radius:10px;
font-weight:bold;
cursor:pointer;
}

.pick.active{
background:#2563eb;
border-color:#60a5fa;
color:white;
}

.grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:12px;
}

@media(max-width:650px){
.grid{
grid-template-columns:1fr;
}
}

.hero{
background:#111827;
border:1px solid #26354d;
border-radius:15px;
padding:14px;
}

.hero h3{
color:#60a5fa;
margin-top:0;
}

.submit{
width:100%;
padding:17px;
border:0;
border-radius:14px;
background:#2563eb;
color:white;
font-size:18px;
font-weight:bold;
margin-top:15px;
}

.note{
color:#94a3b8;
font-size:13px;
}

a{
color:#60a5fa;
text-decoration:none;
}

</style>

</head>

<body>

<div class="wrap">

<form method="POST"
      enctype="multipart/form-data">

<div class="card">

<h1>🛒 ثبت آگهی LUCAS SHOP</h1>

<p class="note">
اطلاعات اکانت را کامل وارد کنید.
</p>

<label>اسم اکانت</label>

<input
name="account_name"
placeholder="مثلاً LUCAS TH18"
required
>

<label>تگ اکانت</label>

<input
name="player_tag"
placeholder="#XXXXXXXX"
>

<label>Supercell ID</label>

<input
name="supercell_id"
placeholder="Supercell ID"
>

</div>


<!-- TH -->

<div class="card">

<h2>🏰 Town Hall</h2>

<div class="btns">

{% for x in range(1,19) %}

<button
type="button"
class="pick {% if x == 1 %}active{% endif %}"
onclick="pick(this,'town_hall','{{x}}')"
>
TH {{x}}
</button>

{% endfor %}

</div>

<input
type="hidden"
id="town_hall"
name="town_hall"
value="1"
>

</div>


<!-- BH -->

<div class="card">

<h2>🔨 Builder Hall</h2>

<div class="btns">

{% for x in range(1,11) %}

<button
type="button"
class="pick {% if x == 1 %}active{% endif %}"
onclick="pick(this,'builder_hall','{{x}}')"
>
BH {{x}}
</button>

{% endfor %}

</div>

<input
type="hidden"
id="builder_hall"
name="builder_hall"
value="1"
>

</div>


<!-- HEROES -->

<div class="card">

<h2>⚔️ هیروها</h2>

<div class="grid">

<div class="hero">

<h3>👑 Barbarian King</h3>

<input
type="number"
name="barbarian_king"
min="0"
max="110"
value="0"
placeholder="Level"
>

</div>


<div class="hero">

<h3>🏹 Archer Queen</h3>

<input
type="number"
name="archer_queen"
min="0"
max="110"
value="0"
placeholder="Level"
>

</div>


<div class="hero">

<h3>🧙 Grand Warden</h3>

<input
type="number"
name="grand_warden"
min="0"
max="80"
value="0"
placeholder="Level"
>

</div>


<div class="hero">

<h3>👸 Royal Champion</h3>

<input
type="number"
name="royal_champion"
min="0"
max="55"
value="0"
placeholder="Level"
>

</div>

</div>

<p class="note">
سطح چهار هیرو را وارد کنید.
</p>

</div>


<!-- NAME -->

<div class="card">

<h2>✏️ تغییر نام</h2>

<div class="btns">

<button
type="button"
class="pick active"
onclick="pick(this,'name_change','ندارد','name')"
>
ندارد
</button>

<button
type="button"
class="pick"
onclick="pick(this,'name_change','دارد','name')"
>
دارد
</button>

</div>

<input
type="hidden"
id="name_change"
name="name_change"
value="ندارد"
>


<h2>💎 تغییر نام با جم</h2>

<div class="btns">

<button
type="button"
class="pick active"
onclick="pick(this,'name_change_gems','ندارد','gems')"
>
ندارد
</button>

<button
type="button"
class="pick"
onclick="pick(this,'name_change_gems','دارد','gems')"
>
دارد
</button>

</div>

<input
type="hidden"
id="name_change_gems"
name="name_change_gems"
value="ندارد"
>

</div>


<!-- PRICE -->

<div class="card">

<h2>💰 قیمت</h2>

<label>قیمت اکانت به تومان</label>

<input
type="text"
name="price"
inputmode="numeric"
placeholder="مثلاً 100000"
required
>

<p class="note">
مثال: 100000 = ۱۰۰٬۰۰۰ تومان
</p>

<label>آیدی تلگرام فروشنده</label>

<input
name="telegram"
value="@LUCAS_SHOP_1"
>

<label>توضیحات</label>

<textarea
name="description"
placeholder="توضیحات اکانت..."
></textarea>

</div>


<!-- IMAGES -->

<div class="card">

<h2>🖼 تصاویر اکانت</h2>

<p class="note">
حداقل ۱ و حداکثر ۳ عکس انتخاب کنید.
</p>

<input
type="file"
name="images"
multiple
accept="image/*"
required
>

</div>


<button
class="submit"
type="submit"
>
🚀 ثبت آگهی
</button>

</form>


<div style="padding:20px;line-height:2.5">

<a href="/account">👤 حساب من</a>
&nbsp; | &nbsp;
<a href="/my-ads">📦 آگهی‌های من</a>
&nbsp; | &nbsp;
<a href="/explore">🛍 بازار</a>

</div>

</div>


<script>

function pick(button,id,value,group){

if(group){

document
.querySelectorAll(
'.pick'
)
.forEach(function(x){

if(
x.getAttribute("onclick") &&
x.getAttribute("onclick")
.includes("'" + group + "'")
){
x.classList.remove("active");
}

});

}else{

let parent=button.parentElement;

parent
.querySelectorAll(".pick")
.forEach(function(x){
x.classList.remove("active");
});

}

button.classList.add("active");

document.getElementById(id).value=value;

}

</script>

</body>
</html>
""",
    )


# -------------------------------------------------
# FORCE OLD ENDPOINT TO NEW FUNCTION
# -------------------------------------------------

app.view_functions["create_ad"] = REAL_LUCAS_CREATE_AD

print("✅ REAL CREATE-AD FUNCTION INSTALLED")

# ============================================================
# LUCAS SHOP - FINAL ACCOUNT FORM
# Supercell buttons + Name Change + Hero buttons + 1-3 images
# ============================================================

import os
import sqlite3
import time
from flask import request, redirect, url_for, session, render_template_string
from werkzeug.utils import secure_filename

LUCAS_HERO_MAX = {
    4:  {"barbarian_king": 1,   "archer_queen": 0,   "grand_warden": 0,  "royal_champion": 0},
    5:  {"barbarian_king": 1,   "archer_queen": 0,   "grand_warden": 0,  "royal_champion": 0},
    6:  {"barbarian_king": 1,   "archer_queen": 0,   "grand_warden": 0,  "royal_champion": 0},
    7:  {"barbarian_king": 10,  "archer_queen": 0,   "grand_warden": 0,  "royal_champion": 0},
    8:  {"barbarian_king": 20,  "archer_queen": 10,  "grand_warden": 0,  "royal_champion": 0},
    9:  {"barbarian_king": 30,  "archer_queen": 30,  "grand_warden": 0,  "royal_champion": 0},
    10: {"barbarian_king": 40,  "archer_queen": 40,  "grand_warden": 0,  "royal_champion": 0},
    11: {"barbarian_king": 50,  "archer_queen": 50,  "grand_warden": 20,  "royal_champion": 0},
    12: {"barbarian_king": 65,  "archer_queen": 65,  "grand_warden": 40,  "royal_champion": 0},
    13: {"barbarian_king": 75,  "archer_queen": 75,  "grand_warden": 50,  "royal_champion": 25},
    14: {"barbarian_king": 85,  "archer_queen": 85,  "grand_warden": 60,  "royal_champion": 30},
    15: {"barbarian_king": 90,  "archer_queen": 90,  "grand_warden": 65,  "royal_champion": 40},
    16: {"barbarian_king": 95,  "archer_queen": 95,  "grand_warden": 70,  "royal_champion": 45},
    17: {"barbarian_king": 100, "archer_queen": 100, "grand_warden": 75,  "royal_champion": 50},
    18: {"barbarian_king": 110, "archer_queen": 110, "grand_warden": 85,  "royal_champion": 55},
}

def lucas_form_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def lucas_add_column_if_missing(conn, table, column, definition):
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

def lucas_prepare_final_ads():
    conn = lucas_form_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            title TEXT,
            price INTEGER DEFAULT 0,
            description TEXT,
            image TEXT,
            town_hall INTEGER,
            builder_hall INTEGER,
            barbarian_king INTEGER,
            archer_queen INTEGER,
            grand_warden INTEGER,
            royal_champion INTEGER,
            telegram TEXT,
            created_at INTEGER
        )
    """)

    columns = {
        "account_name": "TEXT",
        "player_tag": "TEXT",
        "supercell_id": "TEXT",
        "supercell_status": "TEXT",
        "name_change": "TEXT",
        "name_change_gems": "TEXT",
        "image2": "TEXT",
        "image3": "TEXT"
    }

    for col, definition in columns.items():
        lucas_add_column_if_missing(conn, "ads", col, definition)

    conn.commit()
    conn.close()

lucas_prepare_final_ads()


def lucas_final_create_ad():
    if "user_id" not in session:
        return redirect(url_for("lucas_login"))

    conn = lucas_form_db()

    account = conn.execute(
        "SELECT id, username FROM accounts WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    if not account:
        conn.close()
        session.clear()
        return redirect(url_for("lucas_login"))

    error = ""

    if request.method == "POST":

        account_name = request.form.get("account_name", "").strip()
        player_tag = request.form.get("player_tag", "").strip()
        supercell_status = request.form.get("supercell_status", "").strip()

        town_hall_raw = request.form.get("town_hall", "").strip()
        builder_hall_raw = request.form.get("builder_hall", "").strip()

        barbarian_king_raw = request.form.get("barbarian_king", "").strip()
        archer_queen_raw = request.form.get("archer_queen", "").strip()
        grand_warden_raw = request.form.get("grand_warden", "").strip()
        royal_champion_raw = request.form.get("royal_champion", "").strip()

        name_change = request.form.get("name_change", "").strip()
        name_change_gems = request.form.get("name_change_gems", "").strip()

        price_raw = request.form.get("price", "").strip()
        telegram = request.form.get("telegram", "").strip()
        description = request.form.get("description", "").strip()

        images = request.files.getlist("images")

        # ---------------------------
        # Basic validation
        # ---------------------------
        if not account_name:
            error = "نام اکانت را وارد کنید."

        elif not town_hall_raw:
            error = "تاون هال را انتخاب کنید."

        elif not builder_hall_raw:
            error = "بیلدر هال را انتخاب کنید."

        elif not supercell_status:
            error = "وضعیت اتصال سوپرسل را انتخاب کنید."

        elif not name_change:
            error = "وضعیت تغییر نام را انتخاب کنید."

        elif name_change == "با جم" and not name_change_gems:
            error = "مقدار جم تغییر نام را انتخاب کنید."

        elif not price_raw:
            error = "قیمت را وارد کنید."

        elif len(images) < 1:
            error = "حداقل یک عکس برای آگهی لازم است."

        elif len(images) > 3:
            error = "حداکثر ۳ عکس می‌توانید انتخاب کنید."

        # ---------------------------
        # Numeric validation
        # ---------------------------
        try:
            town_hall = int(town_hall_raw)
            builder_hall = int(builder_hall_raw)
            barbarian_king = int(barbarian_king_raw or 0)
            archer_queen = int(archer_queen_raw or 0)
            grand_warden = int(grand_warden_raw or 0)
            royal_champion = int(royal_champion_raw or 0)
            price = int(price_raw.replace(",", "").replace("٬", ""))
        except:
            error = "یکی از مقادیر واردشده صحیح نیست."
            town_hall = builder_hall = 0
            barbarian_king = archer_queen = grand_warden = royal_champion = 0
            price = 0

        # ---------------------------
        # TH / BH limits
        # ---------------------------
        if not error:
            if town_hall < 1 or town_hall > 18:
                error = "تاون هال باید بین ۱ تا ۱۸ باشد."

            elif builder_hall < 1 or builder_hall > 10:
                error = "بیلدر هال باید بین ۱ تا ۱۰ باشد."

        # ---------------------------
        # Correct hero limits
        # ---------------------------
        if not error and town_hall in LUCAS_HERO_MAX:
            mx = LUCAS_HERO_MAX[town_hall]

            if barbarian_king > mx["barbarian_king"]:
                error = f"حداکثر لول کینگ در TH{town_hall} برابر {mx['barbarian_king']} است."

            elif archer_queen > mx["archer_queen"]:
                error = f"حداکثر لول کویین در TH{town_hall} برابر {mx['archer_queen']} است."

            elif grand_warden > mx["grand_warden"]:
                error = f"حداکثر لول واردن در TH{town_hall} برابر {mx['grand_warden']} است."

            elif royal_champion > mx["royal_champion"]:
                error = f"حداکثر لول رویال چمپیون در TH{town_hall} برابر {mx['royal_champion']} است."

        # ---------------------------
        # Name change validation
        # ---------------------------
        if not error and name_change == "رایگان":
            name_change_gems = ""

        if not error and name_change == "با جم":
            allowed_gems = {
                "500",
                "1000",
                "1500",
                "2000",
                "2500",
                "3000",
                "3500",
                "3500 و بیشتر"
            }

            if name_change_gems not in allowed_gems:
                error = "مقدار جم انتخاب‌شده معتبر نیست."

        # ---------------------------
        # Price
        # ---------------------------
        if not error and price < 0:
            error = "قیمت نمی‌تواند منفی باشد."

        # ---------------------------
        # Save images
        # ---------------------------
        saved_images = []

        if not error:

            os.makedirs(UPLOAD_DIR, exist_ok=True)

            allowed = {
                "png",
                "jpg",
                "jpeg",
                "webp",
                "gif"
            }

            for img in images[:3]:

                if not img or not img.filename:
                    continue

                original = secure_filename(img.filename)

                if "." not in original:
                    continue

                ext = original.rsplit(".", 1)[1].lower()

                if ext not in allowed:
                    error = "فرمت عکس مجاز نیست."
                    break

                filename = (
                    str(int(time.time() * 1000000))
                    + "_"
                    + str(len(saved_images) + 1)
                    + "."
                    + ext
                )

                img.save(os.path.join(UPLOAD_DIR, filename))
                saved_images.append(filename)

            if len(saved_images) < 1 and not error:
                error = "حداقل یک عکس معتبر انتخاب کنید."

        if not error:

            image1 = saved_images[0] if len(saved_images) > 0 else ""
            image2 = saved_images[1] if len(saved_images) > 1 else ""
            image3 = saved_images[2] if len(saved_images) > 2 else ""

            title = account_name

            conn.execute("""
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
                    created_at,
                    account_name,
                    player_tag,
                    supercell_id,
                    supercell_status,
                    name_change,
                    name_change_gems,
                    image2,
                    image3
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account["id"],
                title,
                price,
                description,
                image1,
                town_hall,
                builder_hall,
                barbarian_king,
                archer_queen,
                grand_warden,
                royal_champion,
                telegram,
                int(time.time()),
                account_name,
                player_tag,
                "",
                supercell_status,
                name_change,
                name_change_gems,
                image2,
                image3
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("lucas_my_ads"))

    conn.close()

    # ------------------------------------------------------------
    # FORM HTML
    # ------------------------------------------------------------
    html = """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>ثبت آگهی | LUCAS SHOP</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    background:#070a10;
    color:#fff;
    font-family:Tahoma,Arial,sans-serif;
}

.container{
    width:min(900px,94%);
    margin:25px auto 60px;
}

.card{
    background:#101621;
    border:1px solid #202b3b;
    border-radius:22px;
    padding:22px;
    box-shadow:0 15px 50px rgba(0,0,0,.35);
}

h1{
    margin:0 0 8px;
    text-align:center;
    font-size:25px;
}

.sub{
    text-align:center;
    color:#8e9aae;
    margin-bottom:25px;
}

.section{
    margin-top:25px;
}

.section-title{
    font-size:18px;
    font-weight:bold;
    margin-bottom:12px;
}

label{
    display:block;
    margin:14px 0 7px;
    color:#c9d2df;
}

input[type=text],
input[type=number],
textarea{
    width:100%;
    border:1px solid #293548;
    background:#080d15;
    color:#fff;
    border-radius:13px;
    padding:13px;
    outline:none;
    font-size:15px;
}

textarea{
    min-height:110px;
    resize:vertical;
}

input:focus,
textarea:focus{
    border-color:#2388ff;
}

.buttons{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(80px,1fr));
    gap:8px;
}

.choice{
    position:relative;
}

.choice input{
    position:absolute;
    opacity:0;
    pointer-events:none;
}

.choice span{
    display:block;
    padding:12px 8px;
    text-align:center;
    border:1px solid #2a374b;
    border-radius:12px;
    background:#0b111b;
    cursor:pointer;
    transition:.15s;
}

.choice input:checked + span{
    background:#087cff;
    border-color:#087cff;
    color:#fff;
    box-shadow:0 0 18px rgba(8,124,255,.25);
}

.blue{
    color:#4da3ff;
}

.hero-box{
    background:#0b111b;
    border:1px solid #202c3d;
    border-radius:16px;
    padding:14px;
    margin-top:12px;
}

.hero-name{
    font-weight:bold;
    margin-bottom:10px;
}

.hero-buttons{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(55px,1fr));
    gap:6px;
}

.hero-buttons label span{
    padding:9px 4px;
    font-size:13px;
}

.hero-unavailable{
    color:#8793a6;
    background:#090e16;
    border:1px solid #222d3d;
    padding:10px;
    border-radius:10px;
    text-align:center;
}

.hidden{
    display:none;
}

.gem-box{
    margin-top:12px;
    padding:14px;
    background:#0b111b;
    border:1px solid #28374a;
    border-radius:15px;
}

.file-box{
    border:1px dashed #3a4c64;
    padding:16px;
    border-radius:15px;
    background:#0b111b;
}

.file-box small{
    display:block;
    color:#8995a8;
    margin-top:8px;
}

.error{
    background:#3b1117;
    border:1px solid #8d2635;
    color:#ffb9c1;
    padding:13px;
    border-radius:13px;
    margin-bottom:18px;
}

.submit{
    width:100%;
    border:0;
    border-radius:15px;
    padding:16px;
    margin-top:25px;
    background:#087cff;
    color:#fff;
    font-size:17px;
    font-weight:bold;
    cursor:pointer;
}

.submit:hover{
    background:#006ce6;
}

.back{
    display:block;
    text-align:center;
    color:#8ea0b8;
    margin-top:16px;
    text-decoration:none;
}

.hint{
    color:#8491a4;
    font-size:12px;
    margin-top:7px;
}

.price-preview{
    color:#48a1ff;
    margin-top:7px;
    font-size:13px;
}

</style>
</head>

<body>

<div class="container">

<div class="card">

<h1>🛒 ثبت آگهی اکانت</h1>
<div class="sub">LUCAS SHOP</div>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="POST" enctype="multipart/form-data">

<div class="section">

<div class="section-title">📷 تصاویر اکانت</div>

<div class="file-box">

<input
    type="file"
    name="images"
    accept="image/png,image/jpeg,image/webp,image/gif"
    multiple
    required
    id="images"
>

<small>
حداقل ۱ و حداکثر ۳ عکس — می‌توانید هر سه عکس را همزمان انتخاب کنید.
</small>

</div>

</div>


<div class="section">

<div class="section-title">👤 اطلاعات اکانت</div>

<label>نام اکانت</label>
<input
    type="text"
    name="account_name"
    placeholder="مثلاً LUCAS"
    value="{{ request.form.get('account_name','') }}"
    required
>

<label>Player Tag</label>
<input
    type="text"
    name="player_tag"
    placeholder="#XXXXXXXX"
    value="{{ request.form.get('player_tag','') }}"
>


<label>Supercell ID</label>

<div class="buttons">

<label class="choice">
<input
    type="radio"
    name="supercell_status"
    value="متصل"
    {% if request.form.get('supercell_status') == 'متصل' %}checked{% endif %}
>
<span>🟢 متصل</span>
</label>

<label class="choice">
<input
    type="radio"
    name="supercell_status"
    value="متصل نیست"
    {% if request.form.get('supercell_status') == 'متصل نیست' %}checked{% endif %}
>
<span>🔴 متصل نیست</span>
</label>

</div>

</div>


<div class="section">

<div class="section-title">🏰 تاون هال</div>

<div class="buttons">

{% for n in range(1,19) %}

<label class="choice">
<input
    type="radio"
    name="town_hall"
    value="{{ n }}"
    {% if request.form.get('town_hall') == n|string %}checked{% endif %}
    onchange="updateHeroes({{ n }})"
>
<span>TH {{ n }}</span>
</label>

{% endfor %}

</div>

</div>


<div class="section">

<div class="section-title">🔨 بیلدر هال</div>

<div class="buttons">

{% for n in range(1,11) %}

<label class="choice">
<input
    type="radio"
    name="builder_hall"
    value="{{ n }}"
    {% if request.form.get('builder_hall') == n|string %}checked{% endif %}
>
<span>BH {{ n }}</span>
</label>

{% endfor %}

</div>

</div>


<div class="section">

<div class="section-title">🦸 هیروها</div>

<div class="hint">
با انتخاب TH، حداکثر لول مجاز هر هیرو به صورت خودکار نمایش داده می‌شود.
</div>


<div class="hero-box">

<div class="hero-name">👑 Barbarian King</div>

<div id="bk_buttons" class="hero-buttons"></div>

<input
    type="hidden"
    name="barbarian_king"
    id="bk_value"
    value="{{ request.form.get('barbarian_king','0') }}"
>

</div>


<div class="hero-box">

<div class="hero-name">🏹 Archer Queen</div>

<div id="aq_buttons" class="hero-buttons"></div>

<input
    type="hidden"
    name="archer_queen"
    id="aq_value"
    value="{{ request.form.get('archer_queen','0') }}"
>

</div>


<div class="hero-box">

<div class="hero-name">🧙 Grand Warden</div>

<div id="gw_buttons" class="hero-buttons"></div>

<input
    type="hidden"
    name="grand_warden"
    id="gw_value"
    value="{{ request.form.get('grand_warden','0') }}"
>

</div>


<div class="hero-box">

<div class="hero-name">⚔️ Royal Champion</div>

<div id="rc_buttons" class="hero-buttons"></div>

<input
    type="hidden"
    name="royal_champion"
    id="rc_value"
    value="{{ request.form.get('royal_champion','0') }}"
>

</div>

</div>


<div class="section">

<div class="section-title">✏️ تغییر نام</div>

<div class="buttons">

<label class="choice">
<input
    type="radio"
    name="name_change"
    value="رایگان"
    onclick="showGems(false)"
    {% if request.form.get('name_change') == 'رایگان' %}checked{% endif %}
>
<span>🆓 رایگان</span>
</label>

<label class="choice">
<input
    type="radio"
    name="name_change"
    value="با جم"
    onclick="showGems(true)"
    {% if request.form.get('name_change') == 'با جم' %}checked{% endif %}
>
<span>💎 با جم</span>
</label>

</div>


<div
    id="gemBox"
    class="gem-box {% if request.form.get('name_change') != 'با جم' %}hidden{% endif %}"
>

<div class="hero-name">💎 مقدار جم تغییر نام</div>

<div class="buttons">

{% for g in ['500','1000','1500','2000','2500','3000','3500','3500 و بیشتر'] %}

<label class="choice">

<input
    type="radio"
    name="name_change_gems"
    value="{{ g }}"
    {% if request.form.get('name_change_gems') == g %}checked{% endif %}
>

<span>{{ g }}</span>

</label>

{% endfor %}

</div>

</div>

</div>


<div class="section">

<div class="section-title">💰 قیمت (تومان)</div>

<input
    type="number"
    name="price"
    id="price"
    min="0"
    placeholder="مثلاً 100"
    value="{{ request.form.get('price','') }}"
    required
>

<div class="price-preview" id="pricePreview"></div>

</div>


<div class="section">

<div class="section-title">📱 تلگرام</div>

<input
    type="text"
    name="telegram"
    placeholder="@username"
    value="{{ request.form.get('telegram','') }}"
>

</div>


<div class="section">

<div class="section-title">📝 توضیحات</div>

<textarea
    name="description"
    placeholder="توضیحات اکانت را بنویسید..."
>{{ request.form.get('description','') }}</textarea>

</div>


<button class="submit" type="submit">
🚀 ثبت آگهی
</button>

</form>

<a class="back" href="{{ url_for('lucas_account_dashboard') }}">
بازگشت به حساب کاربری
</a>

</div>
</div>


<script>

const HERO_MAX = {
    4:  {bk:1,   aq:0,   gw:0,  rc:0},
    5:  {bk:1,   aq:0,   gw:0,  rc:0},
    6:  {bk:1,   aq:0,   gw:0,  rc:0},
    7:  {bk:10,  aq:0,   gw:0,  rc:0},
    8:  {bk:20,  aq:10,  gw:0,  rc:0},
    9:  {bk:30,  aq:30,  gw:0,  rc:0},
    10: {bk:40,  aq:40,  gw:0,  rc:0},
    11: {bk:50,  aq:50,  gw:20, rc:0},
    12: {bk:65,  aq:65,  gw:40, rc:0},
    13: {bk:75,  aq:75,  gw:50, rc:25},
    14: {bk:85,  aq:85,  gw:60, rc:30},
    15: {bk:90,  aq:90, gw:65, rc:40},
    16: {bk:95,  aq:95, gw:70, rc:45},
    17: {bk:100,aq:100,gw:75, rc:50},
    18: {bk:110,aq:110,gw:85, rc:55}
};


function makeHeroButtons(containerId, inputId, max){

    const box = document.getElementById(containerId);
    const input = document.getElementById(inputId);

    box.innerHTML = "";

    if(max <= 0){

        box.innerHTML =
            '<div class="hero-unavailable">🔒 این هیرو در این TH فعال نیست</div>';

        input.value = "0";
        return;
    }

    let current = parseInt(input.value || "0");

    if(current > max){
        current = max;
        input.value = max;
    }

    for(let i=1; i<=max; i++){

        const label = document.createElement("label");
        label.className = "choice";

        const radio = document.createElement("input");

        radio.type = "radio";
        radio.name = containerId + "_radio";
        radio.value = i;

        if(i === current){
            radio.checked = true;
        }

        radio.onchange = function(){
            input.value = this.value;
        };

        const span = document.createElement("span");
        span.textContent = i;

        label.appendChild(radio);
        label.appendChild(span);

        box.appendChild(label);
    }

}


function updateHeroes(th){

    const h = HERO_MAX[th];

    makeHeroButtons("bk_buttons","bk_value",h.bk);
    makeHeroButtons("aq_buttons","aq_value",h.aq);
    makeHeroButtons("gw_buttons","gw_value",h.gw);
    makeHeroButtons("rc_buttons","rc_value",h.rc);

}


function showGems(show){

    const box = document.getElementById("gemBox");

    if(show){
        box.classList.remove("hidden");
    }else{
        box.classList.add("hidden");

        document
            .querySelectorAll('input[name="name_change_gems"]')
            .forEach(x => x.checked = false);
    }

}


function formatToman(value){

    if(!value){
        return "";
    }

    return Number(value).toLocaleString("fa-IR") + " تومان";
}


document.getElementById("price").addEventListener("input", function(){

    document.getElementById("pricePreview").textContent =
        formatToman(this.value);

});


window.addEventListener("load", function(){

    const selected =
        document.querySelector('input[name="town_hall"]:checked');

    updateHeroes(
        selected ? parseInt(selected.value) : 18
    );

    const price =
        document.getElementById("price").value;

    document.getElementById("pricePreview").textContent =
        formatToman(price);

});

</script>

</body>
</html>
"""

    return render_template_string(
        html,
        error=error
    )


# ============================================================
# Force every /create-ad route to use the new form
# ============================================================

for _rule in list(app.url_map.iter_rules()):
    if _rule.rule == "/create-ad":
        app.view_functions[_rule.endpoint] = lucas_final_create_ad

# اگر endpoint جدیدی هم وجود داشته باشد
app.add_url_rule(
    "/create-ad-final",
    endpoint="lucas_create_ad_final",
    view_func=lucas_final_create_ad,
    methods=["GET", "POST"]
)

print("✅ LUCAS SHOP FINAL ACCOUNT FORM LOADED")
print("✅ Supercell buttons: ON")
print("✅ Name Change + Gems: ON")
print("✅ Hero buttons + correct TH limits: ON")
print("✅ Images 1-3: ON")

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

