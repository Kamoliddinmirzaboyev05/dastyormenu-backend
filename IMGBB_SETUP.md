# ImgBB Image Hosting - Setup Guide

## ✅ Nima Qilindi?

Cloudinary o'rniga **ImgBB** integratsiya qilindi chunki:
- ✅ Uzbekistonda ishlaydi
- ✅ Bepul va cheklovsiz
- ✅ API key allaqachon sozlangan
- ✅ Tez va oson

---

## 🎯 ImgBB Afzalliklari

- 🌍 **Global CDN** - Tez yuklanish
- 🆓 **Bepul** - Cheklovsiz yuklash
- 🇺🇿 **Uzbekistonda ishlaydi** - Blokirovka yo'q
- 🔒 **HTTPS** - Xavfsiz
- 📱 **Direct links** - To'g'ridan-to'g'ri rasm URL
- ⚡ **Tez** - API orqali yuklash

---

## 🚀 Qanday Ishlaydi?

### 1. Rasm Yuklash (API orqali)

```bash
# Menu item yaratish (rasm bilan)
curl -X POST http://localhost:8000/api/menu/items/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Osh" \
  -F "price=2500000" \
  -F "category=CATEGORY_UUID" \
  -F "image=@/path/to/image.jpg"
```

### 2. Response

```json
{
  "id": "uuid",
  "name": "Osh",
  "image_url": "https://i.ibb.co/abc123/image.jpg",
  "price": 2500000,
  "price_uzs": 25000.0
}
```

### 3. Rasm URL

ImgBB avtomatik ravishda rasm URL qaytaradi:
```
https://i.ibb.co/abc123/image.jpg
```

---

## 📝 API Endpoints

### Menu Items

**Create with image:**
```http
POST /api/menu/items/
Content-Type: multipart/form-data

{
  "name": "Osh",
  "price": 2500000,
  "category": "uuid",
  "image": <file>
}
```

**Update with new image:**
```http
PUT /api/menu/items/{id}/
Content-Type: multipart/form-data

{
  "name": "Osh",
  "image": <new_file>
}
```

**Get menu items:**
```http
GET /api/menu/items/

Response:
{
  "results": [
    {
      "id": "uuid",
      "name": "Osh",
      "image_url": "https://i.ibb.co/abc123/image.jpg",
      "price": 2500000
    }
  ]
}
```

### Organizations

**Create with logo:**
```http
POST /api/organizations/
Content-Type: multipart/form-data

{
  "name": "My Restaurant",
  "logo_file": <file>
}
```

**Update logo:**
```http
PUT /api/organizations/{id}/
Content-Type: multipart/form-data

{
  "logo_file": <new_file>
}
```

---

## 🔧 Technical Details

### Models Changed

**Menu Model:**
```python
# Before: ImageField
image_url = models.ImageField(upload_to='menu/items/')

# After: URLField
image_url = models.URLField(max_length=500, null=True, blank=True)
```

**Organization Model:**
```python
# Before: ImageField
logo = models.ImageField(upload_to='organizations/logos/')

# After: URLField
logo = models.URLField(max_length=500, null=True, blank=True)
```

### Serializers

**MenuSerializer:**
- `image` (write_only) - Rasm yuklash uchun
- `image_url` (read_only) - ImgBB URL

**OrganizationSerializer:**
- `logo_file` (write_only) - Logo yuklash uchun
- `logo` (read_only) - ImgBB URL

### Upload Process

1. Client rasm yuboradi (multipart/form-data)
2. Serializer rasm qabul qiladi
3. ImgBB API'ga yuklaydi (base64)
4. ImgBB URL qaytaradi
5. Database'ga URL saqlanadi

---

## 🌐 Production (Railway) Setup

### Environment Variables

Railway dashboard'da:

```
IMGBB_API_KEY=your-imgbb-api-key
```

Bu key allaqachon `.env` faylida sozlangan!

---

## 📱 Admin Panel

Admin panel orqali ham rasm yuklash mumkin:

1. http://localhost:8000/admin/ ga kiring
2. Menu items → Add menu item
3. Image field'ga rasm tanlang
4. Save qiling
5. Rasm avtomatik ImgBB'ga yuklanadi!

---

## ✨ Features

### Avtomatik Upload
- Rasm yuklanganda avtomatik ImgBB'ga yuklanadi
- URL avtomatik database'ga saqlanadi
- Xatolik bo'lsa validation error qaytaradi

### Direct URLs
- ImgBB to'g'ridan-to'g'ri rasm URL beradi
- CDN orqali tez yuklanish
- HTTPS secure links

### No Storage Limits
- Bepul va cheklovsiz
- Har qanday hajmdagi rasm
- Har qanday format (JPG, PNG, GIF, WebP)

---

## 🔍 Testing

### Test Image Upload

```bash
# 1. Get auth token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# 2. Upload image
curl -X POST http://localhost:8000/api/menu/items/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Test Dish" \
  -F "price=1000000" \
  -F "category=CATEGORY_UUID" \
  -F "image=@test_image.jpg"

# 3. Check response
# image_url should be: https://i.ibb.co/...
```

### Test in Browser

1. Open http://localhost:8000/api/menu/items/
2. Click "POST" button
3. Fill form and upload image
4. Submit
5. Check `image_url` in response

---

## ❓ Troubleshooting

### Image not uploading?

**Check API key:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.IMGBB_API_KEY)
# Should print: your-imgbb-api-key
```

**Check internet connection:**
```bash
curl https://api.imgbb.com/1/upload
# Should return: {"status_code":400,"error":{"message":"No image provided"}}
```

### Invalid image format?

ImgBB supports:
- JPG/JPEG
- PNG
- GIF
- WebP
- BMP

Max size: 32 MB

### Upload timeout?

Increase timeout in serializers:
```python
response = requests.post(settings.IMGBB_API_URL, data=payload, timeout=60)
```

---

## 📊 Monitoring

### Check uploaded images

Visit: https://ibb.co/account/images

(Login with ImgBB account if you have one)

### API Response

```json
{
  "data": {
    "url": "https://i.ibb.co/abc123/image.jpg",
    "display_url": "https://i.ibb.co/abc123/image.jpg",
    "size": 123456,
    "time": "1234567890",
    "expiration": "0"
  },
  "success": true,
  "status": 200
}
```

---

## 🎉 Summary

### Before (Cloudinary):
- ❌ Uzbekistonda ishlamaydi
- ❌ Murakkab setup
- ❌ Cheklangan bepul plan

### Now (ImgBB):
- ✅ Uzbekistonda ishlaydi
- ✅ Oson setup (1 daqiqa)
- ✅ Bepul va cheklovsiz
- ✅ Tez va ishonchli

---

**Muvaffaqiyatli ishlar!** 🚀
