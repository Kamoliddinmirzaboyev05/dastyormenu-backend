# Swagger'da Rasm Yuklash - Qo'llanma

## ✅ Swagger Yangilandi!

Endi Swagger'da rasm yuklash uchun `image` field ko'rinadi!

---

## 📸 Qanday Rasm Yuklash?

### 1. Swagger'ni Oching

```
http://localhost:8000/
```

### 2. Menu Item Yaratish

1. **POST /api/menu/** endpointini toping
2. **Try it out** tugmasini bosing
3. **Request body** da `multipart/form-data` tanlang
4. Quyidagi fieldlarni to'ldiring:

```
name: Osh
price: 2500000 (25,000 so'm = 2,500,000 tiyin)
category: <category-uuid>
image: [Choose File] - Rasm tanlang
description: Milliy taom
cook_time_minutes: 30
ingredients: Guruch, go'sht, sabzi, piyoz
is_available: true
sort_order: 0
```

5. **Execute** tugmasini bosing

### 3. Response

```json
{
  "id": "uuid",
  "name": "Osh",
  "image_url": "https://i.ibb.co/abc123/image.jpg",
  "price": 2500000,
  "price_uzs": 25000.0,
  "category": "uuid",
  "category_name": "Milliy taomlar"
}
```

---

## 🏢 Organization Logo Yuklash

### 1. POST /api/organizations/

1. **Try it out** tugmasini bosing
2. **Request body** da `multipart/form-data` tanlang
3. Fieldlarni to'ldiring:

```
name: Mening Restoranim
logo_file: [Choose File] - Logo tanlang
address: Toshkent, Amir Temur ko'chasi
phone: +998901234567
subscription_plan: trial
```

4. **Execute** tugmasini bosing

### 2. Response

```json
{
  "id": "uuid",
  "name": "Mening Restoranim",
  "logo": "https://i.ibb.co/xyz789/logo.jpg",
  "address": "Toshkent, Amir Temur ko'chasi",
  "phone": "+998901234567",
  "subscription_plan": "trial"
}
```

---

## 🔄 Rasmni Yangilash

### PUT /api/menu/{id}/

1. Menu item ID'sini kiriting
2. **Try it out** tugmasini bosing
3. **Request body** da `multipart/form-data` tanlang
4. Yangi rasm yuklang:

```
name: Osh (yangilangan)
image: [Choose File] - Yangi rasm
price: 2800000
```

5. **Execute** tugmasini bosing

---

## 📋 Swagger Schema

### Menu Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✅ | Menu item nomi |
| price | integer | ✅ | Narx (tiyin) |
| category | uuid | ✅ | Category ID |
| image | file | ❌ | Rasm fayli (JPG, PNG, GIF, WebP) |
| description | string | ❌ | Tavsif |
| cook_time_minutes | integer | ❌ | Tayyorlanish vaqti (daqiqa) |
| ingredients | string | ❌ | Tarkibi |
| is_available | boolean | ❌ | Mavjudligi |
| sort_order | integer | ❌ | Tartiblash |

### Organization Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✅ | Tashkilot nomi |
| logo_file | file | ❌ | Logo fayli (JPG, PNG, GIF, WebP) |
| address | string | ❌ | Manzil |
| phone | string | ❌ | Telefon |
| subscription_plan | enum | ❌ | trial, basic, pro, enterprise |

---

## 🎯 Muhim Eslatmalar

### 1. Content-Type

Swagger avtomatik `multipart/form-data` tanlaydi. Agar JSON ko'rsatsa, dropdown'dan `multipart/form-data` tanlang.

### 2. Image Field

- **Create** da: `image` field
- **Update** da: `image` field (yangi rasm)
- **Response** da: `image_url` (ImgBB URL)

### 3. Organization Logo

- **Create** da: `logo_file` field
- **Update** da: `logo_file` field (yangi logo)
- **Response** da: `logo` (ImgBB URL)

### 4. Supported Formats

- JPG/JPEG
- PNG
- GIF
- WebP
- BMP

Max size: 32 MB

---

## 🔍 Testing

### 1. Test Image Yarating

```bash
# Mac/Linux
curl -o test_image.jpg https://picsum.photos/800/600

# Yoki istalgan rasmni ishlating
```

### 2. Swagger'da Test Qiling

1. http://localhost:8000/ ga kiring
2. **POST /api/menu/** ni oching
3. **Try it out** bosing
4. Fieldlarni to'ldiring
5. `image` field'da **Choose File** bosing
6. `test_image.jpg` ni tanlang
7. **Execute** bosing

### 3. Response Tekshiring

```json
{
  "image_url": "https://i.ibb.co/abc123/test_image.jpg"
}
```

Bu URL brauzerda ochilishi kerak!

---

## 📱 cURL Example

Agar Swagger ishlamasa, cURL bilan test qiling:

```bash
# Get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}' \
  | jq -r '.access')

# Upload image
curl -X POST http://localhost:8000/api/menu/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Osh" \
  -F "price=2500000" \
  -F "category=CATEGORY_UUID" \
  -F "image=@test_image.jpg"
```

---

## ❓ Troubleshooting

### Swagger'da image field ko'rinmayapti?

1. Serverni qayta ishga tushiring:
```bash
python manage.py runserver
```

2. Brauzer cache'ni tozalang (Ctrl+Shift+R)

3. Swagger schema'ni yangilang:
```
http://localhost:8000/api/schema/
```

### multipart/form-data tanlash mumkin emas?

1. **Request body** dropdown'ni oching
2. `multipart/form-data` ni tanlang
3. Agar yo'q bo'lsa, serverni qayta ishga tushiring

### Image yuklanganda xato?

1. Rasm formatini tekshiring (JPG, PNG, GIF, WebP)
2. Rasm hajmini tekshiring (max 32MB)
3. IMGBB_API_KEY to'g'ri ekanligini tekshiring:
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.IMGBB_API_KEY)
```

---

## 🎉 Tayyor!

Endi Swagger'da:
- ✅ Image field ko'rinadi
- ✅ Rasm yuklash mumkin
- ✅ multipart/form-data support
- ✅ Logo yuklash mumkin
- ✅ To'liq documentation

**Muvaffaqiyatli ishlar!** 🚀
