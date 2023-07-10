from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    caregory = None
    caregorys = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        caregory = get_object_or_404(Category, slug=category_slug)
        products = products.filter(caregory=caregory)
    context = {'caregory': caregory, 'caregorys': caregorys, 'products': products}
    return render(request, 'shop/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    return render(request, 'shop/detail.html', {'product': product, 'cart_product_form': cart_product_form})
