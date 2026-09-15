from flask import Flask, request, redirect, render_template_string, session, send_from_directory
import sqlite3, os, time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "LUCAS_SHOP_SECRET_1598"

DB = "lucas_shop.db"
UPLOAD = "uploads"
ADMIN_PASSWORD = "1598"

os.makedirs(UPLOAD, exist_ok=True)

ALLOWED = {"jpg","jpeg","png","webp"}

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()

    con.execute("""
    CREATE TABLE IF NOT EXISTS ads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_name TEXT DEFAULT '',
        account_tag TEXT DEFAULT '',
        townhall TEXT DEFAULT '',
        builderhall TEXT DEFAULT '',
        king TEXT DEFAULT '',
        queen TEXT DEFAULT '',
        warden TEXT DEFAULT '',
        royal TEXT DEFAULT '',
        name_change TEXT DEFAULT '',
        name_change_gems TEXT DEFAULT '',
        supercell_id TEXT DEFAULT '',
        account_level TEXT DEFAULT '',
        price TEXT DEFAULT '',
        seller TEXT DEFAULT '',
        description TEXT DEFAULT '',
        image1 TEXT DEFAULT '',
        image2 TEXT DEFAULT '',
        image3 TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        featured INTEGER DEFAULT 0,
        views INTEGER DEFAULT 0,
        created_at TEXT DEFAULT '',
        published INTEGER DEFAULT 0,
        th TEXT DEFAULT '',
        bh TEXT DEFAULT '',
        supercell TEXT DEFAULT '',
        created TEXT DEFAULT '',
        title TEXT DEFAULT '',
        category TEXT DEFAULT 'اکانت کلش',
        level TEXT DEFAULT '',
        barbarian_king TEXT DEFAULT '',
        archer_queen TEXT DEFAULT '',
        grand_warden TEXT DEFAULT '',
        royal_champion TEXT DEFAULT '',
        telegram TEXT DEFAULT '',
        builder_hall TEXT DEFAULT ''
    )
    """)

    con.commit()
    con.close()

init_db()

def save_images():
    result = []

    for field in ["image1","image2","image3"]:
        f = request.files.get(field)

        if f and f.filename:
            ext = f.filename.rsplit(".",1)[-1].lower()

            if ext in ALLOWED:
                filename = (
                    str(int(time.time()*1000000))
                    + "_"
                    + secure_filename(f.filename)
                )

                f.save(os.path.join(UPLOAD, filename))
                result.append(filename)
            else:
                result.append("")
        else:
            result.append("")

    return result


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD, filename)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    con = db()

    ads = con.execute("""
        SELECT * FROM ads
        WHERE status='approved' OR published=1
        ORDER BY id DESC
    """).fetchall()

    con.close()

    cards = ""

    for ad in ads:

        img = ""

        if ad["image1"]:
            img = f"""
            <img src="/uploads/{ad['image1']}"
                 style="
                 width:100%;
                 height:230px;
                 object-fit:cover;
                 border-radius:15px 15px 0 0;
                 ">
            """
        else:
            img = """
            <div style="
            height:230px;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#60748b;
            ">
            بدون تصویر
            </div>
            """

        cards += f"""
        <a href="/ad/{ad['id']}" class="card">

            {img}

            <div class="card-body">

                <div class="ad-title">
                    {ad["account_name"] or "اکانت کلش"}
                </div>

                <div class="mini">
                    🏰 {ad["townhall"] or ad["th"] or "—"}
                    &nbsp;&nbsp;
                    🛠 {ad["builderhall"] or ad["bh"] or "—"}
                </div>

                <div class="price">
                    💰 {ad["price"] or "توافقی"} تومان
                </div>

            </div>

        </a>
        """

    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>LUCAS SHOP</title>

<style>

*{
box-sizing:border-box
}

body{
margin:0;
background:#030812;
color:white;
font-family:Tahoma,Arial;
padding:15px
}

.container{
max-width:1100px;
margin:auto
}

.header{
text-align:center;
padding:25px 10px
}

.logo{
font-size:35px;
font-weight:900;
color:#1680ff;
text-shadow:0 0 20px #0066ff
}

.sub{
color:#8297ae;
margin-top:8px
}

.actions{
display:flex;
gap:10px;
margin-bottom:20px
}

.actions a{
flex:1;
text-align:center;
padding:14px;
border-radius:12px;
text-decoration:none;
background:#126cff;
color:white;
font-weight:bold
}

.grid{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:15px
}

.card{
text-decoration:none;
color:white;
background:#07101d;
border:1px solid #164775;
border-radius:15px;
overflow:hidden;
transition:.2s
}

.card:hover{
border-color:#1680ff;
transform:translateY(-2px)
}

.card-body{
padding:14px
}

.ad-title{
font-size:18px;
font-weight:bold;
margin-bottom:8px
}

.mini{
color:#9bb0c7;
font-size:14px
}

.price{
margin-top:12px;
color:#36a4ff;
font-weight:bold;
font-size:17px
}

@media(max-width:800px){
.grid{
grid-template-columns:1fr 1fr
}
}

@media(max-width:500px){
.grid{
grid-template-columns:1fr
}
}

</style>


<style>
#nameGemsBox button,
#nameGemsBox + label + .options button,
.options button[onclick*="setNameChange"],
.options button[onclick*="setSupercell"]{
    background:#12263d !important;
    color:#fff !important;
    border:1px solid #315579 !important;
    border-radius:14px !important;
    padding:12px 18px !important;
    margin:5px !important;
    font-size:17px !important;
    cursor:pointer !important;
}

#nameGemsBox button.selected,
.options button.selected{
    background:#1683ff !important;
    border-color:#1683ff !important;
    color:#fff !important;
}
</style>
</head>

<body>

<div class="container">

<div class="header">

<div class="logo">
LUCAS SHOP
</div>

<div class="sub">
خرید و فروش اکانت کلش آف کلنز
</div>

</div>

<div class="actions">

<a href="/sell">
➕ ثبت آگهی
</a>

<a href="/login">
⚙️ مدیریت
</a>

</div>

<div class="grid">

{{ cards|safe }}

</div>

</div>

</body>
</html>
""", cards=cards)


# =========================================================
# SELL
# =========================================================

@app.route("/sell", methods=["GET","POST"])
def sell():

    error = ""

    if request.method == "POST":

        data = request.form

        required = [
            "account_name",
            "account_tag",
            "townhall",
            "builderhall",
            "king",
            "queen",
            "warden",
            "royal",
            "account_level",
            "price",
            "telegram"
        ]

        for x in required:
            if not data.get(x):
                return sell_page("لطفاً همه اطلاعات ضروری را وارد کنید.")

        images = save_images()
        now = str(int(time.time()))

        con = db()

        values = (
            data.get("account_name",""),
            data.get("account_tag",""),
            data.get("townhall",""),
            data.get("builderhall",""),
            data.get("king",""),
            data.get("queen",""),
            data.get("warden",""),
            data.get("royal",""),
            data.get("name_change","ندارد"),
            data.get("name_change_gems","0"),
            data.get("supercell_id","ندارد"),
            data.get("account_level",""),
            data.get("price",""),
            data.get("telegram",""),
            data.get("description",""),
            images[0],
            images[1],
            images[2],
            "pending",
            0,
            data.get("townhall",""),
            data.get("builderhall",""),
            data.get("supercell_id","ندارد"),
            now,
            data.get("account_name",""),
            "اکانت کلش",
            data.get("account_level",""),
            data.get("king",""),
            data.get("queen",""),
            data.get("warden",""),
            data.get("royal",""),
            data.get("telegram",""),
            data.get("builderhall",""),
            now
        )

        columns = [
            "account_name","account_tag","townhall","builderhall",
            "king","queen","warden","royal",
            "name_change","name_change_gems","supercell_id",
            "account_level","price","seller","description",
            "image1","image2","image3","status","published",
            "th","bh","supercell","created","title","category","level",
            "barbarian_king","archer_queen","grand_warden","royal_champion",
            "telegram","builder_hall","created_at"
        ]

        placeholders = ",".join(["?"] * len(columns))

        con.execute(
            "INSERT INTO ads (" + ",".join(columns) + ") VALUES (" + placeholders + ")",
            values
        )

        con.commit()
        con.close()

        return redirect("/")

    return sell_page(error)

def sell_page(error=""):

    ths = ""

    for n in range(1,19):
        ths += f"""
        <button type="button"
        class="pick"
        onclick="choose(this,'townhall')"
        data-v="TH{n}">
        TH {n}
        </button>
        """

    bhs = ""

    for n in range(1,11):
        bhs += f"""
        <button type="button"
        class="pick"
        onclick="choose(this,'builderhall')"
        data-v="BH{n}">
        BH {n}
        </button>
        """

    heroes = [
        ("👑 پادشاه بربر","king",110),
        ("🏹 ملکه کماندار","queen",110),
        ("🧙 گرند واردن","warden",85),
        ("🛡️ قهرمان سلطنتی","royal",55)
    ]

    hero_html = ""

    for title,name,max_level in heroes:

        levels=""

        for n in range(1,max_level+1):
            levels += f"""
            <button type="button"
            class="lvl"
            onclick="choose(this,'{name}')"
            data-v="{n}">
            {n}
            </button>
            """

        hero_html += f"""
        <div class="hero">

        <b>{title}</b>

        <div class="levels">
        {levels}
        </div>

        <input type="hidden"
        name="{name}"
        id="{name}">

        </div>
        """

    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>ثبت آگهی | LUCAS SHOP</title>

<style>

*{
box-sizing:border-box
}

body{
margin:0;
background:#050b14;
color:#fff;
font-family:Tahoma,Arial;
padding:12px
}

.wrap{
max-width:900px;
margin:auto
}

.card{
background:#0b1626;
border:1px solid #203752;
border-radius:22px;
padding:18px
}

.logo{
text-align:center;
font-size:28px;
font-weight:900
}

.sub{
text-align:center;
color:#91a5bd;
margin:7px 0 20px
}

label{
display:block;
font-weight:bold;
margin:15px 0 7px
}

input,textarea{
width:100%;
padding:14px;
border-radius:12px;
border:1px solid #29435f;
background:#07101d;
color:#fff;
font-size:16px
}

textarea{
min-height:110px
}

.grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:12px
}

.section{
border-top:1px solid #203752;
margin-top:20px;
padding-top:16px
}

.choices{
display:flex;
flex-wrap:wrap;
gap:6px
}

.pick,.lvl{
border:1px solid #315071;
background:#11243a;
color:white;
border-radius:9px;
padding:9px 11px
}

.pick.active,.lvl.active{
background:#147fff;
border-color:#147fff
}

.hero{
background:#081321;
border:1px solid #1c3149;
border-radius:14px;
padding:12px;
margin:10px 0
}

.hero b{
display:block;
margin-bottom:9px
}

.levels{
display:flex;
flex-wrap:wrap;
gap:4px
}

.lvl{
min-width:37px;
padding:7px
}

.submit{
width:100%;
margin-top:20px;
padding:16px;
border:0;
border-radius:13px;
background:#147fff;
color:white;
font-size:18px;
font-weight:bold
}

.back{
display:block;
text-align:center;
color:#8fc4ff;
text-decoration:none;
margin-top:15px
}

.error{
background:#55202b;
border:1px solid #b94458;
padding:12px;
border-radius:11px;
margin-bottom:12px
}

@media(max-width:650px){
.grid{
grid-template-columns:1fr
}
}

</style>

</head>

<body>

<div class="wrap">

<div class="card">

<div class="logo">
🎮 LUCAS SHOP
</div>

<div class="sub">
ثبت آگهی اکانت کلش آف کلنز
</div>

{% if error %}
<div class="error">
{{ error }}
</div>
{% endif %}

<form method="POST"
enctype="multipart/form-data"
autocomplete="off">

<label>نام اکانت</label>
<input name="account_name" required>

<label>تگ اکانت</label>
<input name="account_tag"
placeholder="#XXXXXXXX"
required>

<div class="section">

<label>تاون هال</label>

<div class="choices">
{{ ths|safe }}
</div>

<input type="hidden"
name="townhall"
id="townhall"
required>

</div>

<div class="section">

<label>بیلدر هال</label>

<div class="choices">
{{ bhs|safe }}
</div>

<input type="hidden"
name="builderhall"
id="builderhall"
required>

</div>

<div class="section">

<label>سطح قهرمان‌ها</label>

{{ hero_html|safe }}

</div>

<div class="grid">

<div>

<label>لول اکانت</label>
<input name="account_level" required>

</div>

<div>

<label>قیمت</label>
<input name="price" required>

</div>

</div>

<label>تغییر نام</label>
<div class="label">تغییر نام</div>
<div class="options">
<button type="button" onclick="pick('name_change','دارد',this)">دارد</button>
<button type="button" onclick="pick('name_change','ندارد',this)">ندارد</button>
</div>
<label>تغییر نام</label>

<div class="options">
<button type="button" onclick="setNameChange('رایگان',this)">رایگان</button>
<button type="button" onclick="setNameChange('با جم',this)">با جم</button>
</div>

<input type="hidden" name="name_change" id="name_change" value="">

<div id="nameGemsBox" style="display:none;">

<label>تعداد جم تغییر نام</label>

<div class="options">
<button type="button" onclick="setGem('500',this)">500</button>
<button type="button" onclick="setGem('1000',this)">1000</button>
<button type="button" onclick="setGem('1500',this)">1500</button>
<button type="button" onclick="setGem('2000',this)">2000</button>
<button type="button" onclick="setGem('2500',this)">2500</button>
<button type="button" onclick="setGem('3000',this)">3000</button>
<button type="button" onclick="setGem('3500',this)">3500</button>
<button type="button" onclick="setGem('بیشتر',this)">بیشتر</button>
</div>

<input type="hidden" name="name_change_gems" id="name_change_gems" value="0">

<input
type="number"
name="name_change_gems_custom"
id="name_change_gems_custom"
placeholder="تعداد جم بیشتر از 3500"
min="3501"
style="display:none;">

</div>

<label>Supercell ID</label>

<div class="options">
<button type="button" onclick="setSupercell('بله متصل هست',this)">بله متصل هست</button>
<button type="button" onclick="setSupercell('خیر متصل نیست',this)">خیر متصل نیست</button>
</div>

<input type="hidden" name="supercell_id" id="supercell_id" value="">

<script>
function setNameChange(value,btn){
    document.getElementById("name_change").value=value;

    btn.parentElement.querySelectorAll("button").forEach(function(b){
        b.classList.remove("selected");
    });
    btn.classList.add("selected");

    var box=document.getElementById("nameGemsBox");

    if(value==="با جم"){
        box.style.display="block";
    }else{
        box.style.display="none";
        document.getElementById("name_change_gems").value="0";
        document.getElementById("name_change_gems_custom").value="";
        document.getElementById("name_change_gems_custom").style.display="none";
    }
}

function setGem(value,btn){
    document.getElementById("name_change_gems").value=value;

    btn.parentElement.querySelectorAll("button").forEach(function(b){
        b.classList.remove("selected");
    });
    btn.classList.add("selected");

    var custom=document.getElementById("name_change_gems_custom");

    if(value==="بیشتر"){
        custom.style.display="block";
        custom.value="";
        custom.focus();
    }else{
        custom.style.display="none";
        custom.value="";
    }
}

function setSupercell(value,btn){
    document.getElementById("supercell_id").value=value;

    btn.parentElement.querySelectorAll("button").forEach(function(b){
        b.classList.remove("selected");
    });
    btn.classList.add("selected");
}

document.getElementById("name_change_gems_custom").addEventListener("input",function(){
    document.getElementById("name_change_gems").value=this.value;
});
</script>

<label>آیدی تلگرام فروشنده</label>
<input name="telegram" required>

<label>توضیحات</label>
<textarea name="description"
placeholder="توضیحات اکانت..."></textarea>

<div class="section">

<label>عکس اول</label>
<input type="file"
name="image1"
accept="image/*">

<label>عکس دوم</label>
<input type="file"
name="image2"
accept="image/*">

<label>عکس سوم</label>
<input type="file"
name="image3"
accept="image/*">

</div>

<button class="submit"
type="submit">
🚀 ثبت آگهی
</button>

<script>
function pick(name,value,btn){
    document.getElementById(name).value=value;
    btn.parentElement.querySelectorAll("button").forEach(function(b){
        b.classList.remove("selected");
    });
    btn.classList.add("selected");
}
</script>
</form>

<a href="/" class="back">
🏠 برگشت به فروشگاه
</a>

</div>

</div>

<script>

function choose(btn,id){

    document
    .querySelectorAll(
        '[onclick*="choose(this,\\''+id+'\\')"]'
    )
    .forEach(x=>x.classList.remove("active"));

    btn.classList.add("active");

    document.getElementById(id).value =
        btn.dataset.v;
}

</script>

</body>
</html>
""",
        error=error,
        ths=ths,
        bhs=bhs,
        hero_html=hero_html
    )


# =========================================================
# AD PAGE
# =========================================================

@app.route("/ad/<int:ad_id>")
def ad_page(ad_id):

    con = db()

    ad = con.execute(
        "SELECT * FROM ads WHERE id=?",
        (ad_id,)
    ).fetchone()

    if ad:
        con.execute(
            "UPDATE ads SET views=views+1 WHERE id=?",
            (ad_id,)
        )
        con.commit()

    con.close()

    if not ad:
        return "آگهی پیدا نشد",404

    def val(key,default="—"):

        try:
            x=ad[key]

            if x not in (None,""):
                return x

        except:
            pass

        return default

    images=[]

    for key in ["image1","image2","image3"]:

        try:

            if ad[key]:
                images.append(
                    "/uploads/"+str(ad[key])
                )

        except:
            pass

    main_img=images[0] if images else ""

    thumbs=""

    for img in images:

        thumbs += f"""
        <img
        src="{img}"
        class="thumb"
        onclick="changeImage('{img}')">
        """

    return render_template_string("""
<!DOCTYPE html>

<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>LUCAS SHOP</title>

<style>

*{
box-sizing:border-box
}

body{
margin:0;
background:#02050b;
color:white;
font-family:Tahoma,Arial;
padding:12px
}

.card{
max-width:1250px;
margin:auto;
background:#030812;
border:2px solid #126cff;
border-radius:20px;
padding:12px;
box-shadow:
0 0 20px #0066ff,
inset 0 0 30px rgba(0,80,255,.12)
}

.title{
text-align:center;
font-size:25px;
font-weight:900;
margin-bottom:15px;
text-shadow:0 0 12px #1680ff
}

.content{
display:grid;
grid-template-columns:1.35fr 1fr;
gap:14px;
direction:ltr
}

.photos{
direction:ltr;
min-height:700px;
border:2px solid #1680ff;
border-radius:18px;
padding:10px;
background:
radial-gradient(
circle at 50% 85%,
rgba(0,100,255,.35),
transparent 35%
),
#02050b;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center
}

.main-img{
width:100%;
max-height:650px;
object-fit:contain;
border-radius:12px;
cursor:pointer
}

.thumbs{
width:100%;
display:flex;
gap:8px;
justify-content:center;
margin-top:10px
}

.thumb{
width:80px;
height:65px;
object-fit:cover;
border:2px solid #126cff;
border-radius:8px;
cursor:pointer
}

.info{
direction:rtl;
display:flex;
flex-direction:column;
gap:7px
}

.row{
min-height:58px;
display:grid;
grid-template-columns:43% 57%;
align-items:center;
background:linear-gradient(
90deg,
#07101d,
#030811
);
border:1px solid #164775;
border-radius:13px;
overflow:hidden
}

.label{
height:100%;
display:flex;
align-items:center;
padding:8px 12px;
font-size:16px;
font-weight:bold;
border-left:1px solid #164775
}

.value{
padding:8px 12px;
font-size:16px;
font-weight:bold;
word-break:break-word
}

.code .value{
color:#4da3ff
}

.price{
border:2px solid #1680ff
}

.price .value{
color:#36a4ff;
font-size:19px
}

.bottom{
margin-top:15px;
border:1px solid #164775;
border-radius:15px;
padding:15px;
background:#030912
}

.description{
line-height:2;
white-space:pre-wrap
}

.contact{
margin-top:12px;
display:grid;
grid-template-columns:1fr 1fr;
gap:10px
}

.contact-box{
border:1px solid #164775;
border-radius:12px;
padding:12px;
text-align:center
}

.contact-title{
color:#40a5ff;
font-weight:bold;
margin-bottom:6px
}

.contact-value{
direction:ltr;
font-weight:bold
}

.back{
display:block;
margin-top:15px;
text-align:center;
padding:14px;
border-radius:12px;
background:#126cff;
color:white;
text-decoration:none;
font-weight:bold
}

@media(max-width:800px){

.content{
grid-template-columns:1fr
}

.photos{
min-height:400px
}

.main-img{
max-height:500px
}

.contact{
grid-template-columns:1fr
}

}

</style>

</head>

<body>

<div class="card">

<div class="title">
🎮 LUCAS SHOP — مشخصات اکانت
</div>

<div class="content">

<div class="photos">

{% if main_img %}

<img
id="mainImage"
src="{{ main_img }}"
class="main-img"
onclick="window.open(this.src,'_blank')">

<div class="thumbs">
{{ thumbs|safe }}
</div>

{% else %}

<div style="
height:500px;
display:flex;
align-items:center;
justify-content:center;
color:#60748b;
">
بدون تصویر
</div>

{% endif %}

</div>


<div class="info">

<div class="row code">
<div class="label">کد آگهی</div>
<div class="value">{{ val("id") }}</div>
</div>

<div class="row">
<div class="label">نام اکانت</div>
<div class="value">{{ val("account_name") }}</div>
</div>

<div class="row">
<div class="label">تاون هال</div>
<div class="value">{{ val("townhall",val("th")) }}</div>
</div>

<div class="row">
<div class="label">بیلدر هال</div>
<div class="value">{{ val("builderhall",val("bh")) }}</div>
</div>

<div class="row">
<div class="label">کینگ بربر</div>
<div class="value">{{ val("king",val("barbarian_king")) }}</div>
</div>

<div class="row">
<div class="label">آرچر کویین</div>
<div class="value">{{ val("queen",val("archer_queen")) }}</div>
</div>

<div class="row">
<div class="label">گرند واردن</div>
<div class="value">{{ val("warden",val("grand_warden")) }}</div>
</div>

<div class="row">
<div class="label">هیروی سلطنتی</div>
<div class="value">{{ val("royal",val("royal_champion")) }}</div>
</div>

<div class="row">
<div class="label">تغییر نام</div>
<div class="value">{{ val("name_change") }}</div>
</div>

<div class="row">
<div class="label">Supercell ID</div>
<div class="value">{{ val("supercell_id",val("supercell")) }}</div>
</div>

<div class="row">
<div class="label">لول اکانت</div>
<div class="value">{{ val("account_level",val("level")) }}</div>
</div>

<div class="row price">
<div class="label">قیمت</div>
<div class="value">{{ val("price") }} تومان</div>
</div>

</div>

</div>

<div class="bottom">

<div class="description">
{{ val("description") }}
</div>

<div class="contact">

<div class="contact-box">

<div class="contact-title">
Admin
</div>

<div class="contact-value">
@LUCAS_SHOP_1
</div>

</div>

<div class="contact-box">

<div class="contact-title">
Channel
</div>

<div class="contact-value">
@LUCAS_SHOP_LS1
</div>

</div>

</div>

</div>

<a href="/" class="back">
🏠 برگشت به فروشگاه
</a>

</div>

<script>

function changeImage(src){

document.getElementById("mainImage").src=src;

}

</script>

</body>
</html>
""",
        ad=ad,
        val=val,
        main_img=main_img,
        thumbs=thumbs
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login",methods=["GET","POST"])
def admin_login():

    if request.method=="POST":

        if request.form.get("password")==ADMIN_PASSWORD:

            session["admin"]=True

            return redirect("/admin")

        return render_template_string("""
        <h3 style="color:red">رمز اشتباه است</h3>
        <a href="/login">برگشت</a>
        """)

    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<body style="
background:#030812;
color:white;
font-family:Tahoma;
padding:30px;
">

<div style="
max-width:400px;
margin:auto;
background:#0b1626;
padding:25px;
border-radius:18px;
border:1px solid #1680ff;
">

<h2>⚙️ مدیریت LUCAS SHOP</h2>

<form method="POST">

<input
type="password"
name="password"
placeholder="رمز مدیریت"
style="
width:100%;
padding:14px;
margin:10px 0;
">

<button
style="
width:100%;
padding:14px;
background:#126cff;
color:white;
border:0;
border-radius:10px;
">

ورود

</button>

</form>

</div>

</body>
</html>
""")


# =========================================================
# ADMIN
# =========================================================

@app.route("/admin")
def admin_panel():

    if not session.get("admin"):
        return redirect("/login")

    con=db()

    ads=con.execute(
        "SELECT * FROM ads ORDER BY id DESC"
    ).fetchall()

    con.close()

    html=""

    for ad in ads:

        img=""

        if ad["image1"]:

            img=f"""
            <img
            src="/uploads/{ad['image1']}"
            style="
            width:100%;
            max-height:220px;
            object-fit:cover;
            border-radius:14px;
            margin-bottom:12px
            ">
            """

        html+=f"""

        <div style="
        background:#07101d;
        border:1px solid #164775;
        border-radius:15px;
        padding:15px;
        margin-bottom:15px;
        ">

        {img}

        <h3>
        #{ad['id']} —
        {ad['account_name']}
        </h3>

        <p>
        TH:
        {ad['townhall']}
        |
        BH:
        {ad['builderhall']}
        </p>

        <p>
        قیمت:
        {ad['price']}
        تومان
        </p>

        <p>
        وضعیت:
        {ad['status']}
        </p>

        <a href="/ad/{ad['id']}"
        style="color:#45a5ff">
        مشاهده آگهی
        </a>

        <br><br>

        <a href="/admin/approve/{ad['id']}"
        style="color:#42e88b">
        ✅ تأیید
        </a>

        &nbsp;&nbsp;

        <a href="/admin/reject/{ad['id']}"
        style="color:#ff6075">
        ❌ رد
        </a>

        <form
        action="/admin/price/{ad['id']}"
        method="POST"
        style="margin-top:12px"
        >

        <input
        name="price"
        value="{ad['price']}"
        placeholder="قیمت جدید"
        style="padding:10px"
        >

        <button>
        تغییر قیمت
        </button>

        </form>

        </div>
        """

    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<body style="
margin:0;
background:#02050b;
color:white;
font-family:Tahoma;
padding:15px
">

<div style="max-width:900px;margin:auto">

<h1>
⚙️ مدیریت LUCAS SHOP
</h1>

{{ html|safe }}

<a href="/admin/logout"
style="color:#ff6075">
خروج از مدیریت
</a>

</div>

</body>
</html>
""",html=html)


@app.route("/admin/approve/<int:ad_id>")
def approve(ad_id):

    if not session.get("admin"):
        return redirect("/login")

    con=db()

    con.execute("""
    UPDATE ads
    SET status='approved',
        published=1
    WHERE id=?
    """,(ad_id,))

    con.commit()
    con.close()

    return redirect("/admin")


@app.route("/admin/reject/<int:ad_id>")
def reject(ad_id):

    if not session.get("admin"):
        return redirect("/login")

    con=db()

    con.execute("""
    UPDATE ads
    SET status='rejected',
        published=0
    WHERE id=?
    """,(ad_id,))

    con.commit()
    con.close()

    return redirect("/admin")


@app.route("/admin/price/<int:ad_id>",methods=["POST"])
def change_price(ad_id):

    if not session.get("admin"):
        return redirect("/login")

    price=request.form.get("price","")

    con=db()

    con.execute(
        "UPDATE ads SET price=? WHERE id=?",
        (price,ad_id)
    )

    con.commit()
    con.close()

    return redirect("/admin")


@app.route("/admin/logout")
def admin_logout():

    session.pop("admin",None)

    return redirect("/login")


# =========================================================
# RUN
# =========================================================

if __name__=="__main__":

    print("================================")
    print("🤖 LUCAS SHOP اجرا شد")
    print("🌐 http://127.0.0.1:8080")
    print("================================")

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
