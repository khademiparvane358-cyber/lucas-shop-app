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


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE username=? AND password=?
        """, (username, password)).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]

            return redirect(
                request.args.get(
                    "next",
                    url_for("home")
                )
            )

        return render_template(
            "login.html",
            error="نام کاربری یا رمز عبور اشتباه است."
        )

    return render_template(
        "login.html",
        error=""
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if len(username) < 3 or len(password) < 4:

            return render_template(
                "register.html",
                error="اطلاعات وارد شده معتبر نیست."
            )

        conn = db()

        try:

            cur = conn.execute("""
                INSERT INTO users(
                    username,
                    name,
                    password,
                    created_at
                )
                VALUES(?,?,?,?)
            """, (
                username,
                name,
                password,
                int(time.time())
            ))

            conn.commit()

            session["user_id"] = cur.lastrowid

            conn.close()

            return redirect(url_for("home"))

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "register.html",
                error="این نام کاربری قبلاً ثبت شده است."
            )

    return render_template(
        "register.html",
        error=""
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():

    user = current_user()

    if not user:
        return redirect(
            url_for(
                "login",
                next=url_for("profile")
            )
        )

    conn = db()

    favorites = conn.execute("""
        SELECT p.*
        FROM products p
        INNER JOIN favorites f
            ON f.product_id=p.id
        WHERE f.user_id=?
        ORDER BY f.id DESC
    """, (user["id"],)).fetchall()

    orders = conn.execute("""
        SELECT *
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 20
    """, (user["id"],)).fetchall()

    conn.close()

    return render_template(
        "profile.html",
        favorites=favorites,
        orders=orders
    )


# ============================================================
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
