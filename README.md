# Invoice & Payment Management System

A Django-based ERP module to manage customer invoices, record payments (partial/full), and integrate with accounting and payment systems.

## Features

- Customer & Invoice models
- Line item support (Invoice Items)
- Partial / full payment recording
- Status auto-update (Unpaid, Partially Paid, Paid, Cancelled)
- AJAX-powered frontend (Bootstrap + jQuery)
- Role-based access (Manager/User)
- Cancel unpaid invoices
- Generate PDF invoices with `xhtml2pdf`
- Send invoice via email (Gmail SMTP)
- Multi-currency support
- Ledger integration (credit entries on payment)
- Webhook endpoint for external payment gateways

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Load sample data including superuser, testuser, customer, and invoice
python manage.py setup_dev_data

# Run the server
source venv/Scripts/activate
python manage.py runserver
```

## Configuration

### Email (Gmail SMTP)
Edit `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### PDF Engine
```bash
pip install xhtml2pdf
```
Used for PDF invoice generation and email attachments.

## Webhook (Payment Gateway)

POST `/api/webhook/payment/`
```json
{
  "invoice_id": 2,
  "amount": "100.00"
}
```

## Endpoints

- `GET /api/invoices/` – list invoices
- `POST /api/invoices/` – create invoice
- `POST /api/invoices/<id>/pay/` – make payment
- `DELETE /api/invoices/<id>/delete/` – delete unpaid invoice
- `GET /api/invoices/<id>/pdf/` – download invoice PDF
- `POST /api/webhook/payment/` – payment webhook

## Folder Structure

```
invoice_system/
├── invoice/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/invoice/
│   │   └── invoice_list.html
│   │   └── pdf_template.html
│   ├── static/invoice/js/
│   │   └── invoice.js
```

---

## Built With
- Django + Django REST Framework
- xhtml2pdf
- Bootstrap 5 + jQuery
- Gmail SMTP