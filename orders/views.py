from django.shortcuts import render
from .forms import OrderCreateForm
from .models import Order, OrderItem
from cart.cart import Cart
from .task import order_created
from django.urls import reverse
from django.shortcuts import redirect


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            order_created.delay(order.id)
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))

    else:
        form = OrderCreateForm()
    return render(request, 'orders/create.html', {'form': form, 'cart': cart})




