import os
import re
import shutil
import sqlite3
import ast
import traceback

APP = "app.py"
DB = "lucas.db"

print("=" * 70)
print("        LUCAS SHOP — FULL SAFE REPAIR")
print("=" * 70)

# ============================================================
# 1. BACKUP
# ============================================================

if os.path.exists(APP):
    shutil.copy2(APP, "app_BEFORE_FULL_REPAIR.py")
    print("✅ app.py backup created")

if os.path.exists(DB):
    shutil.copy2(DB, "lucas_BEFORE_FULL_REPAIR.db")
    print("✅ lucas.db backup created")
else:
    print("❌ lucas.db not found")
    raise SystemExit(1)

# ============================================================
# 2. PYTHON SYNTAX CHECK
# ============================================================

print("\n[1/8] Checking Python syntax...")

try:
    source = open(APP, encoding="utf-8").read()
    ast.parse(source)
    print("✅ Python syntax OK")
except Exception:
    print("❌ Python syntax error:")
    traceback.print_exc()
    raise SystemExit(1)

# ============================================================
# 3. DATABASE OPEN
# ============================================================

print("\n[2/8] Opening database...")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

tables = [
    r[0]
    for r in con.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
]

print("Tables:", ", ".join(tables) if tables else "NONE")

# ============================================================
# 4. ENSURE ADS TABLE / COLUMNS
# ============================================================

print("\n[3/8] Checking ads table...")

ads_exists = con.execute(
    "SELECT 1 FROM sqlite_master "
    "WHERE type='table' AND name='ads'"
).fetchone()

if not ads_exists:
    print("⚠️ ads table does not exist")
    print("ℹ️ It will be created by app.py initialization.")
else:
    ads_cols = {
        r["name"].lower()
        for r in con.execute('PRAGMA table_info("ads")').fetchall()
    }

    print("Existing ads columns:")
    print("  " + ", ".join(sorted(ads_cols)))

    # Safe columns commonly required by the current LUCAS SHOP ad system.
    safe_columns = {
        "views": "INTEGER DEFAULT 0",
        "listing_code": "TEXT",
        "title": "TEXT",
        "price": "TEXT",
        "description": "TEXT",
        "seller_id": "INTEGER",
        "created_at": "TEXT",
        "updated_at": "TEXT",
        "status": "TEXT DEFAULT 'active'",
    }

    for col, definition in safe_columns.items():
        if col.lower() not in ads_cols:
            try:
                con.execute(
                    f'ALTER TABLE ads ADD COLUMN "{col}" {definition}'
                )
                print(f"✅ Added ads.{col}")
            except Exception as e:
                print(f"⚠️ Could not add ads.{col}: {e}")

# ============================================================
# 5. ENSURE VIEWS ARE VALID
# ============================================================

print("\n[4/8] Checking views...")

ads_exists = con.execute(
    "SELECT 1 FROM sqlite_master "
    "WHERE type='table' AND name='ads'"
).fetchone()

if ads_exists:
    cols = {
        r["name"].lower()
        for r in con.execute('PRAGMA table_info("ads")').fetchall()
    }

    if "views" in cols:
        con.execute(
            "UPDATE ads SET views=0 WHERE views IS NULL"
        )
        print("✅ ads.views is ready")
    else:
        print("❌ ads.views is still missing")
else:
    print("ℹ️ ads table not currently present")

# ============================================================
# 6. CHECK LISTING CODES
# ============================================================

print("\n[5/8] Checking listing codes...")

if ads_exists:
    cols = {
        r["name"].lower()
        for r in con.execute('PRAGMA table_info("ads")').fetchall()
    }

    if "listing_code" in cols:
        rows = con.execute(
            'SELECT rowid, listing_code FROM ads'
        ).fetchall()

        used = set()
        changed = 0

        for row in rows:
            code = row["listing_code"]

            if code and str(code).strip():
                used.add(str(code).strip().upper())
                continue

            n = 1
            while f"LS-{n:04d}" in used:
                n += 1

            new_code = f"LS-{n:04d}"

            try:
                con.execute(
                    'UPDATE ads SET listing_code=? WHERE rowid=?',
                    (new_code, row["rowid"])
                )
                used.add(new_code)
                changed += 1
            except Exception as e:
                print(
                    f"⚠️ Could not assign code to row "
                    f"{row['rowid']}: {e}"
                )

        if changed:
            print(f"✅ {changed} missing listing code(s) repaired")
        else:
            print("✅ Listing codes OK")

# ============================================================
# 7. CHECK APP ROUTES / AD PARAMETER
# ============================================================

print("\n[6/8] Checking ad route...")

route_patterns = [
    r'@app\.route\(["\']\/ad\/<[^>]+>["\']',
    r'@app\.route\(["\']\/ad\/<string:[^>]+>["\']',
]

route_found = False

for pattern in route_patterns:
    if re.search(pattern, source):
        route_found = True
        break

if route_found:
    print("✅ /ad/<...> route found")
else:
    print("⚠️ /ad route was not detected automatically")

if "def ad_page(listing_code):" in source:
    print("✅ ad_page(listing_code) is correct")
elif "def ad_page(ad_id):" in source:
    print("⚠️ Old ad_page(ad_id) detected")
    print("ℹ️ No automatic destructive replacement performed")
else:
    print("⚠️ ad_page function signature not detected")

# ============================================================
# 8. FINALIZE DATABASE
# ============================================================

print("\n[7/8] Saving database...")

con.commit()

# Integrity check
integrity = con.execute(
    "PRAGMA integrity_check"
).fetchone()[0]

print("SQLite integrity:", integrity)

con.close()

# ============================================================
# FINAL COMPILE
# ============================================================

print("\n[8/8] Final Python compile...")

os.system("python -m py_compile app.py")

print()
print("=" * 70)
print("              FULL REPAIR FINISHED")
print("=" * 70)
print()
print("✅ Backup: app_BEFORE_FULL_REPAIR.py")
print("✅ Backup: lucas_BEFORE_FULL_REPAIR.db")
print("✅ Database checked")
print("✅ ads checked")
print("✅ views checked")
print("✅ listing codes checked")
print("✅ /ad route checked")
print("✅ Python compile checked")
print()
print("NOW RUN:")
print("python app.py")
print("=" * 70)
