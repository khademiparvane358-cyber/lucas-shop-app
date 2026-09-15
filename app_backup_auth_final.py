from flask import render_template_string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import time
import secrets
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lucas.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

app = Flask(__name__)

# =========================================================
# LUCAS SHOP USER SYSTEM
# =========================================================

def create_user_tables():
    c = db()
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    c.commit()
    c.close()

try:
    create_user_tables()
except Exception:
    pass


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None

    c = db()
    user = c.execute(
        "SELECT id, username, created_at FROM accounts WHERE id=?",
        (uid,)
    ).fetchone()
    c.close()
    return user


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


@app.route("/create-ad", methods=["GET","POST"])
def create_ad():
    user=current_user()

    if not user:
        return redirect("/login")

    if request.method=="POST":

        title=request.form.get("title","").strip()
        price=request.form.get("price","").strip()
        description=request.form.get("description","").strip()

        if not title:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>عنوان آگهی را وارد کن.</div>"+ad_form()
            )

        if not price:
            return account_page(
                "ثبت آگهی",
                "<div class='error'>قیمت را وارد کن.</div>"+ad_form()
            )

        c=db()

        c.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                title TEXT,
                price TEXT,
                description TEXT
            )
        """)

        c.execute(
            "INSERT INTO ads(seller_id,title,price,description) VALUES(?,?,?,?)",
            (user[0],title,price,description)
        )

        c.commit()
        c.close()

        return redirect("/account")

    return account_page("ثبت آگهی",ad_form())


def ad_form(ad=None):
    title=ad[1] if ad else ""
    price=ad[2] if ad else ""
    description=ad[3] if ad else ""

    return f"""
<h1>ثبت آگهی جدید</h1>

<form method="POST">

<label>عنوان آگهی</label>
<input
 name="title"
 value="{title}"
 placeholder="عنوان آگهی"
 required>

<label>قیمت</label>
<input
 name="price"
 value="{price}"
 placeholder="مثلاً 500000"
 required>

<label>توضیحات</label>
<textarea
 name="description"
 placeholder="توضیحات کامل آگهی...">{description}</textarea>

<button type="submit">
ثبت آگهی
</button>

<a class="btn"
style="margin-right:8px;background:#202938"
href="/account">
انصراف
</a>

</form>
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


app.secret_key = secrets.token_hex(32)

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


def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    conn = db()
    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    conn.close()

    return user


@app.context_processor
def global_context():
    return {
        "current_user": current_user(),
        "site_name": get_setting("site_name", "NOVA"),
        "announcement": get_setting(
            "announcement",
            "به نسل جدید تجربه دیجیتال خوش آمدید"
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

    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "newest")

    conn = db()

    sql = """
        SELECT *
        FROM products
        WHERE active=1
    """

    params = []

    if q:
        sql += """
            AND (
                title LIKE ?
                OR description LIKE ?
                OR category LIKE ?
            )
        """

        term = f"%{q}%"
        params.extend([term, term, term])

    if category:
        sql += " AND category=?"
        params.append(category)

    if sort == "cheap":
        sql += " ORDER BY price ASC"

    elif sort == "expensive":
        sql += " ORDER BY price DESC"

    elif sort == "popular":
        sql += " ORDER BY views DESC"

    else:
        sql += " ORDER BY id DESC"

    products = conn.execute(sql, params).fetchall()

    categories = conn.execute("""
        SELECT DISTINCT category
        FROM products
        WHERE active=1
        ORDER BY category
    """).fetchall()

    conn.close()

    return render_template(
        "explore.html",
        products=products,
        categories=categories,
        q=q,
        selected_category=category,
        sort=sort
    )


# ============================================================
# PRODUCT
# ============================================================

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
        port=8080,
        debug=False
    )
