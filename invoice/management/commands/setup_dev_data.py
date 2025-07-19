from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from invoice.models import Customer, Invoice, InvoiceItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Set up development data: groups, superuser, sample customers/invoices'

    def handle(self, *args, **kwargs):
        # Create groups
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        user_group, _ = Group.objects.get_or_create(name='User')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin1234')
            admin.groups.add(manager_group)
            self.stdout.write(self.style.SUCCESS('Created superuser admin'))
        else:
            self.stdout.write(self.style.WARNING('Superuser admin already exists'))

        # Create test user
        if not User.objects.filter(username='user').exists():
            user = User.objects.create_user('user', 'user@gmail.com', 'user1234')
            user.groups.add(user_group)
            self.stdout.write(self.style.SUCCESS('Created test user'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))

        # Create sample customers
        customer, _ = Customer.objects.get_or_create(name='customerone', email='kglay9533@gmail.com', address='Yangon')
        
        # Create sample invoice
        invoice = Invoice.objects.create(
            customer=customer,
            total_amount=Decimal('300.00'),
            due_amount=Decimal('300.00'),
            status='UNPAID'
        )

        InvoiceItem.objects.create(invoice=invoice, description='Consulting Service', quantity=3, unit_price=100)

        self.stdout.write(self.style.SUCCESS('Created sample customer and invoice'))