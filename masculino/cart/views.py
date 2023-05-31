from concurrent.futures import process
from genericpath import exists
from django.shortcuts import render, redirect, get_object_or_404
from .models import*
from django.contrib.auth.decorators import login_required
# Create your views here.
import logging

def _cart_id(request):
    try:
        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart
    except Exception as error:
        logging.error(f'Error in _cart_id function : {str(error)}')

def add_cart(request, product_id):
    logging.info("****************************** Add Cart View ******************************")
    try:
        # import pdb; pdb.set_trace()
        current_user = request.user
        product = Product.objects.get(id=product_id)#get the product
        #check if the user is authenticated
        if current_user.is_authenticated:
            print("authenticated")
            product_variation = []
            if request.method =='POST':
                print("method post")
                for item in request.POST:
                    key = item
                    value = request.POST[key]
                    print(key,item)
                    try:
                        print("create variation")
                        variation = Variation.objects.get(product = product, variation_category__iexact = key,variation_value__iexact = value)
                        product_variation.append(variation)
                    except:
                        pass
                print(product_variation)

            is_cart_item_exist = CartItem.objects.filter(product = product, user=current_user).exists()
            if is_cart_item_exist:
                print("if cart exist then block")
                cart_item = CartItem.objects.filter(product = product, user = current_user)
                #existing variations -> database
                #current variation -> product_variation
                #item_id ->database
                ex_var_list = []
                id  =[]
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)
                if product_variation in ex_var_list:
                    #increase the cart item quantity
                    id_idx = ex_var_list.index(product_variation)
                    item_id = id[id_idx]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity+=1
                    item.save()
                else:
                    item = CartItem.objects.create(product=product, user=current_user,quantity = 1)
                    if len(product_variation)>0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
            else:
                print("if cart not exist")
                cart_item = CartItem.objects.create(product = product, user = current_user, quantity = 1)
                if len(product_variation)>0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
            return redirect('cart')
        
        #is the user is not authenticated
        else:
            product_variation = []
            if request.method =='POST':
                for item in request.POST:
                    key = item
                    value = request.POST[key]
                    try:
                        variation = Variation.objects.get(product = product, variation_category__iexact = key,variation_value__iexact = value)
                        product_variation.append(variation)
                    except:
                        pass
                print(product_variation)

            try:
                #get the cart using the cart_id present in the session
                cart = Cart.objects.get(cart_id = _cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id = _cart_id(request))

            cart.save()

            is_cart_item_exist = CartItem.objects.filter(product = product, cart=cart)
            if is_cart_item_exist:
                cart_item = CartItem.objects.filter(product = product, cart = cart)

                #existing variations -> database
                #current variation -> product_variation
                #item_id ->database
                ex_var_list = []
                id  =[]
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)
                if product_variation in ex_var_list:
                    #increase the cart item quantity
                    id_idx = ex_var_list.index(product_variation)
                    item_id = id[id_idx]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity+=1
                    item.save()
                else:
                    item = CartItem.objects.create(product=product, cart=cart,quantity = 1)
                    if len(product_variation)>0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
            else:
                cart_item = CartItem.objects.create(product = product, cart = cart, quantity = 1)
                if len(product_variation)>0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
            return redirect('cart')
        
    except Exception as error:
        logging.error(f'Error in add cart function : {str(error)}')        

def remove_cart(request, product_id, cart_item_id):
    logging.info("****************************** Remove Cart View ******************************")
    try:
        product = get_object_or_404(Product, id = product_id)
        try:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(product = product, user= request.user, id=cart_item_id)
            else:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                cart_item = CartItem.objects.get(product = product, cart= cart, id=cart_item_id)

            if cart_item.quantity>1:
                cart_item.quantity -=1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
        return redirect('cart')
    except Exception as error:
        logging.error(f'Error in remove cart function : {str(error)}')

def remove_cart_item(request, product_id, cart_item_id):
    logging.info("****************************** Remove Cart Item View ******************************")
    try:
        product = get_object_or_404(Product, id = product_id)
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user= request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart= cart, id=cart_item_id)
        cart_item.delete()
        return redirect('cart')
    except Exception as error:
        logging.error(f'Error in remove cart item function : {str(error)}')

def cart(request, quantity=0, total=0, cart_items = None):
    logging.info("****************************** Cart View ******************************")
    try:
        try:
            tax=0
            grand_total=0
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user = request.user, is_active = True)
            else:
                try:
                    cart = Cart.objects.get(cart_id = _cart_id(request))
                except Exception as e:
                    logging.error(f'Error in cart function : {str(e)}')
                    print("Exception Raised: ",e)
                    return render(request, 'cart/cart.html')
                cart_items = CartItem.objects.filter(cart = cart, is_active = True)
            for cart_item in cart_items:
                total += (int(cart_item.product.price) * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (1 * total)/100
            grand_total = tax + total
        except Exception as e:
            logging.error(f'Error in cart function : {str(e)}')
            print('Error : ', e)
        
        context ={
            'total' : total,
            'quantity' : quantity,
            'cart_items' : cart_items,
            'tax' : tax,
            'grand_total' : grand_total,
        }
            
        return render(request, 'cart/cart.html', context)
    except Exception as error:
        logging.error(f'Error in cart function : {str(error)}')

@login_required(login_url='login')
def checkout(request, quantity=0, total=0, cart_items = None):
    logging.info("****************************** Checkout View ******************************")
    try:
        # import pdb;
        # pdb.set_trace()
        try:
            tax=0
            grand_total=0
            print(_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user = request.user, is_active = True)
            else:
                try:
                    cart = Cart.objects.get(cart_id = _cart_id(request))
                except Exception as e:
                    logging.error(f'Error in cart function : {str(e)}')
                    print("Exception Raised: ",e)
                    return render(request, 'cart/cart.html')
                cart_items = CartItem.objects.filter(cart = cart, is_active = True)
            for cart_item in cart_items:
                total += (int(cart_item.product.price) * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (1 * total)/100
            grand_total = tax + total
        except Exception as e:  
            logging.error(f'Error in checkout function : {str(e)}')
            print('Error : ', e)
        
        context ={
            'total' : total,
            'quantity' : quantity,
            'cart_items' : cart_items,
            'tax' : tax,
            'grand_total' : grand_total,
        }
        return render(request, 'store/checkout.html', context)
    except Exception as error:
        logging.error(f'Error in checkout function : {str(error)}')