# ✅ Swagger Documentation Yangilandi!

## 📝 O'zgarishlar

Barcha POST metodlarga `@extend_schema` decorator qo'shildi va endi Swagger UI da ma'lumot kiritish imkoniyati mavjud.

## 🔧 Yangilangan Fayllar

### 1. apps/users/views.py
- ✅ `login_view` - LoginSerializer bilan
- ✅ `pin_login_view` - PinLoginSerializer bilan
- ✅ `logout_view` - Request body yo'q
- ✅ `set_pin` action - SetPinSerializer bilan

### 2. apps/menu/views.py
- ✅ `toggle_availability` action - Request body yo'q (toggle)

### 3. apps/menu/public_views.py
- ✅ `public_menu` - Query parameter (qr) bilan

### 4. apps/orders/views.py
- ✅ `update_status` action - OrderStatusSerializer bilan
- ✅ `public_create_order` - PublicOrderSerializer bilan
- ✅ `public_order_status` - Path parameter bilan

### 5. apps/tables/views.py
- ✅ `regenerate_qr` action - Request body yo'q

### 6. apps/payments/views.py
- ✅ `confirm` action - PaymentConfirmSerializer bilan

### 7. apps/notifications/views.py
- ✅ `mark_read` action - Request body yo'q
- ✅ `mark_all_read` action - Request body yo'q

## 📊 Swagger Schema

### POST Endpoints bilan Request Body:

1. **Authentication**
   - `/api/auth/login/` - email, password
   - `/api/auth/pin-login/` - organization_id, pin_code
   - `/api/auth/refresh/` - refresh token

2. **Categories**
   - `/api/categories/` - name, icon, sort_order

3. **Menu**
   - `/api/menu/` - name, description, price, category, etc.

4. **Orders**
   - `/api/orders/` - table, items, notes
   - `/api/orders/{id}/update-status/` - status
   - `/api/public/orders/` - qr_code_id, items

5. **Tables**
   - `/api/tables/` - table_number, assigned_waiter

6. **Payments**
   - `/api/payments/` - order, amount, method
   - `/api/payments/{id}/confirm/` - transaction_id

7. **Organizations**
   - `/api/organizations/` - name, address, phone, etc.

8. **Users**
   - `/api/users/` - user data, role, organization
   - `/api/users/{id}/set-pin/` - pin_code

## 🎯 Swagger UI da Test Qilish

### 1. Swagger UI ga Kirish
```
http://localhost:8000/api/docs/
```

### 2. POST Endpoint Tanlash
Har qanday POST metodini bosing, masalan `/api/auth/login/`

### 3. "Try it out" Tugmasini Bosing
O'ng tarafda "Try it out" tugmasi paydo bo'ladi

### 4. Ma'lumot Kiriting
Request body maydonida JSON formatda ma'lumot kiriting:
```json
{
  "email": "manager@test.com",
  "password": "password123"
}
```

### 5. "Execute" Tugmasini Bosing
So'rov yuboriladi va natija ko'rsatiladi

## 📋 Misol: Login Test

### Request:
```json
{
  "email": "manager@test.com",
  "password": "password123"
}
```

### Response (200 OK):
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "...",
    "full_name": "Test Manager",
    "role": "manager",
    "organization": "..."
  }
}
```

## 🔐 Authentication

### Token Olish
1. `/api/auth/login/` orqali login qiling
2. `access_token` ni nusxalang

### Token Ishlatish
1. Swagger UI tepasida "Authorize" tugmasini bosing
2. Token ni kiriting: `Bearer YOUR_ACCESS_TOKEN`
3. "Authorize" tugmasini bosing
4. Endi barcha protected endpointlarni test qilishingiz mumkin

## ✅ Natija

Barcha POST metodlarda:
- ✅ Request body schema ko'rsatiladi
- ✅ Required fieldlar belgilangan
- ✅ Field type va format ko'rsatiladi
- ✅ Example values mavjud
- ✅ "Try it out" funksiyasi ishlaydi
- ✅ Validation xatolari to'g'ri ko'rsatiladi

## 🌐 Foydali Linklar

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Admin Panel**: http://localhost:8000/admin/

## 📚 Qo'shimcha Ma'lumot

### ViewSet lar
ViewSet larda `@extend_schema` decorator kerak emas, chunki DRF avtomatik ravishda serializer dan schema yaratadi. Faqat custom action larga qo'shildi.

### Custom API Views
`@api_view` decorator bilan yaratilgan barcha view larga `@extend_schema` qo'shildi.

### Query Parameters
GET metodlar uchun `OpenApiParameter` ishlatildi (masalan, `public_menu` da `qr` parameter).

Omad! 🚀
