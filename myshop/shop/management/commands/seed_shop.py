from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from coupons.models import Coupon
from shop.models import Category, Product

# (en name, en slug, es name, es slug)
CATEGORIES = [
    ('Tea', 'tea', 'Té', 'te'),
    ('Coffee', 'coffee', 'Café', 'cafe'),
]

# (category slug, price, en name, en slug, es name, es slug, en description)
PRODUCTS = [
    ('tea', '12.50', 'Green tea', 'green-tea', 'Té verde', 'te-verde',
     'Delicate Japanese sencha with a fresh, grassy flavour.'),
    ('tea', '10.00', 'Red tea', 'red-tea', 'Té rojo', 'te-rojo',
     'Pu-erh tea aged for a deep, earthy taste.'),
    ('tea', '9.90', 'Tea powder', 'tea-powder', 'Té en polvo', 'te-en-polvo',
     'Ceremonial-grade matcha powder.'),
    ('coffee', '15.00', 'Arabica beans', 'arabica-beans',
     'Granos de arábica', 'granos-de-arabica',
     'Medium roast single-origin beans from Colombia.'),
    ('coffee', '13.75', 'Espresso blend', 'espresso-blend',
     'Mezcla espresso', 'mezcla-espresso',
     'Dark roast blend built for espresso machines.'),
]


class Command(BaseCommand):
    help = 'Create sample categories, products and a coupon (idempotent).'

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for en_name, en_slug, es_name, es_slug in CATEGORIES:
            category = Category.objects.filter(
                translations__language_code='en',
                translations__slug=en_slug,
            ).first() or Category()
            category.set_current_language('en')
            category.name, category.slug = en_name, en_slug
            category.set_current_language('es')
            category.name, category.slug = es_name, es_slug
            category.save()
            categories[en_slug] = category

        for cat, price, en_name, en_slug, es_name, es_slug, desc in PRODUCTS:
            product = Product.objects.filter(
                translations__language_code='en',
                translations__slug=en_slug,
            ).first() or Product(category=categories[cat])
            product.category = categories[cat]
            product.price = Decimal(price)
            product.available = True
            product.set_current_language('en')
            product.name, product.slug = en_name, en_slug
            product.description = desc
            product.set_current_language('es')
            product.name, product.slug = es_name, es_slug
            product.description = desc
            product.save()

        now = timezone.now()
        Coupon.objects.update_or_create(
            code='WELCOME10',
            defaults={
                'valid_from': now - timedelta(days=1),
                'valid_to': now + timedelta(days=365),
                'discount': 10,
                'active': True,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(CATEGORIES)} categories, {len(PRODUCTS)} '
            'products and coupon WELCOME10.'
        ))
