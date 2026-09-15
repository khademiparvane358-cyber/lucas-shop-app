from flask import Flask, request, redirect, render_template_string, session, send_from_directory
import sqlite3
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

def clean_price(v):
    v=str(v or "")
    trans=str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩","01234567890123456789")
    v=v.translate(trans).replace(",","").replace("٬","").replace(" ","").strip()
    try:
        return int(v)
    except:
        return 0


def safe_price(value):
    try:
        value = str(value).replace(",", "").replace("٬", "").strip()
        return int(value or "0")
    except:
        return 0


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
    if request.method == "GET":
        return sell_page("")

    account_name=request.form.get("account_name","").strip()
    account_tag=request.form.get("account_tag","").strip()
    townhall=request.form.get("townhall","").strip()
    builder_hall=request.form.get("builder_hall","").strip() or "BH1"
    level=request.form.get("level","").strip() or "1"
    price=clean_price(request.form.get("price",""))
    description=request.form.get("description","").strip()
    telegram=request.form.get("telegram","").strip()

    if not account_name:
        return sell_page("نام اکانت را وارد کنید.")
    if not account_tag:
        return sell_page("تگ اکانت را وارد کنید.")
    if not townhall:
        return sell_page("تاون هال را انتخاب کنید.")
    if price <= 0:
        return sell_page("قیمت را درست وارد کنید.")

    images=save_images()
    heroes={}
    for _,key in HEROES:
        heroes[key]=request.form.get(key,"ندارد").strip() or "ندارد"

    now=int(time.time())

    data={
        "account_name":account_name,
        "account_tag":account_tag,
        "townhall":townhall,
        "builderhall":builder_hall,
        "king":heroes.get("barbarian_king","ندارد"),
        "queen":heroes.get("archer_queen","ندارد"),
        "prince":"ندارد",
        "warden":heroes.get("grand_warden","ندارد"),
        "royal":heroes.get("royal_champion","ندارد"),
        "duke":"ندارد",
        "name_change":"ندارد",
        "name_change_gems":"0",
        "supercell_id":"",
        "account_level":level,
        "price":price,
        "seller":telegram,
        "description":description,
        "image1":images[0],
        "image2":images[1],
        "image3":images[2],
        "status":"pending",
        "featured":0,
        "views":0,
        "created_at":now,
        "published":0,
        "th":townhall,
        "bh":builder_hall,
        "supercell":"",
        "created":now,
        "title":account_name,
        "category":"اکانت کلش",
        "level":level,
        "barbarian_king":heroes.get("barbarian_king","ندارد"),
        "archer_queen":heroes.get("archer_queen","ندارد"),
        "grand_warden":heroes.get("grand_warden","ندارد"),
        "royal_champion":heroes.get("royal_champion","ندارد"),
        "telegram":telegram,
        "builder_hall":builder_hall
    }

    con=db()
    schema=con.execute("PRAGMA table_info(ads)").fetchall()
    cols=[r[1] for r in schema if r[1]!="id"]
    required=[r[1] for r in schema if r[1]!="id" and r[3]==1 and r[4] is None]

    for col in required:
        if col not in data:
            data[col]=""

    cols=[c for c in cols if c in data]
    vals=[data[c] for c in cols]

    sql="INSERT INTO ads ("+",".join(cols)+") VALUES ("+(",".join(["?"]*len(cols)))+")"

    try:
        con.execute(sql,vals)
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        return sell_page("ثبت آگهی انجام نشد؛ اطلاعات واردشده را بررسی کنید.")
    finally:
        try:
            con.close()
        except:
            pass

    return redirect("/success")


def sell_page(error=""):
    return """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>LUCAS SHOP - ثبت آگهی</title>
<style>
body{margin:0;background:#080b12;color:white;font-family:Tahoma,Arial}
.box{max-width:700px;margin:20px auto;padding:20px;background:#111827;border-radius:20px}
h1{text-align:center}
label{display:block;margin:15px 0 7px;font-weight:bold}
input,textarea{width:100%;box-sizing:border-box;padding:13px;border-radius:10px;background:#080d16;color:white;border:1px solid #344155;font-size:15px}
textarea{min-height:100px}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}
button{padding:9px;border:1px solid #344155;border-radius:9px;background:#182132;color:white}
button.sel{background:#075985;border-color:#38bdf8}
.hero{margin-top:15px;padding:12px;background:#0b111c;border-radius:12px}
.levels{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;max-height:180px;overflow:auto}
.err{background:#7f1d1d;padding:10px;border-radius:10px;margin-bottom:15px}
.submit{width:100%;margin-top:20px;background:#16a34a;font-size:17px}
@media(max-width:500px){.grid{grid-template-columns:repeat(4,1fr)}.levels{grid-template-columns:repeat(6,1fr)}}
</style>
</head>
<body>
<div class="box">
<h1>🏪 LUCAS SHOP</h1>
<p style="text-align:center">ثبت آگهی فروش اکانت کلش آف کلنز</p>
ERROR

<form method="POST" enctype="multipart/form-data" autocomplete="off" onsubmit="this.querySelectorAll('input[type=text],input[type=number],input[type=tel],textarea').forEach(x=>x.setAttribute('autocomplete','off'));">

<label>🎮 نام اکانت</label>
<input name="account_name" autocomplete="off" required>

<label>🏷️ تگ اکانت</label>
<input name="account_tag" autocomplete="off" placeholder="#ABC123" required>

<label>🏰 تاون هال</label>
<input type="hidden" name="townhall" id="townhall">
<div class="grid">TH</div>

<label>🔨 Builder Hall</label>
<input type="hidden" name="builder_hall" id="builder_hall">
<div class="grid">BH</div>

<label>⭐ لول اکانت</label>
<input name="level" type="number" min="1">

HEROES

<label>💰 قیمت</label>
<input name="price" autocomplete="off" inputmode="numeric" required>

<label>📝 توضیحات</label>
<textarea name="description" autocomplete="off"></textarea>

<label>📱 آیدی تلگرام</label>
<input name="telegram" autocomplete="off" placeholder="@username">

<label>🖼️ تصاویر</label>
<input type="file" name="image1" accept="image/*">
<input type="file" name="image2" accept="image/*">
<input type="file" name="image3" accept="image/*">

<button class="submit" type="submit">🚀 ثبت آگهی</button>
</form>
</div>

<script>
document.querySelectorAll("button[data-target]").forEach(function(b){
    b.onclick=function(){
        var t=document.getElementById(this.dataset.target);
        t.value=this.dataset.value;
        document.querySelectorAll('button[data-target="'+this.dataset.target+'"]').forEach(function(x){x.classList.remove("sel")});
        this.classList.add("sel");
    };
});
</script>
</body>
</html>
"""

    th=""
    for i in range(1,19):
        th += f'<button type="button" data-target="townhall" data-value="TH{i}">TH{i}</button>'

    bh=""
    for i in range(1,11):
        bh += f'<button type="button" data-target="builder_hall" data-value="BH{i}">BH{i}</button>'

    hero_data=[
        ("👑 پادشاه بربرها","barbarian_king",110),
        ("🏹 ملکه کماندار","archer_queen",110),
        ("🧙 نگهبان بزرگ","grand_warden",85),
        ("⚔️ قهرمان سلطنتی","royal_champion",55)
    ]

    heroes=""
    for name,key,mx in hero_data:
        x=f'<div class="hero"><b>{name}</b><input type="hidden" id="{key}" name="{key}" value="ندارد"><div class="levels">'
        x+='<button type="button" data-target="'+key+'" data-value="ندارد">ندارد</button>'
        for n in range(1,mx+1):
            x+=f'<button type="button" data-target="{key}" data-value="{n}">{n}</button>'
        x+='</div></div>'
        heroes+=x

    err=f'<div class="err">{error}</div>' if error else ""

    return html.replace("ERROR",err).replace("TH",th).replace("BH",bh).replace("HEROES",heroes)


@app.route("/login",methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form.get("password","")==ADMIN_PASSWORD:
            session["admin"]=True
            return redirect("/admin")
        return render_template_string("""
        <html lang="fa" dir="rtl"><meta name="viewport" content="width=device-width,initial-scale=1">
        <body style="background:#07111f;color:white;font-family:Tahoma;text-align:center;padding:30px">
        <div style="max-width:400px;margin:auto;background:#0d1b2d;padding:25px;border-radius:20px">
        <h2>❌ رمز اشتباه است</h2>
        <a href="/login" style="color:#4da3ff">دوباره تلاش کن</a>
        </div></body></html>
        """)
    return render_template_string("""
    <html lang="fa" dir="rtl">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <body style="background:#07111f;color:white;font-family:Tahoma;padding:20px">
    <div style="max-width:420px;margin:70px auto;background:#0d1b2d;padding:25px;border-radius:22px">
    <h2 style="text-align:center">🔐 مدیریت LUCAS SHOP</h2>
    <form method="POST">
    <input type="password" name="password" placeholder="رمز مدیریت" required
    style="width:100%;box-sizing:border-box;padding:15px;border-radius:12px;background:#071321;color:white;border:1px solid #29415f">
    <button style="width:100%;margin-top:12px;padding:15px;border:0;border-radius:12px;background:#1683ff;color:white;font-weight:bold">
    ورود به مدیریت
    </button>
    </form>
    </div></body></html>
    """)

@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect("/login")

    con=db()
    rows=con.execute("""
        SELECT id,account_name,account_tag,townhall,builder_hall,
               price,status,description,image1,telegram
        FROM ads ORDER BY id DESC
    """).fetchall()
    con.close()

    cards=""
    for r in rows:
        aid,name,tag,th,bh,price,status,desc,img,tg=r

        if status=="pending":
            actions=(
                '<a href="/admin/approve/'+str(aid)+'" style="background:#159447;color:white;padding:10px 14px;border-radius:10px;text-decoration:none">✅ تأیید</a> '
                '<a href="/admin/reject/'+str(aid)+'" style="background:#b52b3b;color:white;padding:10px 14px;border-radius:10px;text-decoration:none">❌ رد</a>'
            )
        elif status=="approved":
            actions='<span style="color:#4ee39b">✅ منتشر شده</span>'
        else:
            actions='<span style="color:#ff7180">❌ رد شده</span>'

        picture=""
        if img:
            picture='<img src="/uploads/'+str(img)+'" style="width:100%;max-height:220px;object-fit:cover;border-radius:14px;margin-bottom:12px">'

        cards+=(
            '<div style="background:#0d1b2d;border:1px solid #203750;border-radius:20px;padding:16px;margin:15px 0">'
            +picture+
            '<h2>'+str(name or '')+'</h2>'
            '<p>🏷️ '+str(tag or '')+'</p>'
            '<p>🏰 '+str(th or '')+'　🔨 '+str(bh or '')+'</p>'
            '<p>💰 '+str(price or 0)+' تومان</p>'
            '<p>📱 '+str(tg or '')+'</p>'
            '<p>📌 '+str(status or '')+'</p>'
            '<form method="POST" action="/admin/price/'+str(aid)+'">'
            '<input name="price" autocomplete="off" value="'+str(price or 0)+'" inputmode="numeric" '
            'style="width:100%;box-sizing:border-box;padding:12px;border-radius:10px;background:#071321;color:white;border:1px solid #29415f">'
            '<button style="width:100%;margin-top:8px;padding:12px;border:0;border-radius:10px;background:#1683ff;color:white">💰 تغییر قیمت</button>'
            '</form>'
            '<div style="margin-top:12px">'+actions+'</div>'
            '</div>'
        )

    return render_template_string("""
    <!doctype html>
    <html lang="fa" dir="rtl">
    <head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>مدیریت LUCAS SHOP</title>
    </head>
    <body style="margin:0;background:#07111f;color:white;font-family:Tahoma;padding:15px">
    <div style="max-width:900px;margin:auto">
    <div style="background:#0d1b2d;padding:20px;border-radius:20px">
    <h1>⚙️ مدیریت LUCAS SHOP</h1>
    <p>تأیید، رد و تغییر قیمت آگهی‌ها</p>
    <a href="/admin/logout" style="color:#ff7180">🚪 خروج</a>
    </div>
    CARDS
    </div>
    </body>
    </html>
    """.replace("CARDS",cards))

@app.route("/admin/approve/<int:ad_id>")
def admin_approve(ad_id):
    if not session.get("admin"):
        return redirect("/login")
    con=db()
    con.execute("UPDATE ads SET status='approved',published=1 WHERE id=?",(ad_id,))
    con.commit()
    con.close()
    return redirect("/admin")

@app.route("/admin/reject/<int:ad_id>")
def admin_reject(ad_id):
    if not session.get("admin"):
        return redirect("/login")
    con=db()
    con.execute("UPDATE ads SET status='rejected',published=0 WHERE id=?",(ad_id,))
    con.commit()
    con.close()
    return redirect("/admin")

@app.route("/admin/price/<int:ad_id>",methods=["POST"])
def admin_change_price(ad_id):
    if not session.get("admin"):
        return redirect("/login")
    price=clean_price(request.form.get("price",""))
    if price>0:
        con=db()
        con.execute("UPDATE ads SET price=? WHERE id=?",(price,ad_id))
        con.commit()
        con.close()
    return redirect("/admin")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    print("""
================================
       LUCAS SHOP ONLINE
================================
http://127.0.0.1:8080
""")
    app.run(host="0.0.0.0", port=8080, debug=False)
