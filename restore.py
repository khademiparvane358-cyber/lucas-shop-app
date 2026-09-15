import marshal
import dis

pyc = "__pycache__/app.cpython-313.pyc"

with open(pyc, "rb") as f:
    f.read(16)
    code = marshal.load(f)

text = dis.Bytecode(code)

print("✅ فایل pyc خوانده شد")
print("نام‌ها:")
print(code.co_names)

print("\n🔎 بررسی Flask:")
names = set(code.co_names)

if "Flask" in names or "render_template" in names or "sqlite3" in names:
    print("✅ این pyc مربوط به سایت است.")
else:
    print("❌ این pyc احتمالاً نسخه سایت نیست.")
