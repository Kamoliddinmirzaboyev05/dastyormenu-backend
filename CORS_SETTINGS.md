# CORS Sozlamalari ✅

## O'zgartirilgan Fayllar

### 1. `config/settings/base.py`
- ✅ `corsheaders` INSTALLED_APPS ga qo'shildi
- ✅ `CorsMiddleware` MIDDLEWARE ga qo'shildi (eng yuqorida)
- ✅ CORS sozlamalari qo'shildi:
  - `CORS_ALLOW_ALL_ORIGINS = True` - Barcha domenlardan so'rovlarga ruxsat
  - `CORS_ALLOW_CREDENTIALS = True` - Cookie va authentication headerlariga ruxsat
  - Barcha HTTP metodlarga ruxsat (GET, POST, PUT, PATCH, DELETE, OPTIONS)
  - Barcha kerakli headerlarga ruxsat

### 2. `.env`
- ✅ `ALLOWED_HOSTS` ga `*` qo'shildi
- ✅ `CSRF_TRUSTED_ORIGINS` qo'shildi

## CORS Nima?

CORS (Cross-Origin Resource Sharing) - bu brauzerning xavfsizlik mexanizmi bo'lib, bir domendan (masalan, `http://localhost:3000`) boshqa domenga (masalan, `http://localhost:8000`) so'rov yuborishga ruxsat beradi.

## Hozirgi Sozlamalar (Development)

```python
# Barcha domenlardan so'rovlarga ruxsat
CORS_ALLOW_ALL_ORIGINS = True

# Cookie va authentication headerlariga ruxsat
CORS_ALLOW_CREDENTIALS = True

# Barcha HTTP metodlarga ruxsat
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# Barcha kerakli headerlarga ruxsat
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

## Test Qilish

### 1. Serverni ishga tushiring:
```bash
python manage.py runserver
```

### 2. Frontend dan so'rov yuboring:
```javascript
// React/Vue/Angular dan
fetch('http://localhost:8000/api/menu/items/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token-here'
  }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### 3. Postman/Insomnia dan test qiling:
- URL: `http://localhost:8000/api/menu/items/`
- Method: GET
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer your-token-here`

## Production uchun Sozlamalar

⚠️ **MUHIM**: Production da `CORS_ALLOW_ALL_ORIGINS = True` ishlatmang!

Production uchun `config/settings/production.py` da quyidagicha sozlang:

```python
# Production CORS Settings
CORS_ALLOW_ALL_ORIGINS = False  # False qiling!
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# .env da:
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://your-app.railway.app
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://your-app.railway.app
```

## Muammolarni Hal Qilish

### 1. CORS Error hali ham chiqsa:
```bash
# Serverni qayta ishga tushiring
python manage.py runserver
```

### 2. Browser cache ni tozalang:
- Chrome: Ctrl+Shift+Delete
- Firefox: Ctrl+Shift+Delete
- Safari: Cmd+Option+E

### 3. Browser console da xatolarni tekshiring:
- F12 ni bosing
- Console tabiga o'ting
- CORS xatolarini qidiring

### 4. Network tabda so'rovlarni tekshiring:
- F12 ni bosing
- Network tabiga o'ting
- So'rovlarni kuzating
- Response headers da `Access-Control-Allow-Origin` borligini tekshiring

## Xavfsizlik

### Development:
- ✅ `CORS_ALLOW_ALL_ORIGINS = True` - Hamma joydan so'rovlarga ruxsat
- ✅ `DEBUG = True` - Xatolarni ko'rsatadi
- ✅ `ALLOWED_HOSTS = *` - Barcha hostlarga ruxsat

### Production:
- ❌ `CORS_ALLOW_ALL_ORIGINS = False` - Faqat belgilangan domenlar
- ❌ `DEBUG = False` - Xatolarni yashiradi
- ❌ `ALLOWED_HOSTS = yourdomain.com` - Faqat sizning domeningiz

## Qo'shimcha Ma'lumot

- Django CORS Headers: https://github.com/adamchainz/django-cors-headers
- CORS MDN: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- Django Security: https://docs.djangoproject.com/en/5.0/topics/security/

## Status: ✅ TAYYOR

CORS sozlamalari to'liq sozlandi va ishlab chiqish jarayonida barcha linklarga ochiq!
