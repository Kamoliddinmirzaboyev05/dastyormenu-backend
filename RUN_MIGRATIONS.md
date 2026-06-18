# 🚀 MIGRATIONS ISHGA TUSHIRISH

## ⚠️ MUHIM: Migrations Kerak!

Sizning serveringiz ishlab turibdi, lekin 2 ta migration apply qilinmagan:
- `menu.0002_alter_menu_image_url`
- `organizations.0002_alter_organization_logo`

---

## 📋 QANDAY QILISH KERAK?

### Variant 1: Yangi Terminal Oching (Tavsiya etiladi)

1. **Yangi terminal oching** (server ishlab turgan terminaldan boshqa)

2. **Virtual environment aktivlashtiring:**
```bash
source venv/bin/activate
```

3. **Migrations ishga tushiring:**
```bash
python manage.py migrate
```

4. **Kutilgan natija:**
```
Running migrations:
  Applying menu.0002_alter_menu_image_url... OK
  Applying organizations.0002_alter_organization_logo... OK
```

5. **Tayyor!** Server'ni qayta ishga tushirish shart emas.

---

### Variant 2: Server'ni To'xtatib, Qayta Ishga Tushiring

1. **Server'ni to'xtating:**
```
Ctrl+C (yoki Command+C Mac'da)
```

2. **Migrations ishga tushiring:**
```bash
python manage.py migrate
```

3. **Server'ni qayta ishga tushiring:**
```bash
python manage.py runserver
```

---

## ✅ Migrations Nima Qiladi?

### menu.0002_alter_menu_image_url
```python
# ImageField → URLField
image_url = models.URLField(max_length=500, null=True, blank=True)
```

**O'zgarish:**
- Eski: `ImageField` (local file storage)
- Yangi: `URLField` (ImgBB URL)

### organizations.0002_alter_organization_logo
```python
# ImageField → URLField
logo = models.URLField(max_length=500, null=True, blank=True)
```

**O'zgarish:**
- Eski: `ImageField` (local file storage)
- Yangi: `URLField` (ImgBB URL)

---

## 🔍 Tekshirish

Migrations muvaffaqiyatli bo'lganini tekshirish:

```bash
python manage.py showmigrations menu organizations
```

**Kutilgan natija:**
```
menu
 [X] 0001_initial
 [X] 0002_alter_menu_image_url

organizations
 [X] 0001_initial
 [X] 0002_alter_organization_logo
```

`[X]` - applied (muvaffaqiyatli)
`[ ]` - not applied (hali ishga tushmagan)

---

## 📸 Keyin Nima?

Migrations ishga tushgandan keyin:

1. **Swagger'ni yangilang:**
   - http://localhost:8000/
   - Ctrl+Shift+R (cache tozalash)

2. **Rasm yuklang:**
   - POST /api/menu/
   - `image` field'da rasm tanlang
   - Execute

3. **Response tekshiring:**
   ```json
   {
     "image_url": "https://i.ibb.co/abc123/image.jpg"
   }
   ```

---

## ❓ Muammo Bo'lsa?

### Migration xatosi?

```bash
# Fake migration (agar database allaqachon to'g'ri bo'lsa)
python manage.py migrate --fake menu 0002
python manage.py migrate --fake organizations 0002
```

### Database xatosi?

```bash
# Database holatini tekshiring
python manage.py dbshell
\d menu_items
\d organizations
\q
```

### Virtual environment topilmayapti?

```bash
# Virtual environment yarating
python3 -m venv venv

# Aktivlashtiring
source venv/bin/activate

# Dependencies o'rnating
pip install -r requirements.txt

# Migrations ishga tushiring
python manage.py migrate
```

---

## 🎉 Tayyor!

Migrations ishga tushgandan keyin:
- ✅ Database yangilangan
- ✅ ImageField → URLField
- ✅ ImgBB integration tayyor
- ✅ Swagger'da rasm yuklash mumkin

---

**KEYINGI QADAM:**

```bash
# Yangi terminal oching
source venv/bin/activate
python manage.py migrate
```

**Muvaffaqiyatli ishlar!** 🚀
