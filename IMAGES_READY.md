# ✅ RASMLAR TAYYOR - ImgBB Integration

## 🎉 Nima Qilindi?

Cloudinary o'rniga **ImgBB** integratsiya qilindi!

### Nega ImgBB?
- ✅ **Uzbekistonda ishlaydi** - Blokirovka yo'q
- ✅ **Bepul** - Cheklovsiz yuklash
- ✅ **Oson** - API key allaqachon sozlangan
- ✅ **Tez** - Global CDN
- ✅ **Ishonchli** - 99.9% uptime

---

## 📋 O'zgarishlar

### 1. Models Yangilandi
**apps/menu/models.py:**
```python
# ImageField → URLField
image_url = models.URLField(max_length=500, null=True, blank=True)
```

**apps/organizations/models.py:**
```python
# ImageField → URLField
logo = models.URLField(max_length=500, null=True, blank=True)
```

### 2. Serializers Yangilandi
**apps/menu/serializers.py:**
- `image` (write_only) - Rasm yuklash
- `image_url` (read_only) - ImgBB URL
- Avtomatik ImgBB'ga yuklash

**apps/organizations/serializers.py:**
- `logo_file` (write_only) - Logo yuklash
- `logo` (read_only) - ImgBB URL
- Avtomatik ImgBB'ga yuklash

### 3. Settings Yangilandi
**config/settings/base.py:**
```python
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', '')
IMGBB_API_URL = 'https://api.imgbb.com/1/upload'
```

### 4. Environment Variables
**.env:**
```bash
IMGBB_API_KEY=your-imgbb-api-key
```

### 5. Migrations Yaratildi
- `apps/menu/migrations/0002_alter_menu_image_url.py`
- `apps/organizations/migrations/0002_alter_organization_logo.py`

### 6. Cloudinary O'chirildi
- ❌ Cloudinary packages removed from requirements.txt
- ❌ Cloudinary settings removed
- ❌ Cloudinary documentation deleted
- ✅ ImgBB documentation added

---

## 🚀 HOZIR NIMA QILISH KERAK?

### 1. Migrations Ishga Tushiring

```bash
# Virtual environment aktivlashtiring
source venv/bin/activate  # Mac/Linux
# yoki
venv\Scripts\activate  # Windows

# Migrations ishga tushiring
python manage.py migrate
```

### 2. Serverni Ishga Tushiring

```bash
python manage.py runserver
```

### 3. Test Qiling

#### Admin Panel orqali:
```
1. http://localhost:8000/admin/ ga kiring
2. Menu items → Add menu item
3. Rasm yuklang
4. Save qiling
5. Rasm avtomatik ImgBB'ga yuklanadi!
```

#### API orqali:
```bash
# Auth token oling
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Rasm yuklang
curl -X POST http://localhost:8000/api/menu/items/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Osh" \
  -F "price=2500000" \
  -F "category=CATEGORY_UUID" \
  -F "image=@/path/to/image.jpg"
```

#### Response:
```json
{
  "id": "uuid",
  "name": "Osh",
  "image_url": "https://i.ibb.co/abc123/image.jpg",
  "price": 2500000,
  "price_uzs": 25000.0
}
```

---

## 🌐 Production (Railway) Setup

### Railway Variables

Railway dashboard'da:

```
IMGBB_API_KEY=your-imgbb-api-key
```

Bu key allaqachon `.env` faylida mavjud!

### Deploy

```bash
# Railway'ga push qiling
git add .
git commit -m "ImgBB integration"
git push

# Yoki Railway CLI
railway up
```

### Migrations (Railway)

Railway avtomatik migrations ishga tushiradi. Agar kerak bo'lsa:

```bash
railway run python manage.py migrate
```

---

## 📸 Qanday Ishlaydi?

### Upload Process

1. **Client** rasm yuboradi (multipart/form-data)
2. **Serializer** rasm qabul qiladi
3. **ImgBB API** ga yuklaydi (base64 encoded)
4. **ImgBB** URL qaytaradi: `https://i.ibb.co/abc123/image.jpg`
5. **Database** ga URL saqlanadi
6. **Response** da URL qaytariladi

### Example Flow

```
Client → Django API → ImgBB API → ImgBB CDN
                ↓
           Database (URL)
                ↓
           Response (URL)
```

---

## 📝 API Documentation

### Menu Items

**Create with image:**
```http
POST /api/menu/items/
Content-Type: multipart/form-data
Authorization: Bearer {token}

Fields:
- name: string (required)
- price: integer (required)
- category: uuid (required)
- image: file (optional)
- description: string (optional)
- cook_time_minutes: integer (optional)
- ingredients: string (optional)
```

**Update with new image:**
```http
PUT /api/menu/items/{id}/
Content-Type: multipart/form-data
Authorization: Bearer {token}

Fields:
- image: file (optional)
- ... other fields
```

**Get menu items:**
```http
GET /api/menu/items/
Authorization: Bearer {token}

Response:
{
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "name": "Osh",
      "image_url": "https://i.ibb.co/abc123/image.jpg",
      "price": 2500000,
      "price_uzs": 25000.0
    }
  ]
}
```

### Organizations

**Create with logo:**
```http
POST /api/organizations/
Content-Type: multipart/form-data
Authorization: Bearer {token}

Fields:
- name: string (required)
- logo_file: file (optional)
- address: string (optional)
- phone: string (optional)
```

**Update logo:**
```http
PUT /api/organizations/{id}/
Content-Type: multipart/form-data
Authorization: Bearer {token}

Fields:
- logo_file: file (optional)
- ... other fields
```

---

## ✨ Features

### ✅ Avtomatik Upload
- Rasm yuklanganda avtomatik ImgBB'ga yuklanadi
- URL avtomatik database'ga saqlanadi
- Xatolik bo'lsa validation error

### ✅ Direct URLs
- ImgBB to'g'ridan-to'g'ri rasm URL beradi
- CDN orqali tez yuklanish
- HTTPS secure links

### ✅ No Limits
- Bepul va cheklovsiz
- Har qanday hajmdagi rasm (max 32MB)
- Har qanday format (JPG, PNG, GIF, WebP)

### ✅ Global CDN
- Tez yuklanish dunyoning istalgan joyidan
- 99.9% uptime
- HTTPS secure

---

## 🔍 Testing

### Check Settings

```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.IMGBB_API_KEY)
# Should print: your-imgbb-api-key
>>> print(settings.IMGBB_API_URL)
# Should print: https://api.imgbb.com/1/upload
```

### Test Upload

```bash
# Create test image
echo "Test" > test.txt

# Upload via API
curl -X POST http://localhost:8000/api/menu/items/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Test" \
  -F "price=1000000" \
  -F "category=UUID" \
  -F "image=@test_image.jpg"
```

### Check Response

```json
{
  "id": "uuid",
  "name": "Test",
  "image_url": "https://i.ibb.co/abc123/test_image.jpg",
  "price": 1000000
}
```

---

## ❓ Troubleshooting

### Rasm yuklanmayapti?

**1. API key tekshiring:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.IMGBB_API_KEY)
```

**2. Internet ulanishini tekshiring:**
```bash
curl https://api.imgbb.com/1/upload
# Should return error about missing image (this is OK)
```

**3. Rasm formatini tekshiring:**
- Supported: JPG, PNG, GIF, WebP, BMP
- Max size: 32 MB

### Migration xatosi?

```bash
# Migrations qayta ishga tushiring
python manage.py migrate --fake-initial

# Yoki
python manage.py migrate menu
python manage.py migrate organizations
```

### URL noto'g'ri?

- ImgBB URL format: `https://i.ibb.co/abc123/image.jpg`
- Agar boshqa format bo'lsa, serializer xatosi bor

---

## 📚 Documentation

- **IMGBB_SETUP.md** - Batafsil qo'llanma
- **README.md** - Umumiy ma'lumot
- **API Docs** - http://localhost:8000/ (Swagger)

---

## 🎉 TAYYOR!

### Oldin (Cloudinary):
- ❌ Uzbekistonda ishlamaydi
- ❌ Murakkab setup
- ❌ Cheklangan bepul plan

### Hozir (ImgBB):
- ✅ Uzbekistonda ishlaydi
- ✅ Oson setup (1 daqiqa)
- ✅ Bepul va cheklovsiz
- ✅ Tez va ishonchli
- ✅ API key allaqachon sozlangan

---

**Muvaffaqiyatli ishlar!** 🚀

**Keyingi qadam:** `python manage.py migrate` va `python manage.py runserver`
