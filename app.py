ADMIN_ID = 1
from flask import render_template_string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import time
import secrets
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from telegram_system import ensure_telegram_db, send_ad_to_channel, send_sold_to_channel, delete_telegram_posts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lucas.db")

# ============================================================
# LUCAS TELEGRAM SYSTEM
# ============================================================
_telegram_init_conn = sqlite3.connect(DB_PATH)
ensure_telegram_db(_telegram_init_conn)
_telegram_init_conn.close()

UPLOAD_DIR = "/tmp/lucas_uploads"


app = Flask(__name__)

from flask import send_from_directory

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


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


def account_page(title, body):
    return render_template_string("""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} — LUCAS SHOP</title>
<style>
*{box-sizing:border-box}
body{
margin:0;
background:#03050a;
color:#f5f7ff;
font-family:Tahoma,Arial,sans-serif;
min-height:100vh;
}
.wrap{
width:min(1050px,92%);
margin:auto;
padding:35px 0 80px;
}
.top{
display:flex;
align-items:center;
justify-content:space-between;
margin-bottom:35px;
}
.logo{
font-size:25px;
font-weight:900;
color:white;
text-decoration:none;
}
.logo span{color:#287cff}
.back{
color:#aeb9cc;
text-decoration:none;
}
.panel{
background:linear-gradient(145deg,#0c121d,#070a11);
border:1px solid rgba(255,255,255,.08);
border-radius:28px;
padding:35px;
box-shadow:0 25px 80px rgba(0,0,0,.4);
}
h1{
margin:0 0 25px;
font-size:36px;
}
input,select,textarea{
width:100%;
padding:15px;
margin:8px 0 15px;
border-radius:13px;
border:1px solid rgba(255,255,255,.1);
background:#080d16;
color:white;
outline:none;
font-size:15px;
}
textarea{min-height:130px;resize:vertical}
button,.btn{
display:inline-flex;
align-items:center;
justify-content:center;
padding:14px 20px;
border:0;
border-radius:13px;
background:linear-gradient(135deg,#287cff,#7657ff);
color:white;
font-weight:800;
cursor:pointer;
text-decoration:none;
}
.error{
background:rgba(255,77,112,.1);
border:1px solid rgba(255,77,112,.25);
color:#ff8098;
padding:13px;
border-radius:12px;
margin-bottom:15px;
}
.success{
background:rgba(50,229,139,.1);
border:1px solid rgba(50,229,139,.25);
color:#65efa5;
padding:13px;
border-radius:12px;
margin-bottom:15px;
}
.grid{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:15px;
margin:20px 0;
}
.stat{
padding:22px;
border:1px solid rgba(255,255,255,.07);
border-radius:18px;
background:rgba(255,255,255,.025);
}
.stat strong{
display:block;
font-size:30px;
margin-bottom:6px;
}
.stat span{color:#8490a5;font-size:13px}
.ad{
padding:20px;
margin:12px 0;
border:1px solid rgba(255,255,255,.07);
border-radius:18px;
background:#080d15;
}
.ad-title{
font-size:18px;
font-weight:800;
margin-bottom:8px;
}
.ad-meta{
color:#8290a5;
font-size:12px;
margin-bottom:14px;
}
.actions{
display:flex;
gap:8px;
flex-wrap:wrap;
}
.danger{
background:#d93655;
}
@media(max-width:650px){
.panel{padding:22px}
h1{font-size:28px}
.grid{grid-template-columns:1fr}
.top{gap:15px}
}
</style>
</head>
<body>
<div class="wrap">
<div class="top">
<a class="logo" href="/">LUCAS <span>SHOP</span></a>
<a class="back" href="/">صفحه اصلی ←</a>
</div>
<div class="panel">
{{ body|safe }}
</div>
</div>
</body>
</html>
""", title=title, body=body)




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


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","")

        if len(username)<3:
            return account_page(
                "ساخت حساب",
                "<div class='error'>نام کاربری باید حداقل ۳ حرف باشد.</div>"+register_form()
            )

        if len(password)<6:
            return account_page(
                "ساخت حساب",
                "<div class='error'>رمز عبور باید حداقل ۶ کاراکتر باشد.</div>"+register_form()
            )

        c=db()

        try:
            c.execute(
                "INSERT INTO accounts(username,password,created_at) VALUES(?,?,?)",
                (username,generate_password_hash(password),int(time.time()))
            )
            c.commit()

            user=c.execute(
                "SELECT id FROM accounts WHERE username=?",
                (username,)
            ).fetchone()

            c.close()

            session["user_id"]=user[0]
            session.permanent = True
            session["lucas_login_time"] = int(time.time())

            return redirect("/account")

        except sqlite3.IntegrityError:
            c.close()
            return account_page(
                "ساخت حساب",
                "<div class='error'>این نام کاربری قبلاً استفاده شده است.</div>"+register_form()
            )

    return account_page("ساخت حساب",register_form())


def register_form():
    return """
<h1>ساخت حساب جدید</h1>

<form method="POST">

<label>نام کاربری</label>
<input
 name="username"
 placeholder="مثلاً lucas123"
 autocomplete="username"
 required>

<label>رمز عبور</label>
<input
 type="password"
 name="password"
 placeholder="حداقل ۶ کاراکتر"
 autocomplete="new-password"
 required>

<button type="submit">
ساخت حساب
</button>

</form>

<div style="margin-top:20px;color:#8490a5">
قبلاً حساب ساخته‌ای؟
<a href="/login" style="color:#76aaff">ورود به حساب</a>
</div>
"""


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","")

        c=db()
        user=c.execute(
            "SELECT id,username,password FROM accounts WHERE username=?",
            (username,)
        ).fetchone()
        c.close()

        if not user or not check_password_hash(user[2],password):
            return account_page(
                "ورود",
                "<div class='error'>نام کاربری یا رمز عبور اشتباه است.</div>"+login_form()
            )

        session["user_id"]=user[0]
        session.permanent = True
        session["lucas_login_time"] = int(time.time())

        return redirect("/account")

    return account_page("ورود",login_form())


def login_form():
    return """
<h1>ورود به LUCAS SHOP</h1>

<form method="POST">

<label>نام کاربری</label>
<input
 name="username"
 autocomplete="username"
 required>

<label>رمز عبور</label>
<input
 type="password"
 name="password"
 autocomplete="current-password"
 required>

<button type="submit">
ورود
</button>

</form>

<div style="margin-top:20px;color:#8490a5">
حساب نداری؟
<a href="/register" style="color:#76aaff">ساخت حساب</a>
</div>
"""


@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect("/")


@app.route("/account")
def account():
    user=current_user()

    if not user:
        return redirect("/login")

    c=db()

    # تلاش برای استفاده از جدول ads قبلی
    try:
        ads=c.execute(
            "SELECT id,title,price,description FROM ads WHERE seller_id=? ORDER BY id DESC",
            (user[0],)
        ).fetchall()
    except Exception:
        ads=[]

    c.close()

    ads_html=""

    for ad in ads:
        ads_html += f"""
<div class="ad">
<div class="ad-title">{ad[1]}</div>
<div class="ad-meta">قیمت: {ad[2]}</div>
<div style="color:#8995a9;margin-bottom:14px">
{ad[3] or ''}
</div>
<div class="actions">
<a class="btn" href="/edit-ad/{ad[0]}">ویرایش آگهی</a>
<a class="btn danger"
href="/delete-ad/{ad[0]}"
onclick="return confirm('آگهی حذف شود؟')">
حذف
</a>
</div>
</div>
"""

    if not ads_html:
        ads_html="""
<div class="ad">
<div class="ad-title">هنوز آگهی‌ای ثبت نکرده‌ای</div>
<div class="ad-meta">
اولین آگهی خودت را در LUCAS SHOP ثبت کن.
</div>
<a class="btn" href="/create-ad">ثبت آگهی</a>
</div>
"""

    body=f"""
<h1>حساب کاربری</h1>

<div style="color:#8490a5;margin-bottom:20px">
خوش آمدی، <strong style="color:white">{user[1]}</strong>
</div>

<div class="grid">

<div class="stat">
<strong>{len(ads)}</strong>
<span>تعداد آگهی‌ها</span>
</div>

<div class="stat">
<strong>فعال</strong>
<span>وضعیت حساب</span>
</div>

<div class="stat">
<strong>LUCAS</strong>
<span>عضویت در فروشگاه</span>
</div>

</div>

<div class="actions" style="margin-bottom:30px">
<a class="btn" href="/create-ad">＋ ثبت آگهی جدید</a>
<a class="btn" href="/logout">خروج از حساب</a>
</div>

<h2>آگهی‌های من</h2>

{ads_html}
"""

    return account_page("حساب کاربری",body)





@app.route("/ad-submitted")
def ad_submitted():
    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>آگهی ثبت شد</title>
<style>
body{
    margin:0;
    background:#0b0f17;
    color:white;
    font-family:Tahoma,Arial,sans-serif;
    display:flex;
    align-items:center;
    justify-content:center;
    min-height:100vh;
}
.box{
    width:90%;
    max-width:520px;
    background:#151b27;
    border:1px solid #263247;
    border-radius:20px;
    padding:35px 20px;
    text-align:center;
    box-sizing:border-box;
}
.icon{font-size:55px;margin-bottom:15px}
h1{margin:10px 0 15px}
p{line-height:2;color:#cbd5e1}
.btn{
    display:inline-block;
    margin-top:20px;
    padding:13px 25px;
    border-radius:12px;
    background:#2563eb;
    color:white;
    text-decoration:none;
}
</style>
</head>
<body>
<div class="box">
<div class="icon">✅</div>
<h1>آگهی شما ثبت شد</h1>
<p>
آگهی شما با موفقیت ثبت شد.<br>
پس از تأیید ادمین، آگهی در سایت قرار می‌گیرد.
</p>
<a class="btn" href="/account">بازگشت به حساب کاربری</a>
</div>
</body>
</html>
""")

@app.route("/create-ad", methods=["GET","POST"])
def create_ad():

    user = current_user()

    if not user:
        return redirect(url_for("lucas_login", next="/create-ad"))

    lucas_prepare_ads_table()

    if request.method == "POST":

        account_name = request.form.get("account_name", "").strip()
        account_level = request.form.get("account_level", "").strip()
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

        error = ""

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
        elif len(images) > 6:
            error = "حداکثر ۶ عکس می‌توانید برای آگهی انتخاب کنید."

        try:
            town_hall = int(town_hall_raw)
            builder_hall = int(builder_hall_raw)
            barbarian_king = int(barbarian_king_raw or 0)
            archer_queen = int(archer_queen_raw or 0)
            grand_warden = int(grand_warden_raw or 0)
            royal_champion = int(royal_champion_raw or 0)
            price = int(
                price_raw.replace(",", "")
                .replace("٬", "")
                .replace(" ", "")
            )
        except Exception:
            error = "یکی از مقادیر واردشده صحیح نیست."
            town_hall = builder_hall = 0
            barbarian_king = archer_queen = grand_warden = royal_champion = 0
            price = 0

        if not error:
            if town_hall < 1 or town_hall > 18:
                error = "تاون هال باید بین ۱ تا ۱۸ باشد."
            elif builder_hall < 1 or builder_hall > 10:
                error = "بیلدر هال باید بین ۱ تا ۱۰ باشد."

        hero_max = {
            4:  {"barbarian_king":1,   "archer_queen":0,   "grand_warden":0,  "royal_champion":0},
            5:  {"barbarian_king":1,   "archer_queen":0,   "grand_warden":0,  "royal_champion":0},
            6:  {"barbarian_king":1,   "archer_queen":0,   "grand_warden":0,  "royal_champion":0},
            7:  {"barbarian_king":10,  "archer_queen":0,   "grand_warden":0,  "royal_champion":0},
            8:  {"barbarian_king":20,  "archer_queen":10,  "grand_warden":0,  "royal_champion":0},
            9:  {"barbarian_king":30,  "archer_queen":30,  "grand_warden":0,  "royal_champion":0},
            10: {"barbarian_king":40,  "archer_queen":40,  "grand_warden":0,  "royal_champion":0},
            11: {"barbarian_king":50,  "archer_queen":50,  "grand_warden":20, "royal_champion":0},
            12: {"barbarian_king":65,  "archer_queen":65,  "grand_warden":40, "royal_champion":0},
            13: {"barbarian_king":75,  "archer_queen":75,  "grand_warden":50, "royal_champion":25},
            14: {"barbarian_king":85,  "archer_queen":85,  "grand_warden":60, "royal_champion":30},
            15: {"barbarian_king":90,  "archer_queen":90,  "grand_warden":65, "royal_champion":40},
            16: {"barbarian_king":95,  "archer_queen":95,  "grand_warden":70, "royal_champion":45},
            17: {"barbarian_king":100, "archer_queen":100, "grand_warden":75, "royal_champion":50},
            18: {"barbarian_king":110, "archer_queen":110, "grand_warden":85, "royal_champion":55}
        }

        if not error and town_hall in hero_max:
            mx = hero_max[town_hall]

            if barbarian_king > mx["barbarian_king"]:
                error = f"حداکثر لول کینگ در TH{town_hall} برابر {mx['barbarian_king']} است."
            elif archer_queen > mx["archer_queen"]:
                error = f"حداکثر لول کویین در TH{town_hall} برابر {mx['archer_queen']} است."
            elif grand_warden > mx["grand_warden"]:
                error = f"حداکثر لول واردن در TH{town_hall} برابر {mx['grand_warden']} است."
            elif royal_champion > mx["royal_champion"]:
                error = f"حداکثر لول رویال چمپیون در TH{town_hall} برابر {mx['royal_champion']} است."

        allowed_gems = {
            "500", "1000", "1500", "2000",
            "2500", "3000", "3500", "3500 و بیشتر"
        }

        if not error and name_change == "رایگان":
            name_change_gems = ""

        if not error and name_change == "با جم":
            if name_change_gems not in allowed_gems:
                error = "مقدار جم انتخاب‌شده معتبر نیست."

        if not error and price < 0:
            error = "قیمت نمی‌تواند منفی باشد."

        saved_images = []

        if not error:

            os.makedirs(UPLOAD_DIR, exist_ok=True)

            allowed = {
                "png", "jpg", "jpeg", "webp", "gif"
            }

            for img in images[:6]:

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

                img.save(
                    os.path.join(UPLOAD_DIR, filename)
                )

                saved_images.append(filename)

            if len(saved_images) < 1 and not error:
                error = "حداقل یک عکس معتبر انتخاب کنید."

        if not error:

            image1 = saved_images[0] if len(saved_images) > 0 else ""
            image2 = saved_images[1] if len(saved_images) > 1 else ""
            image3 = saved_images[2] if len(saved_images) > 2 else ""
            image4 = saved_images[3] if len(saved_images) > 3 else ""
            image5 = saved_images[4] if len(saved_images) > 4 else ""
            image6 = saved_images[5] if len(saved_images) > 5 else ""

            conn = db()

            try:

                columns = {
                    row[1]
                    for row in conn.execute(
                        "PRAGMA table_info(ads)"
                    ).fetchall()
                }

                needed = {
                    "account_name": "TEXT DEFAULT ''",
                    "player_tag": "TEXT DEFAULT ''",
                    "supercell_id": "TEXT DEFAULT ''",
                    "supercell_status": "TEXT DEFAULT ''",
                    "name_change": "TEXT DEFAULT ''",
                    "name_change_gems": "TEXT DEFAULT ''",
                    "image2": "TEXT DEFAULT ''",
                    "image3": "TEXT DEFAULT ''",
                    "image4": "TEXT DEFAULT ''",
                    "image5": "TEXT DEFAULT ''",
                    "image6": "TEXT DEFAULT ''"
                }

                for col, definition in needed.items():
                    if col not in columns:
                        conn.execute(
                            f"ALTER TABLE ads ADD COLUMN {col} {definition}"
                        )

                title = account_name

                # شماره و کد آگهی
                row_no = conn.execute(
                    "SELECT COALESCE(MAX(ad_number),0)+1 FROM ads"
                ).fetchone()[0]

                listing_code = f"LS-{int(row_no):04d}"

                conn.execute("""
                    INSERT INTO ads (
                        seller_id,title,description,price,
                        town_hall,builder_hall,
                        barbarian_king,archer_queen,grand_warden,royal_champion,
                        created_at,image,telegram,
                        account_name,account_level,player_tag,supercell_id,supercell_status,
                        name_change,name_change_gems,
                        image2,image3,image4,image5,image6,
                        listing_code,approved,ad_number
                    )
                    VALUES (
                        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                    )
                """, (
                    user["id"],
                    title,
                    description,
                    price,
                    town_hall,
                    builder_hall,
                    barbarian_king,
                    archer_queen,
                    grand_warden,
                    royal_champion,
                    int(time.time()),
                    image1,
                    telegram,
                    account_name,
                    account_level,
                    player_tag,
                    "",
                    supercell_status,
                    name_change,
                    name_change_gems,
                    image2,
                    image3,
                    image4,
                    image5,
                    image6,
                    listing_code,
                    0,
                    int(row_no)
                ))

                conn.commit()
                conn.close()

                return redirect("/ad-submitted")

            except Exception as e:

                conn.rollback()
                conn.close()

                print("CREATE AD ERROR:", repr(e))

                error = "CREATE AD ERROR: " + str(e)

        with open("LUCAS_OLD_FULL_PAGE.html", encoding="utf-8") as f:
            template = f.read()
        return render_template_string(
            template,
            error=error,
            request=request
        )

    with open("LUCAS_OLD_FULL_PAGE.html", encoding="utf-8") as f:
        template = f.read()
    return render_template_string(
        template,
        error="",
        request=request
    )


def ad_form(ad=None):
    from flask import render_template_string
    with open("LUCAS_EXACT_FORM.html", encoding="utf-8") as f:
        template = f.read()
    return render_template_string(template, error="", request=request)



@app.route("/my-ads")
def my_ads():
    user=current_user()
    if not user:
        return redirect("/login")

    c=db()
    ads=c.execute(
        "SELECT * FROM ads WHERE seller_id=? ORDER BY id DESC",
        (user[0],)
    ).fetchall()
    c.close()

    html="<h1>📋 آگهی‌های من</h1>"

    if not ads:
        html+="<div class='card'>هنوز آگهی‌ای ثبت نکرده‌اید.</div>"
    else:
        for ad in ads:
            try:
                aid=ad["id"]
            except Exception:
                aid=ad[0]

            title=ad["title"] if "title" in ad.keys() else ad[1]
            price=ad["price"] if "price" in ad.keys() else ad[2]

            try:
                approved=ad["approved"]
            except Exception:
                approved=0

            status="🟢 تأیید شده" if approved==1 else "🟡 در انتظار تأیید ادمین"

            html+=f"""
            <div class='card'>
                <h2>{title}</h2>
                <p>💰 {int(price or 0):,} تومان</p>
                <p>{status}</p>
                <a class='btn' href='/edit-ad/{aid}'>✏️ ویرایش</a>
                <a class='btn' href='/delete-ad/{aid}'>🗑 حذف</a>
            </div>
            """

    html+="<a class='btn' href='/account'>↩️ بازگشت به حساب</a>"
    return account_page("آگهی‌های من",html)



@app.route("/admin")
def admin():
    user=current_user()

    if not user:
        return redirect("/login")

    if int(user[0]) != int(ADMIN_ID):
        return account_page(
            "دسترسی غیرمجاز",
            "<div class='error'>⛔ فقط ادمین سایت به این بخش دسترسی دارد.</div>"
        )

    c=db()

    ads=c.execute("""
        SELECT
            ads.*,
            accounts.username AS seller_username
        FROM ads
        LEFT JOIN accounts ON accounts.id = ads.seller_id
        ORDER BY ads.id DESC
    """).fetchall()

    c.close()

    html=r"""
<style>
.admin-wrap{
    width:100%;
}
.admin-head{
    text-align:center;
    margin-bottom:18px;
}
.admin-stats{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:10px;
    margin-bottom:18px;
}
.admin-stat{
    background:rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.10);
    border-radius:14px;
    padding:14px 8px;
    text-align:center;
}
.admin-stat b{
    display:block;
    font-size:21px;
    margin-top:5px;
}
.admin-ad{
    background:rgba(255,255,255,.055);
    border:1px solid rgba(255,255,255,.11);
    border-radius:18px;
    padding:15px;
    margin-bottom:15px;
    overflow:hidden;
}
.admin-img{
    width:100%;
    max-height:260px;
    object-fit:cover;
    border-radius:13px;
    margin-bottom:12px;
}
.admin-title{
    font-size:21px;
    font-weight:bold;
    margin-bottom:8px;
}
.admin-row{
    padding:6px 0;
    border-bottom:1px solid rgba(255,255,255,.06);
}
.admin-label{
    opacity:.65;
}
.admin-status{
    margin:10px 0;
    padding:9px;
    border-radius:10px;
    text-align:center;
    font-weight:bold;
}
.pending{
    background:rgba(255,180,0,.12);
}
.approved{
    background:rgba(0,200,100,.12);
}
.admin-actions{
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    margin-top:13px;
}
.admin-actions .btn{
    flex:1;
    min-width:130px;
    text-align:center;
}
.danger{
    background:#8b2020 !important;
}
</style>

<div class="admin-wrap">

<div class="admin-head">
    <h1>🛠 مدیریت سایت</h1>
    <p>مدیریت کامل آگهی‌های ثبت‌شده در LUCAS SHOP</p>
</div>
"""

    total=len(ads)
    pending_count=sum(1 for x in ads if int(x["approved"] or 0)==0)
    approved_count=sum(1 for x in ads if int(x["approved"] or 0)==1)

    html+=f"""
<div class="admin-stats">
    <div class="admin-stat">
        📦 آگهی‌ها
        <b>{total}</b>
    </div>
    <div class="admin-stat">
        🟡 در انتظار
        <b>{pending_count}</b>
    </div>
    <div class="admin-stat">
        🟢 تأیید شده
        <b>{approved_count}</b>
    </div>
</div>
"""

    if not ads:
        html+="<div class='card'>هنوز هیچ آگهی‌ای ثبت نشده است.</div>"

    else:
        for ad in ads:

            aid=ad["id"]
            title=ad["title"] or "بدون عنوان"
            price=int(ad["price"] or 0)

            seller_id=ad["seller_id"]
            seller_username=ad["seller_username"] or "حساب حذف‌شده"

            listing_code=ad["listing_code"] or "-"
            account_name=ad["account_name"] or "-"
            account_level=ad["account_level"] or "-"
            player_tag=ad["player_tag"] or "-"
            town_hall=ad["town_hall"] or "-"
            builder_hall=ad["builder_hall"] or "-"
            supercell_status=ad["supercell_status"] or "-"
            telegram=ad["telegram"] or "-"
            description=ad["description"] or "توضیحی ثبت نشده است"

            approved=int(ad["approved"] or 0)

            if approved==1:
                status_html="""
                <div class="admin-status approved">
                    🟢 آگهی تأیید شده و در سایت قابل نمایش است
                </div>
                """
                approve_button=""
            else:
                status_html="""
                <div class="admin-status pending">
                    🟡 این آگهی منتظر تأیید ادمین است
                </div>
                """
                approve_button=f"""
                <a class="btn" href="/admin/approve/{aid}">
                    ✅ تأیید و انتشار آگهی
                </a>
                """

            image_fields = [
                "image",
                "image2",
                "image3",
                "image4",
                "image5",
                "image6"
            ]

            image_html=""
            for field in image_fields:
                try:
                    img_name = ad[field] or ""
                except Exception:
                    img_name = ""

                if img_name:
                    image_html += f'<img class="admin-img" src="/uploads/{img_name}" alt="تصویر آگهی">'

            html+=f"""
<div class="admin-ad">

    {image_html}

    <div class="admin-title">
        🏷️ {title}
    </div>

    <div class="admin-row">
        💰 <span class="admin-label">قیمت:</span>
        <b>{price:,} تومان</b>
    </div>

    <div class="admin-row">
        🆔 <span class="admin-label">کد آگهی:</span>
        <b>{listing_code}</b>
    </div>

    <div class="admin-row">
        👤 <span class="admin-label">حساب ثبت‌کننده:</span>
        <b>{seller_username}</b>
    </div>

    <div class="admin-row">
        🔢 <span class="admin-label">شناسه حساب سایت:</span>
        <b>{seller_id}</b>
    </div>

    <div class="admin-row">
        🎮 <span class="admin-label">نام اکانت:</span>
        {account_name}
    </div>

    <div class="admin-row">
        📊 <span class="admin-label">لول اکانت:</span>
        {account_level}
    </div>

    <div class="admin-row">
        #️⃣ <span class="admin-label">Player Tag:</span>
        {player_tag}
    </div>

    <div class="admin-row">
        🏰 <span class="admin-label">Town Hall:</span>
        {town_hall}
    </div>

    <div class="admin-row">
        🏗️ <span class="admin-label">Builder Hall:</span>
        {builder_hall}
    </div>

    <div class="admin-row">
        🔐 <span class="admin-label">Supercell ID:</span>
        {supercell_status}
    </div>

    <div class="admin-row">
        📱 <span class="admin-label">تلگرام فروشنده:</span>
        {telegram}
    </div>

    {status_html}

    <div class="admin-row">
        📝 <span class="admin-label">توضیحات:</span><br>
        {description}
    </div>

    <div class="admin-actions">
        {approve_button}

        <a class="btn danger"
           href="/admin/delete/{aid}"
           onclick="return confirm('این آگهی برای همیشه حذف شود؟');">
            🗑️ حذف آگهی
        </a>
    </div>

</div>
"""

    html+="""<a class="btn" href="/account">↩️ بازگشت به حساب</a>
</div>"""

    return account_page("مدیریت سایت",html)


@app.route("/admin/approve/<int:ad_id>")
def admin_approve(ad_id):
    user = current_user()

    if not user:
        return redirect("/login")

    if int(user[0]) != int(ADMIN_ID):
        return "⛔ دسترسی غیرمجاز", 403

    c = db()

    try:
        ensure_telegram_db(c)

        ad = c.execute(
            "SELECT * FROM ads WHERE id=?",
            (ad_id,)
        ).fetchone()

        if not ad:
            c.close()
            return "آگهی پیدا نشد", 404

        edited = False

        try:
            edited = int(ad["telegram_edit_pending"] or 0) == 1
        except Exception:
            edited = False

        c.execute(
            "UPDATE ads SET approved=1, status='active', telegram_edit_pending=0 WHERE id=?",
            (ad_id,)
        )
        c.commit()

        ad = c.execute(
            "SELECT * FROM ads WHERE id=?",
            (ad_id,)
        ).fetchone()

        ok, message_id = send_ad_to_channel(
            ad,
            c,
            edited=edited
        )

        if not ok:
            print("⚠️ آگهی در سایت تأیید شد ولی انتشار تلگرام ناموفق بود.")

        c.close()

        return redirect("/admin")

    except Exception as e:
        print("ADMIN APPROVE ERROR:", repr(e))
        try:
            c.close()
        except Exception:
            pass

        return "خطا در تأیید آگهی: " + str(e), 500


@app.route("/admin/sold/<int:ad_id>")
def admin_sold(ad_id):
    user = current_user()

    if not user:
        return redirect("/login")

    if int(user[0]) != int(ADMIN_ID):
        return "⛔ دسترسی غیرمجاز", 403

    c = db()

    try:
        ensure_telegram_db(c)

        ad = c.execute(
            "SELECT * FROM ads WHERE id=?",
            (ad_id,)
        ).fetchone()

        if not ad:
            c.close()
            return "آگهی پیدا نشد", 404

        if str(ad["status"] or "active") == "sold":
            c.close()
            return redirect("/admin")

        c.execute(
            """
            UPDATE ads
            SET status='sold', approved=0
            WHERE id=?
            """,
            (ad_id,)
        )

        c.commit()

        ad = c.execute(
            "SELECT * FROM ads WHERE id=?",
            (ad_id,)
        ).fetchone()

        ok, message_id = send_sold_to_channel(
            ad,
            c
        )

        if not ok:
            print("⚠️ فروش در سایت ثبت شد ولی پیام فروش تلگرام ارسال نشد.")

        c.close()

        return redirect("/admin")

    except Exception as e:
        print("ADMIN SOLD ERROR:", repr(e))

        try:
            c.close()
        except Exception:
            pass

        return "خطا در ثبت فروش: " + str(e), 500


@app.route("/admin/delete/<int:ad_id>")
def admin_delete(ad_id):
    user=current_user()

    if not user:
        return redirect("/login")

    if int(user[0]) != int(ADMIN_ID):
        return "⛔ دسترسی غیرمجاز",403

    c=db()

    c.execute(
        "DELETE FROM ads WHERE id=?",
        (ad_id,)
    )

    c.commit()
    c.close()

    return redirect("/admin")


@app.route("/edit-ad/<int:ad_id>", methods=["GET", "POST"])
def edit_ad(ad_id):
    user = current_user()

    if not user:
        return redirect("/login")

    c = db()

    try:
        ad = c.execute(
            """
            SELECT id,title,price,description,approved
            FROM ads
            WHERE id=? AND seller_id=?
            """,
            (ad_id, user[0])
        ).fetchone()
    except Exception:
        ad = None

    if not ad:
        c.close()

        return account_page(
            "خطا",
            "<div class='error'>این آگهی وجود ندارد یا متعلق به حساب شما نیست.</div>"
            "<a class='btn' href='/account'>بازگشت</a>"
        )

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        price = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()

        try:
            price_value = int(price.replace(",", "").replace("٬", ""))
        except Exception:
            price_value = 0

        ensure_telegram_db(c)

        c.execute(
            """
            UPDATE ads
            SET
                title=?,
                price=?,
                description=?,
                approved=0,
                status='active',
                telegram_edit_pending=1,
                updated_at=?
            WHERE id=? AND seller_id=?
            """,
            (
                title,
                price_value,
                description,
                str(int(time.time())),
                ad_id,
                user[0]
            )
        )

        c.commit()
        c.close()

        return account_page(
            "آگهی ویرایش شد",
            "<div class='success'>"
            "✅ آگهی با موفقیت ویرایش شد.<br><br>"
            "آگهی برای تأیید مجدد ادمین ارسال شد."
            "</div>"
            "<a class='btn' href='/my-ads'>آگهی‌های من</a>"
        )

    c.close()

    return account_page(
        "ویرایش آگهی",
        "<h1>ویرایش آگهی</h1>" + ad_form(ad)
    )


@app.route("/delete-ad/<int:ad_id>")
def delete_ad(ad_id):
    user = current_user()

    if not user:
        return redirect("/login")

    c = db()

    try:
        ensure_telegram_db(c)

        ad = c.execute(
            """
            SELECT *
            FROM ads
            WHERE id=? AND seller_id=?
            """,
            (ad_id, user[0])
        ).fetchone()

        if not ad:
            c.close()
            return redirect("/account")

        delete_telegram_posts(ad_id, c)

        try:
            code = ad["listing_code"]

            if code:
                telegram_image = os.path.join(
                    BASE_DIR,
                    "uploads",
                    "telegram_generated",
                    f"{code}.jpg"
                )

                if os.path.exists(telegram_image):
                    os.remove(telegram_image)
        except Exception:
            pass

        c.execute(
            "DELETE FROM ads WHERE id=? AND seller_id=?",
            (ad_id, user[0])
        )

        c.commit()
        c.close()

    except Exception as e:
        print("USER DELETE ERROR:", repr(e))

        try:
            c.close()
        except Exception:
            pass

    return redirect("/account")


app.secret_key = "LUCAS_SHOP_SESSION_KEY_1598"


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
                image2,
                image3,
                image4,
                image5,
                image6,
                town_hall,
                builder_hall,
                barbarian_king,
                archer_queen,
                grand_warden,
                royal_champion,
                account_name,
                account_level,
                player_tag,
                supercell_id,
                supercell_status,
                name_change,
                name_change_gems,
                telegram,
                listing_code,
                created_at,
                approved,
                ad_number
            FROM ads
            WHERE approved = 1 AND COALESCE(status,'active')='active'
            ORDER BY ad_number DESC, id DESC
        """).fetchall()

        conn.close()

        ads = []

        for row in rows:
            item = dict(row)
            item["is_ad"] = True

            # شماره نمایشی آگهی: #1، #2، #3 ...
            try:
                item["display_number"] = int(item.get("ad_number") or 0)
            except Exception:
                item["display_number"] = 0

            ads.append(item)

        return render_template(
            "explore.html",
            products=ads,
            site_name="LUCAS SHOP"
        )

    except Exception as e:
        print("EXPLORE ADS ERROR:", e)

        try:
            conn.close()
        except Exception:
            pass

        return render_template(
            "explore.html",
            products=[],
            site_name="LUCAS SHOP"
        )


# ============================================================
# PUBLIC AD DETAILS
# ============================================================

@app.route("/ad/<listing_code>")
def ad_page(listing_code):

    con = db()

    ad = con.execute(
        "SELECT * FROM ads WHERE listing_code=? AND approved=1 AND COALESCE(status,'active')='active'",
        (listing_code,)
    ).fetchone()

    if not ad:
        con.close()
        return "آگهی پیدا نشد", 404

    try:
        con.execute(
            "UPDATE ads SET views=COALESCE(views,0)+1 WHERE listing_code=?",
            (listing_code,)
        )
        con.commit()
    except Exception:
        pass

    con.close()

    def val(key, default="—"):
        try:
            value = ad[key]
            if value not in (None, ""):
                return value
        except Exception:
            pass
        return default

    images = []

    for key in [
        "image",
        "image2",
        "image3",
        "image4",
        "image5",
        "image6"
    ]:
        try:
            if ad[key]:
                images.append("/uploads/" + str(ad[key]))
        except Exception:
            pass

    main_img = images[0] if images else ""

    thumbs = ""

    for index, img in enumerate(images):
        thumbs += f"""
        <button class="thumb" type="button"
                onclick="changeImage('{img}')"
                aria-label="تصویر {index + 1}">
            <img src="{img}" alt="تصویر آگهی">
        </button>
        """

    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>{{ val("account_name","آگهی LUCAS SHOP") }} | LUCAS SHOP</title>

<style>

*{
    box-sizing:border-box;
}

html{
    scroll-behavior:smooth;
}

body{
    margin:0;
    padding:14px;
    min-height:100vh;
    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(0,110,255,.25),
            transparent 35%
        ),
        #02050b;
    color:#fff;
    font-family:Tahoma,Arial,sans-serif;
}

.card{
    width:100%;
    max-width:1280px;
    margin:0 auto;
    background:
        linear-gradient(
            145deg,
            rgba(8,20,38,.98),
            rgba(2,7,15,.99)
        );
    border:1px solid #126cff;
    border-radius:22px;
    padding:14px;
    box-shadow:
        0 0 25px rgba(0,102,255,.35),
        inset 0 0 35px rgba(0,80,255,.08);
}

.header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    margin-bottom:14px;
    padding:10px 12px;
    border:1px solid #164775;
    border-radius:15px;
    background:#030a14;
}

.logo{
    font-size:21px;
    font-weight:900;
    color:#fff;
    text-shadow:0 0 12px #1680ff;
}

.badge{
    padding:7px 11px;
    border:1px solid #1680ff;
    border-radius:10px;
    color:#55adff;
    font-size:13px;
    font-weight:bold;
}

.content{
    display:grid;
    grid-template-columns:1.35fr 1fr;
    gap:14px;
    direction:ltr;
}

.photos{
    direction:ltr;
    min-height:700px;
    border:1px solid #1680ff;
    border-radius:18px;
    padding:12px;
    background:
        radial-gradient(
            circle at 50% 80%,
            rgba(0,100,255,.25),
            transparent 40%
        ),
        #02050b;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
}

.main-wrap{
    width:100%;
    min-height:560px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:15px;
    overflow:hidden;
    background:#010307;
    touch-action:pan-x;
    position:relative;
}

.main-wrap.swipe-gallery{
    overflow:hidden;
}

.main-img{
    user-select:none;
    -webkit-user-drag:none;
}

.main-img{
    width:100%;
    max-height:650px;
    object-fit:contain;
    border-radius:12px;
    cursor:pointer;
    transition:transform .2s ease;
}

.main-img:hover{
    transform:scale(1.01);
}

.no-image{
    min-height:500px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#60748b;
    font-size:18px;
}

.thumbs{
    width:100%;
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    justify-content:center;
    margin-top:12px;
}

.thumb{
    width:76px;
    height:62px;
    padding:2px;
    background:#030812;
    border:1px solid #126cff;
    border-radius:9px;
    cursor:pointer;
    overflow:hidden;
}

.thumb img{
    width:100%;
    height:100%;
    object-fit:cover;
    border-radius:6px;
}

.info{
    direction:rtl;
    display:flex;
    flex-direction:column;
    gap:7px;
}

.section-title{
    padding:12px 14px;
    border:1px solid #164775;
    border-radius:13px;
    background:#030912;
    color:#55adff;
    font-weight:900;
    text-align:center;
    margin-bottom:2px;
}

.row{
    min-height:55px;
    display:grid;
    grid-template-columns:43% 57%;
    align-items:center;
    background:
        linear-gradient(
            90deg,
            #07101d,
            #030811
        );
    border:1px solid #164775;
    border-radius:12px;
    overflow:hidden;
}

.label{
    height:100%;
    display:flex;
    align-items:center;
    padding:8px 11px;
    font-size:14px;
    font-weight:bold;
    border-left:1px solid #164775;
    color:#d7e9ff;
}

.value{
    padding:8px 11px;
    font-size:15px;
    font-weight:bold;
    word-break:break-word;
}

.code .value{
    color:#4da3ff;
}

.price{
    border:2px solid #1680ff;
    background:
        linear-gradient(
            90deg,
            #07182c,
            #031020
        );
}

.price .value{
    color:#36a4ff;
    font-size:20px;
}

.bottom{
    margin-top:14px;
    border:1px solid #164775;
    border-radius:16px;
    padding:15px;
    background:#030912;
}

.description-title{
    color:#55adff;
    font-weight:900;
    margin-bottom:8px;
}

.description{
    line-height:2;
    white-space:pre-wrap;
    word-break:break-word;
    color:#e9f4ff;
}

.contact{
    margin-top:14px;
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
}

.contact-box{
    border:1px solid #164775;
    border-radius:12px;
    padding:12px;
    text-align:center;
    background:#020811;
}

.contact-title{
    color:#40a5ff;
    font-weight:bold;
    margin-bottom:7px;
}

.contact-value{
    direction:ltr;
    font-weight:bold;
    color:#fff;
    word-break:break-all;
}

.actions{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin-top:14px;
}

.action{
    display:block;
    padding:13px;
    border-radius:12px;
    text-align:center;
    text-decoration:none;
    font-weight:bold;
    color:white;
    border:1px solid #126cff;
    background:#071a31;
}

.action.primary{
    background:#126cff;
}

.action:hover{
    filter:brightness(1.15);
}

.back{
    display:block;
    margin-top:10px;
    padding:14px;
    border-radius:12px;
    background:#126cff;
    color:white;
    text-decoration:none;
    text-align:center;
    font-weight:bold;
}

.meta{
    margin-top:10px;
    text-align:center;
    color:#70859d;
    font-size:12px;
}

@media(max-width:800px){

    body{
        padding:7px;
    }

    .card{
        padding:9px;
        border-radius:17px;
    }

    .header{
        flex-direction:column;
    }

    .content{
        grid-template-columns:1fr;
    }

    .photos{
        min-height:400px;
    }

    .main-wrap{
        min-height:330px;
    }

    .main-img{
        max-height:500px;
    }

    .no-image{
        min-height:300px;
    }

    .contact{
        grid-template-columns:1fr;
    }

    .actions{
        grid-template-columns:1fr;
    }

    .row{
        grid-template-columns:42% 58%;
    }

    .label,
    .value{
        font-size:13px;
    }
}

</style>

</head>

<body>

<div class="card">

    <div class="header">

        <div class="logo">
            🎮 LUCAS SHOP
        </div>

        <div class="badge">
            آگهی فروش اکانت
        </div>

    </div>

    <div class="content">

        <div class="photos">

            {% if main_img %}

            <div class="main-wrap">

                <img
                    id="mainImage"
                    src="{{ main_img }}"
                    class="main-img"
                    onclick="window.open(this.src,'_blank')"
                    alt="تصویر اکانت">

            </div>

            <div class="thumbs">
                {{ thumbs|safe }}
            </div>

            {% else %}

            <div class="main-wrap">
                <div class="no-image">
                    بدون تصویر
                </div>
            </div>

            {% endif %}

        </div>


        <div class="info">

            <div class="section-title">
                📋 مشخصات اکانت
            </div>

            <div class="row code">
                <div class="label">کد آگهی</div>
                <div class="value">
                    LS-{{ "%04d"|format(val("ad_number", 0)|int) }}
                </div>
            </div>

            <div class="row">
                <div class="label">نام اکانت</div>
                <div class="value">
                    {{ val("account_name") }}
                </div>
            </div>

            <div class="row">
                <div class="label">تاون هال</div>
                <div class="value">
                    {{ val("town_hall",val("townhall",val("th"))) }}
                </div>
            </div>

            <div class="row">
                <div class="label">بیلدر هال</div>
                <div class="value">
                    {{ val("builder_hall",val("builderhall",val("bh"))) }}
                </div>
            </div>

            <div class="row">
                <div class="label">کینگ بربر</div>
                <div class="value">
                    {{ val("king",val("barbarian_king")) }}
                </div>
            </div>

            <div class="row">
                <div class="label">آرچر کویین</div>
                <div class="value">
                    {{ val("queen",val("archer_queen")) }}
                </div>
            </div>

            <div class="row">
                <div class="label">گرند واردن</div>
                <div class="value">
                    {{ val("warden",val("grand_warden")) }}
                </div>
            </div>

            <div class="row">
                <div class="label">هیروی سلطنتی</div>
                <div class="value">
                    {{ val("royal",val("royal_champion")) }}
                </div>
            </div>

            <div class="row">
                <div class="label">تغییر نام</div>
                <div class="value">
                    {% set nc = val("name_change","") %}
                    {% set gems = val("name_change_gems","") %}

                    {% if gems not in ("", "—", None, 0, "0") %}
                        {{ gems }} جم
                    {% elif nc|string|lower in ("رایگان","free","آزاد","دارد","yes","true","1") %}
                        رایگان
                    {% elif nc not in ("", "—", None) and "رایگان" in nc|string %}
                        رایگان
                    {% else %}
                        {{ nc if nc not in ("", "—", None) else "رایگان" }}
                    {% endif %}
                </div>
            </div>

            <div class="row">
                <div class="label">Supercell ID</div>
                <div class="value">
                    {{ val("supercell_id",val("supercell")) }}
                </div>
            </div>

            <div class="row">
                <div class="label">لول اکانت</div>
                <div class="value">
                    {{ val("account_level",val("level")) }}
                </div>
            </div>

            <div class="row price">
                <div class="label">💰 قیمت</div>
                <div class="value">
                    {{ "{:,}".format(val("price", 0)|int) }} تومان
                </div>
            </div>

        </div>

    </div>


    <div class="bottom">

        <div class="description-title">
            📝 توضیحات فروشنده
        </div>

        <div class="description">
            {{ val("description") }}
        </div>

        <div class="contact">

            <div class="contact-box">

                <div class="contact-title">
                    👤 Admin
                </div>

                <div class="contact-value">
                    @LUCAS_SHOP_1
                </div>

            </div>

            <div class="contact-box">

                <div class="contact-title">
                    📢 Channel
                </div>

                <div class="contact-value">
                    @LUCAS_SHOP_LS1
                </div>

            </div>

        </div>

        <div class="actions">

            <a
                href="https://t.me/LUCAS_SHOP_1"
                class="action primary">
                💬 ارتباط با ادمین
            </a>

            <a
                href="https://t.me/LUCAS_SHOP_LS1"
                class="action">
                📢 ورود به کانال
            </a>

        </div>

        <a href="/explore" class="back">
            🏠 برگشت به فروشگاه
        </a>

        <div class="meta">
            LUCAS SHOP • فروش اکانت کلش آف کلنز
        </div>

    </div>

</div>

<script>

const galleryImages = {{ images|tojson }};
let galleryIndex = 0;

function changeImage(src){

    const image = document.getElementById("mainImage");

    if(image){
        image.src = src;

        const index = galleryImages.indexOf(src);
        if(index >= 0){
            galleryIndex = index;
        }
    }
}

(function(){

    const image = document.getElementById("mainImage");

    if(!image || galleryImages.length < 2)
        return;

    let startX = 0;
    let startY = 0;

    image.addEventListener("touchstart", function(e){

        if(!e.touches || !e.touches.length)
            return;

        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;

    }, {passive:true});

    image.addEventListener("touchend", function(e){

        if(!e.changedTouches || !e.changedTouches.length)
            return;

        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;

        const dx = endX - startX;
        const dy = endY - startY;

        if(Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy))
            return;

        if(dx < 0){
            galleryIndex =
                (galleryIndex + 1) % galleryImages.length;
        }else{
            galleryIndex =
                (galleryIndex - 1 + galleryImages.length)
                % galleryImages.length;
        }

        image.src = galleryImages[galleryIndex];

    }, {passive:true});

})();

</script>

</body>
</html>
""",
        ad=ad,
        val=val,
        main_img=main_img,
        thumbs=thumbs,
        images=images
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
        port=int(os.environ.get("PORT", 8080)),
        debug=False
    )
