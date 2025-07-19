from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('api/invoices/', views.InvoiceListCreateView.as_view(), name='api_invoice_list_create'),
    path('api/invoices/<int:id>/pay/', views.make_payment, name='make_payment'),
    path('api/invoices/<int:id>/cancel/', views.cancel_invoice, name='cancel_invoice'),
    path('api/invoices/<int:id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('api/invoices/<int:id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('api/invoices/<int:id>/send-email/', views.send_invoice_email, name='send_invoice_email'),
    path('api/webhook/payment/', views.payment_webhook, name='payment_webhook'),
]
