from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Invoice, Payment
from decimal import Decimal
from rest_framework import generics
from .serializers import InvoiceSerializer
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa
import io
from django.core.mail import EmailMessage
from .models import LedgerEntry
import json

@login_required
def invoice_list(request):
    invoices_by_status = {
        'Unpaid': Invoice.objects.filter(status='UNPAID'),
        'Paid': Invoice.objects.filter(status='PAID'),
        'Partially Paid': Invoice.objects.filter(status='PARTIALLY_PAID'),
        'Cancelled': Invoice.objects.filter(status='CANCELLED'),
    }
    is_manager = request.user.groups.filter(name__iexact='Manager').exists()
    return render(request, 'invoice/invoice_list.html', {'invoices_by_status': invoices_by_status, 'is_manager': is_manager})

class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        queryset = Invoice.objects.all()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status__iexact=status)
        return queryset

@csrf_exempt
@require_POST
def make_payment(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    amount = Decimal(request.POST.get('amount'))

    if amount <= 0 or amount > invoice.due_amount:
        return JsonResponse({'error': 'Invalid amount'}, status=400)

    Payment.objects.create(invoice=invoice, amount=amount)
    invoice.due_amount -= amount

    if invoice.due_amount == 0:
        invoice.status = 'PAID'
    elif invoice.due_amount < invoice.total_amount:
        invoice.status = 'PARTIALLY_PAID'

    invoice.save()

    # Create ledger entry
    LedgerEntry.objects.create(
        invoice=invoice,
        entry_type='CREDIT',
        amount=amount,
        description=f'Payment received for Invoice #{invoice.id}'
    )
    return JsonResponse({'status': invoice.status})

@require_POST
def cancel_invoice(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    if request.user.groups.filter(name='Manager').exists() and invoice.status == 'UNPAID':
        invoice.status = 'CANCELLED'
        invoice.save()
        return JsonResponse({'status': 'cancelled'})
    return JsonResponse({'error': 'unauthorized'}, status=403)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_invoice(request, id):
    invoice = get_object_or_404(Invoice, id=id)

    if invoice.payments.exists():
        return JsonResponse({'error': 'Cannot delete invoice with payments'}, status=400)

    invoice.delete()
    return JsonResponse({'status': 'deleted'})

@csrf_exempt
@require_http_methods(["GET"])
def generate_invoice_pdf(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    html = render_to_string("invoice/pdf_template.html", {"invoice": invoice})
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return JsonResponse({'error': 'PDF generation failed'}, status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.pdf'
    return response

@csrf_exempt
@require_http_methods(["POST"])
def send_invoice_email(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    html = render_to_string("invoice/pdf_template.html", {"invoice": invoice})
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return JsonResponse({'error': 'Email PDF generation failed'}, status=500)

    subject = f"Invoice #{invoice.id} from Your Company"
    body = f"Dear {invoice.customer.name},\n\nPlease find attached your invoice. You can also pay online here: http://localhost:8000/invoices/"
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invoice.customer.email],
    )
    email.attach(f'invoice_{invoice.id}.pdf', result.getvalue(), 'application/pdf')
    email.send(fail_silently=False)

    return JsonResponse({"status": "sent"})

# Add webhook endpoint for payment gateway integration
@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request):
    try:
        data = json.loads(request.body)
        invoice_id = data.get('invoice_id')
        amount = Decimal(data.get('amount'))

        invoice = Invoice.objects.get(id=invoice_id)

        if amount <= 0 or amount > invoice.due_amount:
            return JsonResponse({'error': 'Invalid payment amount'}, status=400)

        Payment.objects.create(invoice=invoice, amount=amount)
        invoice.due_amount -= amount

        if invoice.due_amount == 0:
            invoice.status = 'PAID'
        elif invoice.due_amount < invoice.total_amount:
            invoice.status = 'PARTIALLY_PAID'

        invoice.save()

        LedgerEntry.objects.create(
            invoice=invoice,
            entry_type='CREDIT',
            amount=amount,
            description=f'Webhook payment received for Invoice #{invoice.id}'
        )

        return JsonResponse({'status': invoice.status})

    except Invoice.DoesNotExist:
        return JsonResponse({'error': 'Invoice not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

