from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from cart.views import _cart_id
from .models import *
from home.models import Category
from cart.models import CartItem
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.db.models import Q
# Create your views here.
import logging

def store(request, category_slug = None):
    logging.info("****************************** Store View ******************************")
    try:
        categories = None
        products = None

        if category_slug != None:
            categories = get_object_or_404(Category, slug = category_slug)
            products = Product.objects.filter(category = categories, is_available = True)

        else:
            products = Product.objects.all().filter(is_available = True)
            
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

        context = {
            'products':paged_products,
            'category_name':categories,
            'product_count':product_count,
        }
        return render(request,'store/store.html',context)
    except Exception as error:
        logging.error(f'Error in store views function : {str(error)}')

def product_detail(request, category_slug, product_slug):
    logging.info("****************************** Product Detail View ******************************")
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
        context = {'single_product':single_product, 'in_cart': in_cart}
        return render(request, 'store/product_detail.html', context)
    except Exception as error:
        logging.error(f'Error in product_detail function : {str(error)}')

def search(request):
    logging.info("****************************** Search View ******************************")
    try:
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
            if keyword:
                products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword) )
            # paginator = Paginator(products, 8)
            # page = request.GET.get('page')
            # paged_products = paginator.get_page(page)
            product_count = products.count()
            context ={
                'products':products,
                'product_count':product_count,
            }
        return render(request,'store/store.html',context)
    except Exception as error:
        logging.error(f'Error in search function : {str(error)}')
