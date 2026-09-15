from flask import Flask, request, redirect, render_template_string, session, send_from_directory
import sqlite3
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "LUCAS_SHOP_SECRET_1598"

DB = "lucas_shop.db"
UPLOAD = "uploads"
ADMIN_PASSWORD = "1598"

os.makedirs(UPLOAD, exist_ok=True)

HEROES = [
    ("شاه بربر", "barbarian_king"),
    ("ملکه کماندار", "archer_queen"),
    ("نگهبان بزرگ", "grand_warden"),
    ("قهرمان سلطنتی", "royal_champion"),
]

ALLOWED = {"png", "jpg", "jpeg", "webp"}

app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()

    con.execute("""
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT '',
        category TEXT DEFAULT 'اکانت کلش',
        townhall TEXT DEFAULT '',
        builder_hall TEXT DEFAULT '',
        level TEXT DEFAULT '',
        account_name TEXT DEFAULT '',
        account_tag TEXT DEFAULT '',
        price TEXT DEFAULT '',
        description TEXT DEFAULT '',
        seller TEXT DEFAULT '',
        telegram TEXT DEFAULT '',
        image1 TEXT DEFAULT '',
        image2 TEXT DEFAULT '',
        image3 TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        created INTEGER DEFAULT 0,
        views INTEGER DEFAULT 0,
        barbarian_king TEXT DEFAULT '',
        archer_queen TEXT DEFAULT '',
        grand_warden TEXT DEFAULT '',
        royal_champion TEXT DEFAULT ''
    )
    """)

    cols = [x["name"] for x in con.execute("PRAGMA table_info(ads)").fetchall()]

    new_cols = {
        "builder_hall": "TEXT DEFAULT ''",
        "account_name": "TEXT DEFAULT ''",
        "account_tag": "TEXT DEFAULT ''",
        "barbarian_king": "TEXT DEFAULT ''",
        "archer_queen": "TEXT DEFAULT ''",
        "grand_warden": "TEXT DEFAULT ''",
        "royal_champion": "TEXT DEFAULT ''"
    }

    for col, typ in new_cols.items():
        if col not in cols:
            con.execute(f"ALTER TABLE ads ADD COLUMN {col} {typ}")

    con.commit()
    con.close()


init_db()


STYLE = """
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{touch-action:manipulation}
body{
margin:0;background:#070b14;color:#fff;
font-family:Tahoma,Arial,sans-serif;direction:rtl
}
a{text-decoration:none;color:inherit}
.container{width:min(1100px,94%);margin:auto}
.nav{
position:sticky;top:0;z-index:20;
background:rgba(7,11,20,.96);
border-bottom:1px solid #172238
}
.nav-inner{
min-height:68px;display:flex;align-items:center;
justify-content:space-between;gap:10px
}
.logo{font-size:23px;font-weight:900;color:#55aaff}
.nav-links{display:flex;gap:8px}
.btn{
border:0;border-radius:12px;padding:12px 17px;
background:#18243a;color:#fff;font-weight:800;
cursor:pointer;display:inline-block;text-align:center
}
.btn-primary{background:linear-gradient(135deg,#1683ff,#0057d9)}
.btn-success{background:#16834d}
.btn-danger{background:#b52b3d}
.hero{
margin:28px 0;padding:35px 23px;
border:1px solid #1c2b45;border-radius:23px;
background:radial-gradient(circle at 80% 10%,rgba(0,130,255,.2),transparent 35%),#0b1322
}
.hero h1{margin:0 0 10px;font-size:36px}
.muted{color:#9eabc0;line-height:1.9}
.grid{
display:grid;grid-template-columns:repeat(3,1fr);gap:17px
}
.card{
background:#0d1524;border:1px solid #1b2a42;
border-radius:19px;overflow:hidden
}
.card-img{
width:100%;height:205px;object-fit:cover;background:#111a2a
}
.card-body{padding:17px}
.card-title{font-size:19px;font-weight:900}
.tags{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0}
.tag{
background:#16233a;border:1px solid #263956;
border-radius:9px;padding:7px 9px;font-size:13px
}
.price{color:#55aaff;font-size:21px;font-weight:900;margin:13px 0}
.form-box{
max-width:850px;margin:30px auto;
background:#0d1524;border:1px solid #1b2a42;
border-radius:22px;padding:22px
}
label{display:block;margin:17px 0 8px;font-weight:900}
input,textarea{
width:100%;border:1px solid #293a55;border-radius:12px;
background:#080e19;color:#fff;padding:14px;font-size:16px;outline:none
}
textarea{min-height:130px;resize:vertical}
.choice-title{margin-top:20px;margin-bottom:9px;font-weight:900}
.choices{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}
.choice{
border:1px solid #293a55;background:#111b2d;color:#fff;
padding:11px 5px;border-radius:11px;cursor:pointer;font-weight:800
}
.choice.selected{background:#1683ff;border-color:#52adff}
.hero-box{
margin-top:20px;padding:15px;border:1px solid #1e304b;
border-radius:17px;background:#09111e
}
.hero-name{font-weight:900;margin-bottom:9px}
.hero-levels{display:grid;grid-template-columns:repeat(10,1fr);gap:6px}
.hero-level{
border:1px solid #293a55;background:#111b2d;color:#fff;
border-radius:8px;padding:8px 2px;cursor:pointer;font-weight:bold
}
.hero-level.selected{background:#1683ff;border-color:#54b0ff}
.images{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.notice{
padding:14px;border-radius:13px;background:#101c2e;
border:1px solid #20334f;margin-bottom:15px
}
.error{color:#ff7785}
.detail{max-width:900px;margin:30px auto}
.detail-images{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.detail-images img{
width:100%;height:270px;object-fit:cover;border-radius:15px
}
.info-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:20px 0}
.info{
background:#101a2b;border:1px solid #1e3049;
padding:14px;border-radius:13px
}
.admin-row{
background:#101a2b;border:1px solid #1e3049;
border-radius:15px;padding:15px;margin-bottom:12px
}
footer{padding:45px 0;text-align:center;color:#66758d}

@media(max-width:800px){
.grid{grid-template-columns:repeat(2,1fr)}
.choices{grid-template-columns:repeat(4,1fr)}
.hero-levels{grid-template-columns:repeat(8,1fr)}
}

@media(max-width:550px){
.nav-inner{min-height:60px}
.logo{font-size:20px}
.nav-links .btn{padding:9px 11px;font-size:12px}
.hero{padding:25px 17px}
.hero h1{font-size:28px}
.grid{grid-template-columns:1fr}
.choices{grid-template-columns:repeat(3,1fr)}
.hero-levels{grid-template-columns:repeat(6,1fr)}
.images{grid-template-columns:1fr}
.info-grid{grid-template-columns:1fr}
.detail-images{grid-template-columns:1fr}
.detail-images img{height:240px}
}
</style>
"""

NAV = """
<div class="nav">
<div class="container nav-inner">
<a class="logo" href="/">LUCAS SHOP</a>
<div class="nav-links">
<a class="btn" href="/">خانه</a>
<a class="btn btn-primary" href="/sell">ثبت آگهی</a>
<a class="btn" href="/login">مدیریت</a>
</div>
</div>
</div>
"""


def page(title, body, script=""):
    return f"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{title} | LUCAS SHOP</title>
{STYLE}
</head>
<body>
{NAV}
<main class="container">
{body}
</main>
<footer>LUCAS SHOP</footer>
{script}
</body>
</html>
"""


@app.route("/")
def home():
    con = db()

    q = request.args.get("q","").strip()
    th = request.args.get("th","").strip()

    sql = "SELECT * FROM ads WHERE status='approved'"
    params = []

    if q:
        sql += " AND (account_name LIKE ? OR account_tag LIKE ?)"
        x = f"%{q}%"
        params += [x,x]

    if th:
        sql += " AND townhall=?"
        params.append(th)

    sql += " ORDER BY id DESC"

    ads = con.execute(sql,params).fetchall()
    con.close()

    cards = ""

    for ad in ads:
        if ad["image1"]:
            img = f'<img class="card-img" src="/uploads/{ad["image1"]}">'
        else:
            img = '<div class="card-img"></div>'

        cards += f"""
<a href="/ad/{ad['id']}" class="card">
{img}
<div class="card-body">
<div class="card-title">
{ad["account_name"] or "اکانت کلش"}
</div>
<div class="tags">
<span class="tag">🏰 {ad["townhall"] or "-"}</span>
<span class="tag">🔨 {ad["builder_hall"] or "-"}</span>
<span class="tag">⭐ لول {ad["level"] or "-"}</span>
</div>
<div class="muted">{ad["account_tag"] or ""}</div>
<div class="price">💰 {ad["price"] or "-"}</div>
</div>
</a>
"""

    if not cards:
        cards = '<div class="notice">هنوز آگهی تأییدشده‌ای وجود ندارد.</div>'

    body = f"""
<section class="hero">
<h1>🔥 LUCAS SHOP</h1>
<p>خرید و فروش اکانت‌های کلش آف کلنز</p>
<a class="btn btn-primary" href="/sell">➕ ثبت آگهی جدید</a>
</section>

<form class="notice" method="get">
<input name="q" value="{q}" placeholder="🔎 نام اکانت یا تگ...">
<br><br>
<div class="choices">
"""

    for i in range(1,19):
        selected = "selected" if th == f"TH{i}" else ""
        body += f"""
<button type="button"
class="choice {selected}"
onclick="location.href='/?th=TH{i}'">
TH{i}
</button>
"""

    body += """
</div>
<br>
<button class="btn btn-primary" type="submit">جستجو</button>
<a class="btn" href="/">پاک کردن</a>
</form>

<div class="grid">
""" + cards + """
</div>
"""

    return page("خانه",body)


def save_images():
    images=[]

    for field in ["image1","image2","image3"]:
        f=request.files.get(field)

        if f and f.filename:
            ext=f.filename.rsplit(".",1)[-1].lower()

            if ext in ALLOWED:
                filename=str(int(time.time()*1000000))+"_"+secure_filename(f.filename)
                f.save(os.path.join(UPLOAD,filename))
                images.append(filename)
            else:
                images.append("")
        else:
            images.append("")

    return images

@app.route("/sell", methods=["GET", "POST"])
def sell():
    error = ""

    if request.method == "POST":
        account_name = request.form.get("account_name", "").strip()
        account_tag = request.form.get("account_tag", "").strip()
        townhall = request.form.get("townhall", "").strip()
        builder_hall = request.form.get("builder_hall", "").strip() or "BH1"
        level = request.form.get("level", "").strip() or "1"
        price = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()
        telegram = request.form.get("telegram", "").strip()

        if not account_name:
            error = "نام اکانت را وارد کنید."
        elif not account_tag:
            error = "تگ اکانت را وارد کنید."
        elif not townhall:
            error = "تاون هال را انتخاب کنید."
        elif not price:
            error = "قیمت را وارد کنید."

        if error:
            return sell_page(error)

        images = save_images()

        heroes = {}
        for _, key in HEROES:
            heroes[key] = request.form.get(key, "ندارد").strip() or "ندارد"

        con = db()

        con.execute("""
            INSERT INTO ads (
                account_name,
                account_tag,
                townhall,
                builderhall,
                king,
                queen,
                prince,
                warden,
                royal,
                duke,
                name_change,
                name_change_gems,
                supercell_id,
                account_level,
                price,
                seller,
                description,
                image1,
                image2,
                image3,
                status,
                featured,
                views,
                created_at,
                published,
                th,
                bh,
                supercell,
                created,
                title,
                category,
                level,
                barbarian_king,
                archer_queen,
                grand_warden,
                royal_champion,
                telegram,
                builder_hall
            )
            VALUES (
                ?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?
            )
        """, (
            account_name,
            account_tag,
            townhall,
            builder_hall,

            heroes.get("barbarian_king", "ندارد"),
            heroes.get("archer_queen", "ندارد"),
            "ندارد",
            heroes.get("grand_warden", "ندارد"),
            heroes.get("royal_champion", "ندارد"),
            "ندارد",

            "ندارد",
            "0",
            "",
            level,
            price,
            "",
            description,

            images[0],
            images[1],
            images[2],

            "pending",
            0,
            0,
            int(time.time()),
            0,

            townhall,
            builder_hall,
            "",
            int(time.time()),

            account_name,
            "اکانت کلش",
            level,

            heroes.get("barbarian_king", "ندارد"),
            heroes.get("archer_queen", "ندارد"),
            heroes.get("grand_warden", "ندارد"),
            heroes.get("royal_champion", "ندارد"),

            telegram,
            builder_hall
        ))

        con.commit()
        con.close()

        return redirect("/success")

    return sell_page(error)

if __name__ == "__main__":
    print("""
================================
       LUCAS SHOP ONLINE
================================
http://127.0.0.1:8080
""")
    app.run(host="0.0.0.0", port=8080, debug=False)
