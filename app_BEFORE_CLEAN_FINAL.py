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



# LUCAS_PUBLIC_AD_ROUTE_FIXED
@app.route("/ad/<code>", methods=["GET"])
def lucas_public_ad_fixed(code):

    c=lucas_ad_management_db()

    ad=c.execute(
        "SELECT * FROM ads WHERE listing_code=?",
        (code,)
    ).fetchone()

    c.close()

    if not ad:
        return "آگهی پیدا نشد",404

    def val(x):
        return x if x not in (None,"") else "—"

    images=[]
    for col in ("image1","image2","image3","image","image2","image3"):
        try:
            v=ad[col]
        except:
            v=""
        if v and v not in images:
            images.append(v)

    html="""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LUCAS SHOP | آگهی {{ public_code }}</title>

<style>
*{box-sizing:border-box}
body{
margin:0;
background:#050912;
color:#fff;
font-family:Tahoma,Arial,sans-serif;
}
.wrap{
max-width:850px;
margin:auto;
padding:20px 12px 50px;
}
.card{
background:#0a111e;
border:1px solid #1d3150;
border-radius:22px;
overflow:hidden;
box-shadow:0 15px 50px #0008;
}
.top{
padding:17px;
border-bottom:1px solid #1d3150;
font-size:20px;
font-weight:900;
}
.code{
float:left;
color:#60a5fa;
}
.content{
padding:15px;
}
.gallery{
background:#050912;
border-radius:16px;
overflow:hidden;
}
.main{
width:100%;
height:400px;
object-fit:contain;
display:block;
}
.thumbs{
display:flex;
gap:8px;
padding:10px;
overflow:auto;
}
.thumb{
width:75px;
height:60px;
object-fit:cover;
border-radius:9px;
border:2px solid #24324a;
cursor:pointer;
}
.info{
margin-top:15px;
}
.row{
display:flex;
justify-content:space-between;
gap:15px;
padding:13px;
margin-bottom:7px;
background:#0e1727;
border:1px solid #1a2940;
border-radius:11px;
}
.label{color:#94a3b8}
.value{font-weight:800}
.blue{color:#60a5fa}
.green{color:#4ade80}
.red{color:#f87171}
.price{
font-size:19px;
}
.description{
margin-top:10px;
padding:15px;
line-height:2;
background:#0e1727;
border-radius:12px;
color:#dbeafe;
}
.back{
display:block;
margin-top:15px;
padding:13px;
text-align:center;
background:#2563eb;
border-radius:12px;
font-weight:900;
}
@media(max-width:600px){
.main{height:280px}
.row{font-size:13px}
}
</style>
</head>

<body>
<div class="wrap">
<div class="card">

<div class="top">
🛒 LUCAS SHOP
<span class="code">{{ public_code }}</span>
<div style="clear:both"></div>
</div>

<div class="content">

<div class="gallery">

{% if images %}
<img id="mainImage" class="main" src="/uploads/{{ images[0] }}">

<div class="thumbs">
{% for img in images %}
<img class="thumb"
src="/uploads/{{ img }}"
onclick="document.getElementById('mainImage').src=this.src">
{% endfor %}
</div>

{% else %}
<div style="padding:80px;text-align:center;color:#64748b">
تصویر ندارد
</div>
{% endif %}

</div>

<div class="info">

<div class="row">
<div class="label">کد آگهی</div>
<div class="value blue">{{ public_code }}</div>
</div>

<div class="row">
<div class="label">نام اکانت</div>
<div class="value">{{ val(ad['account_name']) }}</div>
</div>

<div class="row">
<div class="label">تاون هال</div>
<div class="value blue">TH {{ val(ad['townhall']) }}</div>
</div>

<div class="row">
<div class="label">بیلدر هال</div>
<div class="value blue">BH {{ val(ad['builderhall']) }}</div>
</div>

<div class="row">
<div class="label">کینگ بربر</div>
<div class="value">{{ val(ad['barbarian_king']) }}</div>
</div>

<div class="row">
<div class="label">آرچر کویین</div>
<div class="value">{{ val(ad['archer_queen']) }}</div>
</div>

<div class="row">
<div class="label">گرند واردن</div>
<div class="value">{{ val(ad['grand_warden']) }}</div>
</div>

<div class="row">
<div class="label">هیروی سلطنتی</div>
<div class="value">{{ val(ad['royal_champion']) }}</div>
</div>

<div class="row">
<div class="label">تغییر نام</div>
<div class="value">{{ val(ad['name_change']) }}</div>
</div>

<div class="row">
<div class="label">Supercell ID</div>
<div class="value">
{{ val(ad['supercell_id']) }}
</div>
</div>

<div class="row price">
<div class="label">قیمت</div>
<div class="value blue">{{ ad['price'] }} تومان</div>
</div>

{% if ad['description'] %}
<div class="description">
{{ ad['description'] }}
</div>
{% endif %}

</div>

<a class="back" href="/explore">← برگشت به آگهی‌ها</a>

</div>
</div>
</div>

</body>
</html>
"""

    public_code="#"+str(ad["ad_number"])

    return render_template_string(
        html,
        ad=ad,
        images=images,
        public_code=public_code,
        val=val
    )

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

        # محصولات عادی سایت
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

        products = list(rows)

        # آگهی‌های تأییدشده LUCAS SHOP
        try:
            ad_rows = conn.execute("""
                SELECT *
                FROM ads
                WHERE approved = 1
                ORDER BY id DESC
            """).fetchall()

            for ad in ad_rows:
                products.append({
                    "id": ad["id"],
                    "title": ad["account_name"] or ad["title"] or "اکانت کلش آف کلنز",
                    "description": ad["description"] or "",
                    "price": ad["price"],
                    "image": ad["image"],
                    "category": "Clash of Clans",
                    "created_at": ad["created_at"],
                    "listing_code": ad["listing_code"],
                    "is_ad": 1
                })

        except Exception as e:
            print("ADS MARKET ERROR:", e)

        conn.close()

    except Exception as e:
        print("EXPLORE ERROR:", e)
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

        # محدودیت قطعی عکس: حداقل ۱ و حداکثر ۳
        if len(images) < 1:
            error = "حداقل یک عکس برای آگهی لازم است."

        elif len(images) > 3:
            error = "حداکثر ۳ عکس می‌توانید برای آگهی انتخاب کنید."

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

            return redirect(url_for("lucas_my_ads_real"))

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
    onchange="checkImageCount(this)"
>

<small>
حداقل ۱ و حداکثر ۳ عکس — بیشتر از ۳ عکس قابل انتخاب نیست.
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
    placeholder="مثلاً 100,000 تومان"
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


function checkImageCount(input){

    if(input.files.length > 3){

        alert("حداکثر ۳ عکس می‌توانید انتخاب کنید.");

        input.value = "";

        return false;
    }

    if(input.files.length < 1){

        return false;
    }

    return true;
}


function formatToman(value){

    if(!value){
        return "";
    }

    let number = Number(
        String(value)
        .replace(/,/g,"")
        .replace(/٬/g,"")
        .replace(/تومان/g,"")
        .trim()
    );

    if(isNaN(number)){
        return "";
    }

    return number.toLocaleString("en-US") + " تومان";
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


# ============================================================
# LUCAS_AD_MANAGEMENT_V1
# کد آگهی + نمایش + ویرایش + حذف
# ============================================================

def lucas_ad_management_db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def lucas_prepare_ad_management():

    c = lucas_ad_management_db()

    c.execute("""
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

    cols = {
        "listing_code": "TEXT",
        "account_name": "TEXT",
        "player_tag": "TEXT",
        "supercell_status": "TEXT",
        "name_change": "TEXT",
        "name_change_gems": "TEXT",
        "image2": "TEXT",
        "image3": "TEXT"
    }

    existing = [
        x[1] for x in c.execute("PRAGMA table_info(ads)").fetchall()
    ]

    for col, definition in cols.items():
        if col not in existing:
            c.execute(
                f"ALTER TABLE ads ADD COLUMN {col} {definition}"
            )

    # برای آگهی‌های قدیمی هم کد بساز
    rows = c.execute("""
        SELECT id FROM ads
        WHERE listing_code IS NULL OR listing_code=''
        ORDER BY id
    """).fetchall()

    for r in rows:
        code = f"LS-{int(r['id']):04d}"
        c.execute(
            "UPDATE ads SET listing_code=? WHERE id=?",
            (code, r["id"])
        )

    c.commit()
    c.close()


lucas_prepare_ad_management()



# ============================================================
# PUBLIC AD NUMBER
# ============================================================

def lucas_public_number(ad):

    try:
        c = lucas_ad_management_db()

        rows = c.execute("""
            SELECT id
            FROM ads
            ORDER BY id ASC
        """).fetchall()

        c.close()

        for i, row in enumerate(rows, 1):
            if int(row["id"]) == int(ad["id"]):
                return i

    except:
        pass

    return ad["id"]


def lucas_fill_missing_ad_codes():

    try:
        c = lucas_ad_management_db()

        rows = c.execute("""
            SELECT id
            FROM ads
            ORDER BY id ASC
        """).fetchall()

        for index, row in enumerate(rows, 1):
            code = f"#{index}"

            c.execute("""
                UPDATE ads
                SET listing_code=?
                WHERE id=?
            """, (code, row["id"]))

        c.commit()
        c.close()

    except Exception:
        pass


@app.before_request
def lucas_auto_ad_codes():
    lucas_fill_missing_ad_codes()




# =========================
# LUCAS SHOP ADMIN PANEL
# =========================
@app.route("/admin", methods=["GET"])
def lucas_admin_panel():
    if not lucas_is_admin():
        return redirect(url_for("lucas_login"))

    return redirect("/manage-ads")


def lucas_is_admin():

    try:
        if not session.get("user_id"):
            return False

        c = lucas_ad_management_db()

        row = c.execute(
            "SELECT username FROM accounts WHERE id=?",
            (session.get("user_id"),)
        ).fetchone()

        c.close()

        return bool(
            row and str(row["username"]).lower() == "ahmadreza"
        )

    except Exception:
        return False


def lucas_current_user_id():
    return session.get("user_id")


def lucas_ad_allowed(ad):

    uid = lucas_current_user_id()

    if not uid:
        return False

    if lucas_is_admin():
        return True

    return str(ad["seller_id"]) == str(uid)


def lucas_toman(value):

    try:
        return f"{int(value):,} تومان"
    except:
        return "0 تومان"


# ============================================================
# نمایش آگهی با ظاهر نزدیک به قالب ارسال‌شده
# ============================================================

def lucas_ad_view(code):

    lucas_fill_missing_ad_codes()

    c = lucas_ad_management_db()

    ad = c.execute("""
        SELECT * FROM ads
        WHERE listing_code=?
    """, (code,)).fetchone()

    c.close()

    if not ad:
        return "آگهی پیدا نشد", 404

    images = []

    for col in ["image", "image2", "image3"]:

        value = ad[col] if col in ad.keys() else ""

        if value:
            images.append("/uploads/" + value)

    if not images:
        images = [""]

    def val(x):
        return x if x not in (None, "") else "—"

    html = """
<!doctype html>
<html lang="fa" dir="rtl">

<head>

<meta charset="utf-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>{{ ad['listing_code'] }} | LUCAS SHOP</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    background:#050810;
    color:#fff;
    font-family:Tahoma,Arial,sans-serif;
}

.wrap{
    width:min(1100px,95%);
    margin:25px auto;
}

.ad-card{
    background:#070d18;
    border:2px solid #1685ff;
    border-radius:24px;
    overflow:hidden;
    box-shadow:
        0 0 25px rgba(0,120,255,.22),
        inset 0 0 30px rgba(0,80,180,.08);
}

.top{
    padding:15px 20px;
    text-align:center;
    border-bottom:1px solid #173a62;
    font-size:23px;
    font-weight:bold;
}

.code{
    color:#48a8ff;
}

.content{
    display:grid;
    grid-template-columns:1.15fr 1fr;
    gap:15px;
    padding:15px;
}

.gallery{
    min-height:520px;
    background:#02060d;
    border:1px solid #1769b5;
    border-radius:18px;
    padding:10px;
    display:flex;
    align-items:center;
    justify-content:center;
}

.main-image{
    width:100%;
    height:500px;
    object-fit:contain;
    border-radius:13px;
}

.no-image{
    color:#65758d;
    font-size:20px;
}

.main-photo-wrap{
    width:100%;
    display:flex;
    align-items:center;
    justify-content:center;
}

.thumbs{
    width:100%;
    display:flex;
    justify-content:center;
    gap:9px;
    flex-wrap:wrap;
    margin-top:10px;
}

.thumb{
    width:78px;
    height:62px;
    padding:2px;
    border-radius:10px;
    border:2px solid #25405f;
    background:#07101d;
    cursor:pointer;
}

.thumb img{
    width:100%;
    height:100%;
    object-fit:cover;
    border-radius:7px;
}

.thumb.active{
    border-color:#1685ff;
    box-shadow:0 0 10px rgba(22,133,255,.45);
}

.info{
    display:flex;
    flex-direction:column;
    gap:8px;
}

.row{
    min-height:57px;
    display:grid;
    grid-template-columns:135px 1fr;
    align-items:center;
    border:1px solid #25405f;
    border-radius:12px;
    overflow:hidden;
    background:#080f1b;
}

.label{
    padding:12px;
    background:#0b1625;
    color:#dbe9fa;
    font-weight:bold;
}

.value{
    padding:12px;
    text-align:center;
    color:#fff;
    font-size:17px;
}

.blue{
    color:#49a8ff;
}

.green{
    color:#42e58a;
}

.red{
    color:#ff6575;
}

.price{
    border-color:#1685ff;
}

.price .value{
    color:#4da9ff;
    font-size:21px;
    font-weight:bold;
}

.description{
    margin-top:10px;
    padding:15px;
    border:1px solid #25405f;
    border-radius:14px;
    background:#080f1b;
    white-space:pre-wrap;
}

.actions{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin-top:15px;
}

.btn{
    flex:1;
    min-width:130px;
    padding:14px;
    border-radius:12px;
    text-align:center;
    text-decoration:none;
    color:#fff;
    font-weight:bold;
    border:1px solid #275274;
    background:#0c1725;
}

.edit{
    background:#087cff;
    border-color:#087cff;
}

.delete{
    background:#6d1721;
    border-color:#a52a38;
}

.back{
    background:#111b29;
}

@media(max-width:750px){

    .content{
        grid-template-columns:1fr;
    }

    .gallery{
        min-height:350px;
    }

    .main-image{
        height:340px;
    }

    .row{
        grid-template-columns:110px 1fr;
    }

}

</style>

</head>

<body>

<div class="wrap">

<div class="ad-card">

<div class="top">
    🛒 LUCAS SHOP
    <span class="code">#{{ lucas_public_number(ad) }}</span>
</div>

<div class="content">

<div class="gallery">

{% if images and images[0] %}

<div class="main-photo-wrap">

<img
    id="mainImage"
    class="main-image"
    src="{{ images[0] }}"
>

</div>

{% if images|length > 1 %}

<div class="thumbs">

{% for image in images %}

{% if image %}

<button
    type="button"
    class="thumb {% if loop.first %}active{% endif %}"
    onclick="showAdImage({{ loop.index0 }}, this)"
>
<img src="{{ image }}" alt="">
</button>

{% endif %}

{% endfor %}

</div>

{% endif %}

{% else %}

<div class="no-image">
    تصویر ندارد
</div>

{% endif %}

</div>


<div class="info">

<div class="row">
    <div class="label">کد آگهی</div>
    <div class="value blue">
        {{ ad['listing_code'] }}
    </div>
</div>

<div class="row">
    <div class="label">تاون هال</div>
    <div class="value blue">
        TH {{ val(ad['town_hall']) }}
    </div>
</div>

<div class="row">
    <div class="label">بیلدر هال</div>
    <div class="value blue">
        BH {{ val(ad['builder_hall']) }}
    </div>
</div>

<div class="row">
    <div class="label">کینگ بربر</div>
    <div class="value">
        {{ ad['barbarian_king'] if ad['barbarian_king'] not in (None, '', 0, '0') else '—' }}
    </div>
</div>

<div class="row">
    <div class="label">آرچر کویین</div>
    <div class="value">
        {{ ad['archer_queen'] if ad['archer_queen'] not in (None, '', 0, '0') else '—' }}
    </div>
</div>

<div class="row">
    <div class="label">گرند واردن</div>
    <div class="value">
        {{ ad['grand_warden'] if ad['grand_warden'] not in (None, '', 0, '0') else '—' }}
    </div>
</div>

<div class="row">
    <div class="label">هیروی سلطنتی</div>
    <div class="value">
        {{ ad['royal_champion'] if ad['royal_champion'] not in (None, '', 0, '0') else '—' }}
    </div>
</div>

<div class="row">
    <div class="label">تغییر نام</div>
    <div class="value">
        {{ val(ad['name_change']) }}
        {% if ad['name_change'] == 'با جم' and ad['name_change_gems'] %}
        — {{ ad['name_change_gems'] }} 💎
        {% endif %}
    </div>
</div>

<div class="row">
    <div class="label">Supercell ID</div>

    <div class="value
        {% if ad['supercell_status']=='متصل' %}
        green
        {% else %}
        red
        {% endif %}
    ">

        {% if ad['supercell_status']=='متصل' %}
            🟢 متصل
        {% elif ad['supercell_status']=='متصل نیست' %}
            🔴 متصل نیست
        {% else %}
            —
        {% endif %}

    </div>

</div>

<div class="row price">
    <div class="label">قیمت</div>
    <div class="value">
        {{ lucas_toman(ad['price']) }}
    </div>
</div>

{% if ad['description'] %}

<div class="description">
    {{ ad['description'] }}
</div>

{% endif %}

</div>

</div>

<div style="padding:0 15px 15px">

<div class="actions">

{% if session.get('user_id') and lucas_ad_allowed(ad) %}

<a
    class="btn edit"
    href="/ad/{{ ad['listing_code'] }}/edit"
>
✏️ ویرایش آگهی
</a>

<a
    class="btn delete"
    href="/ad/{{ ad['listing_code'] }}/delete"
    onclick="return confirm('آیا از حذف این آگهی مطمئن هستید؟')"
>
🗑 حذف آگهی
</a>

{% endif %}

<a
    class="btn back"
    href="/my-ads"
>
📋 آگهی‌های من
</a>

</div>

</div>

</div>

</div>

<script>

const adImages = [
{% for image in images %}
{% if image %}
"{{ image }}"{% if not loop.last %},{% endif %}
{% endif %}
{% endfor %}
];

function showAdImage(index, button){

    const main = document.getElementById("mainImage");

    if(!main || !adImages[index]){
        return;
    }

    main.src = adImages[index];

    document.querySelectorAll(".thumb").forEach(function(x){
        x.classList.remove("active");
    });

    button.classList.add("active");
}

</script>

</body>
</html>
"""

    return render_template_string(
        html,
        ad=ad,
        images=images,
        val=val,
        lucas_toman=lucas_toman,
        lucas_ad_allowed=lucas_ad_allowed,
        lucas_public_number=lucas_public_number
    )


app.add_url_rule(
    "/ad/<code>",
    endpoint="lucas_ad_view",
    view_func=lucas_ad_view,
    methods=["GET"]
)


# ============================================================
# حذف آگهی
# ============================================================

def lucas_delete_ad(code):

    if not session.get("user_id"):
        return redirect(url_for("lucas_login"))

    lucas_fill_missing_ad_codes()

    c = lucas_ad_management_db()

    ad = c.execute(
        "SELECT * FROM ads WHERE listing_code=?",
        (code,)
    ).fetchone()

    if not ad:
        c.close()
        return "آگهی پیدا نشد", 404

    if not lucas_ad_allowed(ad):
        c.close()
        return "اجازه حذف این آگهی را ندارید.", 403

    # حذف تصاویر مربوط به آگهی
    for col in ["image", "image2", "image3"]:

        filename = ad[col] if col in ad.keys() else ""

        if filename:

            try:
                full = os.path.join(
                    UPLOAD_DIR,
                    filename
                )

                if os.path.exists(full):
                    os.remove(full)

            except:
                pass

    c.execute(
        "DELETE FROM ads WHERE id=?",
        (ad["id"],)
    )

    c.commit()
    c.close()

    return redirect(url_for("lucas_my_ads_management"))


app.add_url_rule(
    "/ad/<code>/delete",
    endpoint="lucas_delete_ad",
    view_func=lucas_delete_ad,
    methods=["GET"]
)


# ============================================================
# ویرایش آگهی
# ============================================================

def lucas_edit_ad(code):

    if not session.get("user_id"):
        return redirect(url_for("lucas_login"))

    lucas_fill_missing_ad_codes()

    c = lucas_ad_management_db()

    ad = c.execute(
        "SELECT * FROM ads WHERE listing_code=?",
        (code,)
    ).fetchone()

    if not ad:
        c.close()
        return "آگهی پیدا نشد", 404

    if not lucas_ad_allowed(ad):
        c.close()
        return "اجازه ویرایش این آگهی را ندارید.", 403

    error = ""

    if request.method == "POST":

        account_name = request.form.get(
            "account_name",""
        ).strip()

        player_tag = request.form.get(
            "player_tag",""
        ).strip()

        town_hall = request.form.get(
            "town_hall",""
        ).strip()

        builder_hall = request.form.get(
            "builder_hall",""
        ).strip()

        barbarian_king = request.form.get(
            "barbarian_king","0"
        ).strip()

        archer_queen = request.form.get(
            "archer_queen","0"
        ).strip()

        grand_warden = request.form.get(
            "grand_warden","0"
        ).strip()

        royal_champion = request.form.get(
            "royal_champion","0"
        ).strip()

        supercell_status = request.form.get(
            "supercell_status",""
        ).strip()

        name_change = request.form.get(
            "name_change",""
        ).strip()

        name_change_gems = request.form.get(
            "name_change_gems",""
        ).strip()

        price = request.form.get(
            "price","0"
        ).replace(",","").replace("٬","").replace("تومان","").strip()

        telegram = request.form.get(
            "telegram",""
        ).strip()

        description = request.form.get(
            "description",""
        ).strip()

        try:

            th = int(town_hall)
            bh = int(builder_hall)

            bk = int(barbarian_king or 0)
            aq = int(archer_queen or 0)
            gw = int(grand_warden or 0)
            rc = int(royal_champion or 0)

            price_int = int(price or 0)

        except:

            error = "مقادیر واردشده صحیح نیست."

            th = bh = bk = aq = gw = rc = price_int = 0


        if not error and not (1 <= th <= 18):
            error = "تاون هال باید بین ۱ تا ۱۸ باشد."

        if not error and not (1 <= bh <= 10):
            error = "بیلدر هال باید بین ۱ تا ۱۰ باشد."


        # سقف هیروها
        if not error and th in LUCAS_HERO_MAX:

            mx = LUCAS_HERO_MAX[th]

            if bk > mx["barbarian_king"]:
                error = f"حداکثر کینگ در TH{th} برابر {mx['barbarian_king']} است."

            elif aq > mx["archer_queen"]:
                error = f"حداکثر کویین در TH{th} برابر {mx['archer_queen']} است."

            elif gw > mx["grand_warden"]:
                error = f"حداکثر واردن در TH{th} برابر {mx['grand_warden']} است."

            elif rc > mx["royal_champion"]:
                error = f"حداکثر رویال چمپیون در TH{th} برابر {mx['royal_champion']} است."


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
                error = "مقدار جم معتبر نیست."


        if not error:

            # اگر عکس جدید انتخاب شود، جایگزین عکس‌های قبلی می‌شود
            new_images = request.files.getlist("images")

            valid_new = [
                x for x in new_images
                if x and x.filename
            ]

            if len(valid_new) > 3:
                error = "حداکثر ۳ عکس مجاز است."

            if not error and valid_new:

                allowed = {
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "gif"
                }

                saved = []

                os.makedirs(
                    UPLOAD_DIR,
                    exist_ok=True
                )

                for img in valid_new[:3]:

                    fn = secure_filename(
                        img.filename
                    )

                    if "." not in fn:
                        continue

                    ext = fn.rsplit(
                        ".",
                        1
                    )[1].lower()

                    if ext not in allowed:
                        continue

                    filename = (
                        str(int(time.time()*1000000))
                        + "_edit_"
                        + str(len(saved)+1)
                        + "."
                        + ext
                    )

                    img.save(
                        os.path.join(
                            UPLOAD_DIR,
                            filename
                        )
                    )

                    saved.append(filename)


                if not saved:
                    error = "عکس جدید معتبر نیست."

                else:

                    # پاک کردن عکس‌های قبلی
                    for col in [
                        "image",
                        "image2",
                        "image3"
                    ]:

                        old = ad[col]

                        if old:

                            try:

                                oldpath = os.path.join(
                                    UPLOAD_DIR,
                                    old
                                )

                                if os.path.exists(oldpath):
                                    os.remove(oldpath)

                            except:
                                pass


                    image1 = saved[0] if len(saved)>0 else ""
                    image2 = saved[1] if len(saved)>1 else ""
                    image3 = saved[2] if len(saved)>2 else ""

                    c.execute("""
                        UPDATE ads SET
                            title=?,
                            account_name=?,
                            player_tag=?,
                            town_hall=?,
                            builder_hall=?,
                            barbarian_king=?,
                            archer_queen=?,
                            grand_warden=?,
                            royal_champion=?,
                            supercell_status=?,
                            name_change=?,
                            name_change_gems=?,
                            price=?,
                            telegram=?,
                            description=?,
                            image=?,
                            image2=?,
                            image3=?
                        WHERE id=?
                    """,(
                        account_name,
                        account_name,
                        player_tag,
                        th,
                        bh,
                        bk,
                        aq,
                        gw,
                        rc,
                        supercell_status,
                        name_change,
                        name_change_gems,
                        price_int,
                        telegram,
                        description,
                        image1,
                        image2,
                        image3,
                        ad["id"]
                    ))

                    c.commit()


            else:

                c.execute("""
                    UPDATE ads SET
                        title=?,
                        account_name=?,
                        player_tag=?,
                        town_hall=?,
                        builder_hall=?,
                        barbarian_king=?,
                        archer_queen=?,
                        grand_warden=?,
                        royal_champion=?,
                        supercell_status=?,
                        name_change=?,
                        name_change_gems=?,
                        price=?,
                        telegram=?,
                        description=?
                    WHERE id=?
                """,(
                    account_name,
                    account_name,
                    player_tag,
                    th,
                    bh,
                    bk,
                    aq,
                    gw,
                    rc,
                    supercell_status,
                    name_change,
                    name_change_gems,
                    price_int,
                    telegram,
                    description,
                    ad["id"]
                ))

                c.commit()


            c.close()

            return redirect(
                url_for(
                    "lucas_ad_view",
                    code=code
                )
            )


    c.close()

    html = """
<!doctype html>
<html lang="fa" dir="rtl">

<head>

<meta charset="utf-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>ویرایش {{ ad['listing_code'] }}</title>

<style>

body{
    margin:0;
    background:#060a11;
    color:#fff;
    font-family:Tahoma,Arial;
}

.box{
    width:min(800px,94%);
    margin:25px auto;
    background:#101722;
    padding:22px;
    border-radius:20px;
    border:1px solid #24415f;
}

h1{
    text-align:center;
}

label{
    display:block;
    margin-top:13px;
    margin-bottom:6px;
}

input,
textarea,
select{
    width:100%;
    box-sizing:border-box;
    padding:12px;
    border-radius:10px;
    border:1px solid #2b4057;
    background:#080d14;
    color:#fff;
}

textarea{
    min-height:120px;
}

button{
    width:100%;
    margin-top:20px;
    padding:14px;
    border:0;
    border-radius:12px;
    background:#087cff;
    color:#fff;
    font-size:17px;
    font-weight:bold;
}

.error{
    background:#48151d;
    padding:12px;
    border-radius:10px;
}

.back{
    display:block;
    text-align:center;
    margin-top:15px;
    color:#8ebcff;
}

</style>

</head>

<body>

<div class="box">

<h1>
✏️ ویرایش {{ ad['listing_code'] }}
</h1>

{% if error %}
<div class="error">
{{ error }}
</div>
{% endif %}

<form method="POST" enctype="multipart/form-data">

<label>نام اکانت</label>
<input
 name="account_name"
 value="{{ ad['account_name'] or ad['title'] or '' }}"
>

<label>Player Tag</label>
<input
 name="player_tag"
 value="{{ ad['player_tag'] or '' }}"
>

<label>تاون هال</label>
<input
 type="number"
 min="1"
 max="18"
 name="town_hall"
 value="{{ ad['town_hall'] or '' }}"
>

<label>بیلدر هال</label>
<input
 type="number"
 min="1"
 max="10"
 name="builder_hall"
 value="{{ ad['builder_hall'] or '' }}"
>

<label>کینگ بربر</label>
<input
 type="number"
 min="0"
 name="barbarian_king"
 value="{{ ad['barbarian_king'] or 0 }}"
>

<label>آرچر کویین</label>
<input
 type="number"
 min="0"
 name="archer_queen"
 value="{{ ad['archer_queen'] or 0 }}"
>

<label>گرند واردن</label>
<input
 type="number"
 min="0"
 name="grand_warden"
 value="{{ ad['grand_warden'] or 0 }}"
>

<label>رویال چمپیون</label>
<input
 type="number"
 min="0"
 name="royal_champion"
 value="{{ ad['royal_champion'] or 0 }}"
>

<label>Supercell ID</label>

<select name="supercell_status">

<option
 value="متصل"
 {% if ad['supercell_status']=='متصل' %}selected{% endif %}
>
🟢 متصل
</option>

<option
 value="متصل نیست"
 {% if ad['supercell_status']=='متصل نیست' %}selected{% endif %}
>
🔴 متصل نیست
</option>

</select>


<label>تغییر نام</label>

<select name="name_change">

<option
 value="رایگان"
 {% if ad['name_change']=='رایگان' %}selected{% endif %}
>
رایگان
</option>

<option
 value="با جم"
 {% if ad['name_change']=='با جم' %}selected{% endif %}
>
با جم
</option>

</select>


<label>جم تغییر نام</label>

<select name="name_change_gems">

{% for g in ['500','1000','1500','2000','2500','3000','3500','3500 و بیشتر'] %}

<option
 value="{{ g }}"
 {% if ad['name_change_gems']==g %}selected{% endif %}
>
{{ g }}
</option>

{% endfor %}

</select>


<label>قیمت</label>

<input
 type="text"
 name="price"
 value="{{ ad['price'] }}"
 placeholder="مثلاً 100,000 تومان"
>


<label>تلگرام</label>

<input
 name="telegram"
 value="{{ ad['telegram'] or '' }}"
>


<label>توضیحات</label>

<textarea name="description">{{ ad['description'] or '' }}</textarea>


<label>
عکس جدید — اختیاری، حداکثر ۳ عکس
</label>

<input
 type="file"
 name="images"
 multiple
 accept="image/png,image/jpeg,image/webp,image/gif"
 onchange="if(this.files.length>3){alert('حداکثر ۳ عکس');this.value='';}"
>


<button type="submit">
💾 ذخیره تغییرات
</button>

</form>

<a class="back" href="/ad/{{ ad['listing_code'] }}">
↩️ بازگشت به آگهی
</a>

</div>

</body>

</html>
"""

    return render_template_string(
        html,
        ad=ad,
        error=error
    )


app.add_url_rule(
    "/ad/<code>/edit",
    endpoint="lucas_edit_ad",
    view_func=lucas_edit_ad,
    methods=["GET","POST"]
)


# ============================================================
# مدیریت آگهی‌های کاربر
# ============================================================


# ============================================================
# LUCAS APPROVAL SYSTEM
# ============================================================

def lucas_approved_column():
    c = lucas_ad_management_db()
    cols = [x[1] for x in c.execute("PRAGMA table_info(ads)").fetchall()]
    if "approved" not in cols:
        c.execute("ALTER TABLE ads ADD COLUMN approved INTEGER DEFAULT 0")
        c.commit()
    c.close()

lucas_approved_column()


@app.route("/ad/<code>/approve", methods=["GET"])
def lucas_approve_ad(code):
    if not session.get("user_id"):
        return redirect(url_for("lucas_login"))

    if not lucas_is_admin():
        return "دسترسی غیرمجاز", 403

    lucas_approved_column()

    c = lucas_ad_management_db()

    ad = c.execute(
        "SELECT id, approved FROM ads WHERE listing_code=?",
        (code,)
    ).fetchone()

    if not ad:
        c.close()
        return "آگهی پیدا نشد", 404

    status = 0 if ad["approved"] else 1

    c.execute(
        "UPDATE ads SET approved=? WHERE id=?",
        (status, ad["id"])
    )

    c.commit()
    c.close()

    return redirect("/manage-ads")


def lucas_my_ads_management():

    if not session.get("user_id"):
        return redirect(url_for("lucas_login"))

    lucas_fill_missing_ad_codes()

    c = lucas_ad_management_db()

    if lucas_is_admin():

        ads = c.execute("""
            SELECT * FROM ads
            ORDER BY id DESC
        """).fetchall()

    else:

        ads = c.execute("""
            SELECT * FROM ads
            WHERE seller_id=?
            ORDER BY id DESC
        """,(session.get("user_id"),)).fetchall()

    c.close()

    html = """
<!doctype html>
<html lang="fa" dir="rtl">

<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>مدیریت آگهی‌ها | LUCAS SHOP</title>

<style>

body{
    margin:0;
    background:#060a11;
    color:#fff;
    font-family:Tahoma,Arial;
}

.wrap{
    width:min(1000px,94%);
    margin:25px auto;
}

h1{
    text-align:center;
}

.grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
    gap:15px;
}

.card{
    background:#101722;
    border:1px solid #25415e;
    border-radius:18px;
    padding:15px;
}

.code{
    color:#4ba7ff;
    font-size:18px;
    font-weight:bold;
}

.name{
    margin-top:8px;
    font-size:18px;
}

.price{
    color:#4ba7ff;
    margin-top:8px;
}

.status{
    color:#9baabd;
    margin-top:6px;
}

.actions{
    display:flex;
    gap:8px;
    margin-top:15px;
}

.btn{
    flex:1;
    padding:11px;
    text-align:center;
    border-radius:10px;
    text-decoration:none;
    color:#fff;
    background:#087cff;
}

.delete{
    background:#701923;
}

.open{
    background:#172537;
}

.empty{
    text-align:center;
    color:#8897aa;
    padding:50px;
}

</style>

</head>

<body>

<div class="wrap">

<h1>
📋 مدیریت آگهی‌ها
</h1>

{% if ads %}

<div class="grid">

{% for ad in ads %}

<div class="card">

<div class="code">
{{ ad['listing_code'] }}
</div>

<div class="name">
{{ ad['account_name'] or ad['title'] or 'بدون نام' }}
</div>

<div>
🏰 TH {{ ad['town_hall'] or '—' }}
&nbsp;&nbsp;
🔨 BH {{ ad['builder_hall'] or '—' }}
</div>

<div class="price">
💰 {{ lucas_toman(ad['price']) }}
</div>

<div class="status">
Supercell:
{{ ad['supercell_status'] or '—' }}
</div>

<div class="status">
{% if ad['approved'] %}
✅ وضعیت: تأیید شده
{% else %}
⏳ وضعیت: در انتظار تأیید
{% endif %}
</div>

<div class="actions">

<a
class="btn open"
href="/ad/{{ ad['listing_code'] }}"
>
👁 مشاهده
</a>

<a
class="btn"
href="/ad/{{ ad['listing_code'] }}/edit"
>
✏️ ویرایش
</a>

{% if lucas_admin_mode %}
<a
class="btn"
href="/ad/{{ ad['listing_code'] }}/approve"
style="background:#16823b;"
>
{% if ad['approved'] %}
↩️ لغو تأیید
{% else %}
✅ تأیید
{% endif %}
</a>
{% endif %}

<a
class="btn delete"
href="/ad/{{ ad['listing_code'] }}/delete"
onclick="return confirm('آگهی حذف شود؟')"
>
🗑 حذف
</a>

</div>

</div>

{% endfor %}

</div>

{% else %}

<div class="empty">
هنوز آگهی‌ای ثبت نشده است.
</div>

{% endif %}

</div>

</body>

</html>
"""

    return render_template_string(
        html,
        ads=ads,
        lucas_toman=lucas_toman,
        lucas_admin_mode=lucas_is_admin()
    )


# مسیر جدید
app.add_url_rule(
    "/manage-ads",
    endpoint="lucas_my_ads_management",
    view_func=lucas_my_ads_management,
    methods=["GET"]
)


# مسیر /my-ads را هم به مدیریت جدید وصل می‌کنیم
for _rule in list(app.url_map.iter_rules()):

    if _rule.rule == "/my-ads":

        app.view_functions[
            _rule.endpoint
        ] = lucas_my_ads_management


print("======================================")
print("✅ LUCAS AD MANAGEMENT ACTIVE")
print("✅ Auto Listing Codes: LS-0001 ...")
print("✅ Edit: ON")
print("✅ Delete: ON")
print("✅ Ad Display Template: ON")
print("======================================")





# ============================================================
# LUCAS_FINAL_AD_FIX_INSTALLED
# LUCAS SHOP - FINAL PUBLIC ADS FIX
# فقط بازار و نمایش آگهی را اصلاح می‌کند
# ============================================================

def LUCAS_FINAL_AD_DATA(code):
    c=lucas_ad_management_db()

    ad=None

    # کد داخلی مثل LS-0001
    ad=c.execute(
        "SELECT * FROM ads WHERE listing_code=?",
        (str(code),)
    ).fetchone()

    # شماره مثل 1
    if not ad:
        x=str(code).lstrip("#")
        if x.isdigit():
            ad=c.execute(
                "SELECT * FROM ads WHERE ad_number=? OR id=?",
                (int(x),int(x))
            ).fetchone()

    c.close()
    return ad


def LUCAS_FINAL_PUBLIC_AD(code):

    ad=LUCAS_FINAL_AD_DATA(code)

    if not ad:
        return "آگهی پیدا نشد",404

    def V(*names):
        for name in names:
            try:
                value=ad[name]
                if value is not None and str(value).strip()!="":
                    return value
            except:
                pass
        return "—"

    images=[]

    for name in ("image1","image2","image3"):
        try:
            value=ad[name]
        except:
            value=""

        if value:
            value=str(value)

            if value.startswith("/uploads/"):
                value=value[len("/uploads/"):]

            if value not in images:
                images.append(value)

    public_number=V("ad_number","id")
    public_code="#"+str(public_number)

    html=r"""
<!doctype html>
<html lang="fa" dir="rtl">

<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{{ public_code }} | LUCAS SHOP</title>

<style>

*{
box-sizing:border-box;
}

body{
margin:0;
background:#050912;
color:#fff;
font-family:Tahoma,Arial,sans-serif;
}

a{
text-decoration:none;
color:inherit;
}

.wrap{
max-width:900px;
margin:auto;
padding:20px 12px 60px;
}

.ad-card{
background:#080f1c;
border:1px solid #20324d;
border-radius:24px;
overflow:hidden;
box-shadow:0 20px 70px #0009;
}

.top{
padding:18px;
font-size:22px;
font-weight:900;
border-bottom:1px solid #20324d;
}

.code{
float:left;
background:#0d1b31;
border:1px solid #28558d;
color:#60a5fa;
padding:8px 14px;
border-radius:12px;
font-size:17px;
}

.content{
padding:15px;
}

.gallery{
background:#040810;
border:1px solid #182941;
border-radius:18px;
overflow:hidden;
}

.main-image{
display:block;
width:100%;
height:430px;
object-fit:contain;
background:#040810;
}

.thumbs{
display:flex;
gap:9px;
padding:10px;
overflow-x:auto;
}

.thumb{
width:82px;
height:65px;
object-fit:cover;
border-radius:10px;
border:2px solid #243852;
cursor:pointer;
flex:none;
}

.info{
margin-top:15px;
}

.row{
display:flex;
align-items:center;
justify-content:space-between;
gap:15px;
padding:14px;
margin-bottom:8px;
background:#0d1728;
border:1px solid #1b2b44;
border-radius:12px;
}

.label{
color:#94a3b8;
}

.value{
font-weight:900;
color:#fff;
text-align:left;
}

.blue{
color:#60a5fa;
}

.green{
color:#4ade80;
}

.red{
color:#f87171;
}

.price{
font-size:20px;
}

.description{
margin-top:10px;
padding:16px;
background:#0d1728;
border:1px solid #1b2b44;
border-radius:12px;
line-height:2;
color:#dbeafe;
}

.back{
display:block;
margin-top:15px;
padding:14px;
background:#2563eb;
border-radius:13px;
text-align:center;
font-weight:900;
}

@media(max-width:600px){

.wrap{
padding:10px 8px 40px;
}

.main-image{
height:300px;
}

.top{
font-size:19px;
}

.code{
font-size:15px;
}

.row{
font-size:13px;
}

}

</style>
</head>

<body>

<div class="wrap">

<div class="ad-card">

<div class="top">
🛒 LUCAS SHOP

<span class="code">
{{ public_code }}
</span>

<div style="clear:both"></div>
</div>


<div class="content">


<!-- تمام عکس‌های موجود داخل همان قالب -->

<div class="gallery">

{% if images %}

<img
id="mainImage"
class="main-image"
src="/uploads/{{ images[0] }}"
>

{% if images|length > 1 %}

<div class="thumbs">

{% for image in images %}

<img
class="thumb"
src="/uploads/{{ image }}"
onclick="document.getElementById('mainImage').src=this.src"
>

{% endfor %}

</div>

{% endif %}

{% else %}

<div style="height:300px;display:flex;align-items:center;justify-content:center;color:#64748b">
تصویر ندارد
</div>

{% endif %}

</div>


<div class="info">


<div class="row">

<div class="label">
کد آگهی
</div>

<div class="value blue">
{{ public_code }}
</div>

</div>


<div class="row">

<div class="label">
نام اکانت
</div>

<div class="value">
{{ V("account_name","title") }}
</div>

</div>


<div class="row">

<div class="label">
تاون هال
</div>

<div class="value blue">
TH {{ V("townhall","th") }}
</div>

</div>


<div class="row">

<div class="label">
بیلدر هال
</div>

<div class="value blue">
BH {{ V("builderhall","builder_hall","bh") }}
</div>

</div>


<div class="row">

<div class="label">
کینگ بربر
</div>

<div class="value">
{{ V("barbarian_king","king") }}
</div>

</div>


<div class="row">

<div class="label">
آرچر کویین
</div>

<div class="value">
{{ V("archer_queen","queen") }}
</div>

</div>


<div class="row">

<div class="label">
گرند واردن
</div>

<div class="value">
{{ V("grand_warden","warden") }}
</div>

</div>


<div class="row">

<div class="label">
هیروی سلطنتی
</div>

<div class="value">
{{ V("royal_champion","royal") }}
</div>

</div>


<div class="row">

<div class="label">
تغییر نام
</div>

<div class="value">
{{ V("name_change") }}

{% if V("name_change_gems") != "—" %}
 — {{ V("name_change_gems") }} 💎
{% endif %}

</div>

</div>


<div class="row">

<div class="label">
Supercell ID
</div>

<div class="value">

{% set sid=V("supercell_id","supercell") %}

{% if sid in ["متصل","متصل است","connected","1"] %}

<span class="green">🟢 متصل</span>

{% elif sid in ["متصل نیست","قطع","0","not_connected"] %}

<span class="red">🔴 متصل نیست</span>

{% else %}

{{ sid }}

{% endif %}

</div>

</div>


<div class="row price">

<div class="label">
قیمت
</div>

<div class="value blue">
{{ V("price") }} تومان
</div>

</div>


{% if V("description") != "—" %}

<div class="description">
{{ V("description") }}
</div>

{% endif %}


</div>


<a class="back" href="/explore">
← برگشت به آگهی‌ها
</a>


</div>

</div>

</div>

</body>
</html>
"""

    return render_template_string(
        html,
        ad=ad,
        images=images,
        public_code=public_code,
        V=V
    )


# ------------------------------------------------------------
# بازار واقعی LUCAS SHOP
# ------------------------------------------------------------

def LUCAS_FINAL_EXPLORE():

    c=lucas_ad_management_db()

    ads=c.execute("""
        SELECT *
        FROM ads
        ORDER BY id DESC
    """).fetchall()

    c.close()

    html=r"""
<!doctype html>
<html lang="fa" dir="rtl">

<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>LUCAS SHOP | آگهی‌ها</title>

<style>

*{
box-sizing:border-box;
}

body{
margin:0;
background:#050912;
color:#fff;
font-family:Tahoma,Arial,sans-serif;
}

a{
text-decoration:none;
color:inherit;
}

.nav{
padding:18px;
border-bottom:1px solid #18263b;
display:flex;
justify-content:space-between;
align-items:center;
max-width:1200px;
margin:auto;
}

.logo{
font-size:23px;
font-weight:900;
}

.logo span{
color:#3b82f6;
}

.btn{
display:inline-block;
padding:10px 15px;
border-radius:12px;
background:#0d1728;
border:1px solid #243650;
font-weight:800;
}

.primary{
background:#2563eb;
border-color:#2563eb;
}

.wrap{
max-width:1200px;
margin:auto;
padding:28px 15px 60px;
}

.hero{
padding:28px;
border:1px solid #1d3150;
border-radius:24px;
background:
radial-gradient(circle at 85% 20%,rgba(37,99,235,.22),transparent 35%),
linear-gradient(145deg,#0b1424,#070c16);
margin-bottom:25px;
}

.hero h1{
margin:0 0 10px;
font-size:31px;
}

.hero p{
margin:0;
color:#94a3b8;
font-size:16px;
line-height:2;
}

.grid{
display:grid;
grid-template-columns:repeat(auto-fill,minmax(250px,1fr));
gap:16px;
}

.card{
overflow:hidden;
border:1px solid #182a43;
border-radius:20px;
background:#080f1c;
}

.pic{
height:210px;
background:#040810;
}

.pic img{
width:100%;
height:100%;
object-fit:cover;
}

.noimg{
height:100%;
display:flex;
align-items:center;
justify-content:center;
font-size:50px;
color:#64748b;
}

.body{
padding:15px;
}

.title{
font-size:19px;
font-weight:900;
margin-bottom:12px;
}

.code{
display:inline-block;
padding:7px 12px;
border-radius:10px;
background:#0d1b31;
border:1px solid #28558d;
color:#60a5fa;
font-weight:900;
margin-bottom:12px;
}

.info{
display:grid;
grid-template-columns:1fr 1fr;
gap:8px;
margin-bottom:13px;
}

.info div{
padding:10px;
border-radius:11px;
background:#0e1727;
border:1px solid #1a2940;
color:#94a3b8;
font-size:12px;
}

.info b{
display:block;
color:#fff;
font-size:15px;
margin-top:5px;
}

.price{
font-size:20px;
font-weight:900;
color:#60a5fa;
margin-bottom:13px;
}

.view{
display:block;
text-align:center;
padding:12px;
border-radius:12px;
background:#2563eb;
font-weight:900;
}

.empty{
text-align:center;
padding:70px 20px;
border:1px dashed #263650;
border-radius:20px;
color:#94a3b8;
}

@media(max-width:600px){

.grid{
grid-template-columns:1fr;
}

.pic{
height:230px;
}

.hero h1{
font-size:24px;
}

}

</style>
</head>

<body>

<div class="nav">

<a class="logo" href="/">
LUCAS <span>SHOP</span>
</a>

<div style="display:flex;gap:8px;flex-wrap:wrap">

<a class="btn" href="/">
خانه
</a>

<a class="btn primary" href="/create-ad">
📢 ثبت آگهی
</a>

<a class="btn" href="/account">
👤 حساب من
</a>

</div>

</div>


<main class="wrap">


<section class="hero">

<h1>
📢 آگهی‌های LUCAS SHOP
</h1>

<p>
آگهی‌های فروش اکانت کلش آف کلنز را مشاهده کنید.
</p>

</section>


{% if ads %}

<div class="grid">

{% for ad in ads %}

<article class="card">


<div class="pic">

{% if ad['image1'] %}

<img src="/uploads/{{ ad['image1'] }}">

{% elif ad['image2'] %}

<img src="/uploads/{{ ad['image2'] }}">

{% elif ad['image3'] %}

<img src="/uploads/{{ ad['image3'] }}">

{% else %}

<div class="noimg">
🎮
</div>

{% endif %}

</div>


<div class="body">


<div class="code">
#{{ ad['ad_number'] or ad['id'] }}
</div>


<div class="title">
{{ ad['account_name'] or ad['title'] or 'اکانت کلش آف کلنز' }}
</div>


<div class="info">

<div>
تاون هال
<b>
TH {{ ad['townhall'] if ad['townhall'] not in [None,''] else ad['th'] }}
</b>
</div>

<div>
بیلدر هال
<b>
BH {{ ad['builderhall'] if ad['builderhall'] not in [None,''] else ad['bh'] }}
</b>
</div>

</div>


<div class="price">
{{ ad['price'] }} تومان
</div>


<a class="view"
href="/ad/{{ ad['listing_code'] }}">
👁 مشاهده آگهی
</a>


</div>

</article>

{% endfor %}

</div>

{% else %}

<div class="empty">

<div style="font-size:50px">
📦
</div>

<h2>
هنوز آگهی‌ای ثبت نشده
</h2>

<a class="btn primary" href="/create-ad">
📢 ثبت آگهی
</a>

</div>

{% endif %}


</main>

</body>
</html>
"""

    return render_template_string(
        html,
        ads=ads
    )


# ============================================================
# جایگزینی view های قبلی بدون دست زدن به route های ادمین
# ============================================================

app.view_functions["lucas_ad_view"]=LUCAS_FINAL_PUBLIC_AD
app.view_functions["explore"]=LUCAS_FINAL_EXPLORE

# مسیرهای مستقیم اضافی برای شماره آگهی
@app.route("/ad-number/<int:number>")
def LUCAS_AD_NUMBER(number):
    return LUCAS_FINAL_PUBLIC_AD(str(number))


# LUCAS_FINAL_ADS_REPAIR_INSTALLED

# ============================================================
# LUCAS SHOP FINAL ADS REPAIR
# ============================================================

import sqlite3 as _LUCAS_SQLITE
import os as _LUCAS_OS

_LUCAS_AD_DB = _LUCAS_OS.path.join(
    _LUCAS_OS.path.dirname(__file__),
    "lucas_shop.db"
)


def _lucas_ads_db():
    c=_LUCAS_SQLITE.connect(_LUCAS_AD_DB)
    c.row_factory=_LUCAS_SQLITE.Row
    return c


def _lucas_repair_ads():

    c=_lucas_ads_db()

    cols=[
        r["name"]
        for r in c.execute("PRAGMA table_info(ads)").fetchall()
    ]

    if "listing_code" not in cols:
        c.execute(
            "ALTER TABLE ads ADD COLUMN listing_code TEXT"
        )

    if "ad_number" not in cols:
        c.execute(
            "ALTER TABLE ads ADD COLUMN ad_number INTEGER"
        )

    if "approved" not in cols:
        c.execute(
            "ALTER TABLE ads ADD COLUMN approved INTEGER DEFAULT 0"
        )

    # شماره نمایشی آگهی
    rows=c.execute("""
        SELECT id
        FROM ads
        WHERE ad_number IS NULL OR ad_number=0
        ORDER BY id
    """).fetchall()

    mx=c.execute("""
        SELECT COALESCE(MAX(ad_number),0)
        FROM ads
    """).fetchone()[0]

    for r in rows:
        mx+=1
        c.execute(
            "UPDATE ads SET ad_number=? WHERE id=?",
            (mx,r["id"])
        )

    # کد داخلی آگهی
    rows=c.execute("""
        SELECT id,ad_number
        FROM ads
        WHERE listing_code IS NULL OR listing_code=''
        ORDER BY id
    """).fetchall()

    for r in rows:
        c.execute(
            "UPDATE ads SET listing_code=? WHERE id=?",
            ("LS-%04d"%int(r["ad_number"]),r["id"])
        )

    # شماره خودکار برای آگهی‌های بعدی
    c.execute("""
    CREATE TRIGGER IF NOT EXISTS lucas_ads_auto_number
    AFTER INSERT ON ads
    WHEN NEW.ad_number IS NULL OR NEW.ad_number=0
    BEGIN
        UPDATE ads
        SET ad_number=(
            SELECT COALESCE(MAX(ad_number),0)+1
            FROM ads
            WHERE id != NEW.id
        )
        WHERE id=NEW.id
        AND (ad_number IS NULL OR ad_number=0);

        UPDATE ads
        SET listing_code='LS-' || printf('%04d',ad_number)
        WHERE id=NEW.id
        AND (listing_code IS NULL OR listing_code='');
    END
    """)

    c.commit()
    c.close()


_lucas_repair_ads()


def _lucas_get(ad,*names):

    for name in names:
        try:
            v=ad[name]
            if v is not None and str(v).strip()!="":
                return str(v)
        except Exception:
            pass

    return "—"


def _lucas_images(ad):

    result=[]

    for name in (
        "image1",
        "image2",
        "image3"
    ):

        try:
            value=ad[name]
        except Exception:
            value=""

        if value:
            value=str(value).strip()

            if value.startswith("/uploads/"):
                value=value[len("/uploads/"):]

            if value not in result:
                result.append(value)

    return result


def _lucas_find_ad(code):

    c=_lucas_ads_db()

    code=str(code).strip()

    # کد داخلی مثل LS-0001
    ad=c.execute(
        "SELECT * FROM ads WHERE listing_code=?",
        (code,)
    ).fetchone()

    # شماره مثل #1 یا 1
    if not ad:

        clean=code.replace("#","").strip()

        if clean.isdigit():

            ad=c.execute(
                "SELECT * FROM ads WHERE ad_number=?",
                (int(clean),)
            ).fetchone()

    c.close()

    return ad


def _lucas_ad_page(code):

    ad=_lucas_find_ad(code)

    if not ad:
        return """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>آگهی پیدا نشد</title>
<style>
body{
margin:0;
background:#050912;
color:white;
font-family:Tahoma,Arial;
text-align:center;
padding:70px 20px;
}
.box{
max-width:500px;
margin:auto;
background:#0b1424;
border:1px solid #20324d;
border-radius:20px;
padding:35px;
}
a{
display:block;
margin-top:20px;
padding:13px;
background:#2563eb;
border-radius:12px;
color:white;
text-decoration:none;
font-weight:900;
}
</style>
</head>
<body>
<div class="box">
<h2>آگهی پیدا نشد</h2>
<a href="/explore">بازگشت به آگهی‌ها</a>
</div>
</body>
</html>
""",404

    images=_lucas_images(ad)

    number=_lucas_get(ad,"ad_number","id")
    public_code="#"+number

    account=_lucas_get(
        ad,
        "account_name",
        "title"
    )

    th=_lucas_get(
        ad,
        "townhall",
        "town_hall",
        "th"
    )

    bh=_lucas_get(
        ad,
        "builderhall",
        "builder_hall",
        "bh"
    )

    king=_lucas_get(
        ad,
        "barbarian_king",
        "king"
    )

    queen=_lucas_get(
        ad,
        "archer_queen",
        "queen"
    )

    warden=_lucas_get(
        ad,
        "grand_warden",
        "warden"
    )

    royal=_lucas_get(
        ad,
        "royal_champion",
        "royal"
    )

    name_change=_lucas_get(
        ad,
        "name_change"
    )

    gems=_lucas_get(
        ad,
        "name_change_gems"
    )

    supercell=_lucas_get(
        ad,
        "supercell_id",
        "supercell"
    )

    price=_lucas_get(
        ad,
        "price"
    )

    description=_lucas_get(
        ad,
        "description"
    )

    # وضعیت Supercell
    if supercell in (
        "متصل",
        "متصل است",
        "connected",
        "1"
    ):
        supercell_html='<span class="green">🟢 متصل</span>'
    elif supercell in (
        "متصل نیست",
        "قطع",
        "0",
        "not_connected"
    ):
        supercell_html='<span class="red">🔴 متصل نیست</span>'
    else:
        supercell_html=supercell

    # تغییر نام
    if gems!="—" and name_change!="—":
        name_html=name_change+" — "+gems+" 💎"
    else:
        name_html=name_change

    # --------------------------------------------------------
    # گالری داخل همان قالب آگهی
    # --------------------------------------------------------

    if images:

        first="/uploads/"+images[0]

        thumbs=""

        if len(images)>1:

            thumbs="""
<div class="thumbs">
%s
</div>
""" % "".join(
                """
<img
class="thumb"
src="/uploads/%s"
onclick="document.getElementById('mainImage').src=this.src"
>
""" % x
                for x in images
            )

        gallery="""
<div class="gallery">

<img
id="mainImage"
class="main-image"
src="%s"
>

%s

</div>
""" % (
            first,
            thumbs
        )

    else:

        gallery="""
<div class="gallery no-image">
🎮
<div>تصویر ندارد</div>
</div>
"""

    description_html=""

    if description!="—":
        description_html="""
<div class="description">
%s
</div>
""" % description

    html="""
<!doctype html>
<html lang="fa" dir="rtl">

<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>%s | LUCAS SHOP</title>

<style>

*{
box-sizing:border-box;
}

body{
margin:0;
background:#050912;
color:#fff;
font-family:Tahoma,Arial,sans-serif;
}

.wrap{
width:100%%;
max-width:620px;
margin:auto;
padding:14px 10px 40px;
}

.card{
background:#080f1c;
border:1px solid #20324d;
border-radius:20px;
overflow:hidden;
}

.header{
padding:14px;
border-bottom:1px solid #20324d;
font-size:19px;
font-weight:900;
}

.header-code{
float:left;
padding:6px 11px;
border-radius:10px;
background:#0d1b31;
border:1px solid #28558d;
color:#60a5fa;
font-size:15px;
}

.content{
padding:10px;
}

/* ==========================================================
   تصویرها داخل همان قالب
   ========================================================== */

.gallery{
width:100%%;
background:#03070d;
border:1px solid #172840;
border-radius:14px;
overflow:hidden;
}

.main-image{
display:block;
width:100%%;
height:260px;
object-fit:contain;
background:#03070d;
}

.thumbs{
display:flex;
gap:7px;
padding:7px;
overflow-x:auto;
}

.thumb{
width:64px;
height:50px;
object-fit:cover;
border-radius:8px;
border:2px solid #263b59;
flex:none;
cursor:pointer;
}

.no-image{
height:180px;
display:flex;
align-items:center;
justify-content:center;
flex-direction:column;
color:#64748b;
font-size:32px;
gap:7px;
}

/* ==========================================================
   اطلاعات قالب
   ========================================================== */

.info{
margin-top:10px;
}

.row{
display:flex;
align-items:center;
justify-content:space-between;
gap:10px;
padding:9px 11px;
margin-bottom:5px;
background:#0d1728;
border:1px solid #1b2b44;
border-radius:10px;
font-size:13px;
min-height:40px;
}

.label{
color:#94a3b8;
}

.value{
font-weight:900;
color:#fff;
text-align:left;
}

.blue{
color:#60a5fa;
}

.green{
color:#4ade80;
}

.red{
color:#f87171;
}

.account-row{
font-size:16px;
}

.price-row{
font-size:18px;
}

.description{
margin-top:6px;
padding:11px;
background:#0d1728;
border:1px solid #1b2b44;
border-radius:10px;
line-height:1.8;
font-size:13px;
}

.back{
display:block;
margin-top:10px;
padding:11px;
text-align:center;
background:#2563eb;
border-radius:11px;
color:white;
text-decoration:none;
font-weight:900;
}

@media(max-width:600px){

.wrap{
padding:7px;
}

.main-image{
height:235px;
}

.row{
font-size:13px;
padding:9px;
}

.account-row{
font-size:15px;
}

}

</style>

</head>

<body>

<div class="wrap">

<div class="card">

<div class="header">

🛒 LUCAS SHOP

<span class="header-code">
%s
</span>

<div style="clear:both"></div>

</div>

<div class="content">

%s

<div class="info">

<div class="row">

<div class="label">
کد آگهی
</div>

<div class="value blue">
%s
</div>

</div>

<div class="row account-row">

<div class="label">
نام اکانت
</div>

<div class="value">
%s
</div>

</div>

<div class="row">

<div class="label">
تاون هال
</div>

<div class="value blue">
TH %s
</div>

</div>

<div class="row">

<div class="label">
بیلدر هال
</div>

<div class="value blue">
BH %s
</div>

</div>

<div class="row">

<div class="label">
کینگ بربر
</div>

<div class="value">
%s
</div>

</div>

<div class="row">

<div class="label">
آرچر کویین
</div>

<div class="value">
%s
</div>

</div>

<div class="row">

<div class="label">
گرند واردن
</div>

<div class="value">
%s
</div>

</div>

<div class="row">

<div class="label">
هیروی سلطنتی
</div>

<div class="value">
%s
</div>

</div>

<div class="row">

<div class="label">
تغییر نام
</div>

<div class="value">
%s
</div>

</div>

<div class="row">

<div class="label">
Supercell ID
</div>

<div class="value">
%s
</div>

</div>

<div class="row price-row">

<div class="label">
قیمت
</div>

<div class="value blue">
%s تومان
</div>

</div>

%s

</div>

<a class="back" href="/explore">
← برگشت به آگهی‌ها
</a>

</div>

</div>

</div>

</body>
</html>
""" % (
        public_code,
        public_code,
        gallery,
        public_code,
        account,
        th,
        bh,
        king,
        queen,
        warden,
        royal,
        name_html,
        supercell_html,
        price,
        description_html
    )

    return html,200


# ============================================================
# بازار جدید
# ============================================================

def _lucas_explore_page():

    c=_lucas_ads_db()

    ads=c.execute("""
        SELECT *
        FROM ads
        ORDER BY id DESC
    """).fetchall()

    c.close()

    cards=""

    for ad in ads:

        images=_lucas_images(ad)

        number=_lucas_get(
            ad,
            "ad_number",
            "id"
        )

        account=_lucas_get(
            ad,
            "account_name",
            "title"
        )

        th=_lucas_get(
            ad,
            "townhall",
            "town_hall",
            "th"
        )

        bh=_lucas_get(
            ad,
            "builderhall",
            "builder_hall",
            "bh"
        )

        price=_lucas_get(
            ad,
            "price"
        )

        listing=_lucas_get(
            ad,
            "listing_code"
        )

        if images:

            pic="""
<img src="/uploads/%s">
""" % images[0]

        else:

            pic="""
<div class="noimg">
🎮
</div>
"""

        cards += """
<article class="ad-card">

<div class="pic">
%s
</div>

<div class="body">

<div class="number">
#%s
</div>

<div class="title">
%s
</div>

<div class="mini">

<div>
<span>تاون هال</span>
<b>TH %s</b>
</div>

<div>
<span>بیلدر هال</span>
<b>BH %s</b>
</div>

</div>

<div class="price">
%s تومان
</div>

<a class="view" href="/ad/%s">
👁 مشاهده آگهی
</a>

</div>

</article>
""" % (
            pic,
            number,
            account,
            th,
            bh,
            price,
            listing
        )

    if not cards:

        cards="""
<div class="empty">
📦
<h2>هنوز آگهی‌ای ثبت نشده</h2>
</div>
"""

    html="""
<!doctype html>

<html lang="fa" dir="rtl">

<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>LUCAS SHOP | آگهی‌ها</title>

<style>

*{
box-sizing:border-box;
}

body{
margin:0;
background:#050912;
color:#fff;
font-family:Tahoma,Arial,sans-serif;
}

.nav{
padding:13px;
border-bottom:1px solid #18263b;
display:flex;
justify-content:space-between;
align-items:center;
max-width:1180px;
margin:auto;
gap:10px;
}

.logo{
font-size:21px;
font-weight:900;
}

.logo span{
color:#3b82f6;
}

.btn{
display:inline-block;
padding:9px 12px;
border-radius:11px;
background:#0d1728;
border:1px solid #243650;
font-weight:800;
color:white;
text-decoration:none;
}

.primary{
background:#2563eb;
}

.wrap{
max-width:1180px;
margin:auto;
padding:20px 12px 45px;
}

.hero{
padding:21px;
border:1px solid #1d3150;
border-radius:21px;
background:
radial-gradient(
circle at 85%% 20%%,
rgba(37,99,235,.20),
transparent 35%%
),
linear-gradient(145deg,#0b1424,#070c16);
margin-bottom:18px;
}

.hero h1{
margin:0 0 7px;
font-size:27px;
}

.hero p{
margin:0;
color:#94a3b8;
line-height:1.8;
}

.grid{
display:grid;
grid-template-columns:
repeat(auto-fill,minmax(250px,1fr));
gap:13px;
}

.ad-card{
overflow:hidden;
border:1px solid #1d304a;
border-radius:18px;
background:#080f1c;
}

.pic{
height:170px;
background:#03070d;
overflow:hidden;
}

.pic img{
width:100%%;
height:100%%;
object-fit:cover;
display:block;
}

.noimg{
height:100%%;
display:flex;
align-items:center;
justify-content:center;
font-size:42px;
color:#64748b;
}

.body{
padding:12px;
}

.number{
display:inline-block;
padding:6px 11px;
border-radius:10px;
background:#0d1b31;
border:1px solid #28558d;
color:#60a5fa;
font-weight:900;
margin-bottom:8px;
}

.title{
font-size:17px;
font-weight:900;
margin-bottom:8px;
white-space:nowrap;
overflow:hidden;
text-overflow:ellipsis;
}

.mini{
display:grid;
grid-template-columns:1fr 1fr;
gap:6px;
}

.mini div{
padding:8px;
background:#0e1727;
border:1px solid #1a2940;
border-radius:9px;
}

.mini span{
display:block;
color:#94a3b8;
font-size:11px;
}

.mini b{
display:block;
margin-top:3px;
font-size:13px;
}

.price{
font-size:18px;
font-weight:900;
color:#60a5fa;
margin:10px 0;
}

.view{
display:block;
padding:10px;
border-radius:10px;
background:#2563eb;
text-align:center;
font-weight:900;
color:white;
text-decoration:none;
}

.empty{
text-align:center;
padding:55px 20px;
border:1px dashed #263650;
border-radius:18px;
color:#94a3b8;
}

@media(max-width:600px){

.grid{
grid-template-columns:1fr;
}

.pic{
height:165px;
}

}

</style>

</head>

<body>

<div class="nav">

<a class="logo" href="/">
LUCAS <span>SHOP</span>
</a>

<div style="display:flex;gap:6px;flex-wrap:wrap">

<a class="btn" href="/">
خانه
</a>

<a class="btn primary" href="/create-ad">
📢 ثبت آگهی
</a>

<a class="btn" href="/account">
👤 حساب من
</a>

</div>

</div>

<main class="wrap">

<section class="hero">

<h1>
📢 آگهی‌های LUCAS SHOP
</h1>

<p>
آگهی‌های فروش اکانت کلش آف کلنز را مشاهده کنید.
</p>

</section>

<div class="grid">

%s

</div>

</main>

</body>

</html>
""" % cards

    return html,200


# ============================================================
# کنترل نهایی آدرس‌ها
# ============================================================

@app.before_request
def _lucas_final_ads_intercept():

    path=request.path

    # بازار
    if path=="/explore":
        html,status=_lucas_explore_page()
        return html,status

    # نمایش آگهی
    if path.startswith("/ad/"):

        code=path[len("/ad/"):]

        if code:
            html,status=_lucas_ad_page(code)
            return html,status

    return None


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

