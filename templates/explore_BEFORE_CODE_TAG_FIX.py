<!doctype html>
<html lang="fa" dir="rtl">

<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{{ site_name or "LUCAS SHOP" }} | آگهی‌ها</title>

<style>
*{box-sizing:border-box}

body{
 margin:0;
 background:#050912;
 color:#fff;
 font-family:Tahoma,Arial,sans-serif;
}

a{text-decoration:none;color:inherit}

.top{
 position:sticky;
 top:0;
 z-index:20;
 background:rgba(5,9,18,.94);
 border-bottom:1px solid #172235;
 backdrop-filter:blur(15px);
}

.nav{
 max-width:1180px;
 margin:auto;
 padding:16px 18px;
 display:flex;
 align-items:center;
 justify-content:space-between;
 gap:12px;
}

.logo{
 font-size:22px;
 font-weight:900;
 letter-spacing:1px;
 color:#fff;
}

.logo span{color:#3b82f6}

.navlinks{
 display:flex;
 gap:8px;
 flex-wrap:wrap;
}

.btn{
 display:inline-flex;
 align-items:center;
 justify-content:center;
 padding:10px 15px;
 border-radius:12px;
 border:1px solid #24324a;
 background:#0d1524;
 color:#fff;
 font-weight:700;
}

.btn.primary{
 background:#2563eb;
 border-color:#2563eb;
}

.wrap{
 max-width:1180px;
 margin:auto;
 padding:28px 18px 70px;
}

.hero{
 padding:25px;
 border:1px solid #17253b;
 border-radius:24px;
 background:
 radial-gradient(circle at 85% 20%,rgba(37,99,235,.22),transparent 35%),
 linear-gradient(145deg,#0b1424,#070c16);
 margin-bottom:22px;
}

.hero h1{
 margin:0 0 9px;
 font-size:32px;
}

.hero p{
 margin:0;
 color:#94a3b8;
 line-height:1.9;
}

.grid{
 display:grid;
 grid-template-columns:repeat(auto-fill,minmax(245px,1fr));
 gap:16px;
}

.card{
 overflow:hidden;
 border:1px solid #18263b;
 border-radius:19px;
 background:#0a111e;
 transition:.2s;
}

.card:hover{
 transform:translateY(-3px);
 border-color:#31588f;
}

.pic{
 height:205px;
 background:#080d17;
 display:flex;
 align-items:center;
 justify-content:center;
 overflow:hidden;
}

.pic img{
 width:100%;
 height:100%;
 object-fit:cover;
}

.noimg{
 color:#64748b;
 font-size:50px;
}

.body{
 padding:16px;
}

.title{
 font-size:18px;
 font-weight:900;
 margin-bottom:10px;
 white-space:nowrap;
 overflow:hidden;
 text-overflow:ellipsis;
}

.code{
 display:inline-block;
 color:#4ba7ff;
 background:#0b1a2d;
 border:1px solid #21466e;
 padding:5px 9px;
 border-radius:8px;
 font-size:12px;
 font-weight:900;
 margin-bottom:12px;
}

.info{
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:8px;
 margin-bottom:12px;
}

.info div{
 background:#0e1727;
 border:1px solid #1a2940;
 border-radius:10px;
 padding:9px;
 font-size:12px;
 color:#94a3b8;
}

.info b{
 display:block;
 color:#fff;
 margin-top:4px;
 font-size:13px;
}

.price{
 font-size:20px;
 font-weight:900;
 color:#60a5fa;
 margin-bottom:13px;
}

.extra{
 background:#0e1727;
 border:1px solid #1a2940;
 border-radius:10px;
 padding:9px;
 margin-bottom:12px;
 font-size:12px;
 color:#94a3b8;
}

.extra b{
 color:#fff;
}

.empty{
 text-align:center;
 padding:60px 20px;
 border:1px dashed #263650;
 border-radius:20px;
 color:#94a3b8;
}

@media(max-width:600px){

 .nav{
  padding:12px;
 }

 .hero h1{
  font-size:25px;
 }

 .wrap{
  padding:18px 12px 50px;
 }

 .grid{
  grid-template-columns:1fr 1fr;
  gap:10px;
 }

 .pic{
  height:145px;
 }

 .body{
  padding:11px;
 }

 .title{
  font-size:14px;
 }

 .price{
  font-size:16px;
 }

 .btn{
  padding:9px 11px;
  font-size:12px;
 }

 .info div{
  padding:7px;
  font-size:11px;
 }

 .info b{
  font-size:12px;
 }

}
</style>

</head>

<body>

<header class="top">

<div class="nav">

<a class="logo" href="/">
LUCAS <span>SHOP</span>
</a>

<div class="navlinks">

<a class="btn" href="/">
خانه
</a>

<a class="btn primary" href="/create-ad">
📢 ثبت آگهی
</a>

{% if current_user %}

<a class="btn" href="/account">
👤 حساب من
</a>

{% else %}

<a class="btn" href="/login">
ورود
</a>

{% endif %}

</div>

</div>

</header>


<main class="wrap">

<section class="hero">

<h1>
📢 آگهی‌های LUCAS SHOP
</h1>

<p>
آگهی‌های فروش اکانت کلش آف کلنز را مشاهده کنید.
</p>

</section>


{% if products %}

<div class="grid">

{% for p in products %}

<article class="card">


<div class="pic">

{% if p['image'] %}

<img
src="/uploads/{{ p['image'] }}"
alt=""
>

{% else %}

<div class="noimg">
🎮
</div>

{% endif %}

</div>


<div class="body">


{% if p['is_ad'] is defined and p['is_ad'] %}

<div class="code">
{{ p['listing_code'] }}
</div>

{% endif %}


<div class="title">
{{ p['title'] or 'بدون نام' }}
</div>


<div class="info">

<div>

تاون هال

<b>
{% if p['is_ad'] is defined and p['is_ad'] %}
TH {{ p['town_hall'] or '—' }}
{% else %}
{{ p['town_hall'] if 'town_hall' in p.keys() else '—' }}
{% endif %}
</b>

</div>


<div>

بیلدر هال

<b>
{% if p['is_ad'] is defined and p['is_ad'] %}
BH {{ p['builder_hall'] or '—' }}
{% else %}
{{ p['builder_hall'] if 'builder_hall' in p.keys() else '—' }}
{% endif %}
</b>

</div>

</div>


{% if p['is_ad'] is defined and p['is_ad'] %}

<div class="extra">

Player Tag:

<b>
{{ p['player_tag'] or '—' }}
</b>

</div>

{% endif %}


<div class="price">

{{ money(p['price']) if money is defined else p['price'] }}
تومان

</div>


{% if p['is_ad'] is defined and p['is_ad'] %}

<a
class="btn primary"
style="width:100%"
href="/ad/{{ p['listing_code'] }}"
>
👁 مشاهده آگهی
</a>

{% else %}

<a
class="btn primary"
style="width:100%"
href="/product/{{ p['id'] }}"
>
👁 مشاهده محصول
</a>

{% endif %}


</div>

</article>

{% endfor %}

</div>


{% else %}

<div class="empty">

<div style="font-size:45px;margin-bottom:12px">
📦
</div>

<h2 style="color:#fff">
هنوز آگهی‌ای ثبت نشده
</h2>

<p>
اولین آگهی فروش اکانت را ثبت کنید.
</p>

<a
class="btn primary"
href="/create-ad"
>
📢 ثبت آگهی
</a>

</div>

{% endif %}

</main>

</body>
</html>
