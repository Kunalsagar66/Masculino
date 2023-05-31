from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import Account
from cart.models import Cart,CartItem
from cart.views import _cart_id

import logging
import requests
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    logging.info("****************************** Register View ******************************")
    try:
        if request.method == "POST":
            form = RegistrationForm(request.POST)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone_number = form.cleaned_data['phone_number']
                password = form.cleaned_data['password']
                username = email.split('@')[0]
                user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,username=username, password=password)
                user.phone_number = phone_number
                user.save()

                #user activation
                current_site =get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('accounts/account_verfication.html',{
                    'user':user,
                    'domain':current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject,message,to=[to_email])
                send_email.send()

                messages.success(request, 'Thankyou for registration. We have sent you an email please verify.')
                return redirect('register')
        else:
            form = RegistrationForm()
        context ={
            'form' : form
        }
        return render(request, 'accounts/register.html',context)
    except Exception as error:
        logging.error(f'Error in resgistering user : {str(error)}')

def login(request):
    logging.info("****************************** Login View ******************************")

    try:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)

            if user is not None:
                
                try:
                    cart = Cart.objects.get(cart_id = _cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        
                        #getting the product variation by cart id
                        product_variation=[]
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                        #get the cart item from the user to access his product variation
                        cart_item = CartItem.objects.filter(user = user)
                        ex_var_list = []
                        id  =[]
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity+=1
                                item.user=user
                                item.save()
                            else:
                                cart_item=CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
                except:
                    pass
                auth.login(request, user)
                url = request.META.get('HTTP_REFERER')
                print(url)
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('dashboard')

            else:
                messages.error(request, 'Invalid credentials!')
                return redirect('login')

        return render(request, 'accounts/login.html')
    except Exception as error:
        logging.error(f'Error in Login : {str(error)}')

@login_required(login_url = 'login')
def logout(request):
     logging.info("****************************** Logout View ******************************")
     try:
        auth.logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('login')
     except Exception as error:
        logging.error(f'Error in Logout : {str(error)}')

def activate(request, uidb64, token):
    logging.info("****************************** Activate View ******************************")
    try:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active =True
            user.save()
            messages.success(request, 'Your account is activated!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid activation link!')
            return redirect('login')
    except Exception as error:
        logging.error(f'Error in activate account views : {str(error)}')
    
@login_required(login_url = 'login')
def dashboard(request):
     logging.info("****************************** Dashboard View ******************************")
     try:
         return render(request, 'accounts/dashboard.html')
     except Exception as error:
        logging.error(f'Error in Dashboard : {str(error)}')

def forgotPassword(request):
    logging.info("****************************** Forgot Password View ******************************")
    try:
        if request.method =='POST':
            email = request.POST['email']
            if Account.objects.filter(email=email).exists():
                user = Account.objects.get(email__iexact=email)

                #reset password email
                current_site =get_current_site(request)
                mail_subject = 'Reset Your Password'
                message = render_to_string('accounts/reset_password_email.html',{
                    'user':user,
                    'domain':current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject,message,to=[to_email])
                send_email.send()

                messages.success(request,"Password reset email has been sent to your email address.")
                return redirect('login')

            else:
                messages.error(request, "Account does not exist!")
                return render(request, 'accounts/forgot_password.html')
            
        return render(request, 'accounts/forgot_password.html')
    except Exception as error:
        logging.error(f'Error in forgot password : {str(error)}')

def reset_password_validate(request, uidb64, token):
    logging.info("****************************** Reset password validation View ******************************")
    try:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid']=uid
            messages.success(request, 'Please reset your password!')
            return redirect('resetPassword')
        else:
            messages.error(request, 'Invalid activation link!')
            return redirect('login')
    except Exception as error:
        logging.error(f'Error in reset password validation : {str(error)}')

def resetPassword(request):
    logging.info("****************************** Reset Password View ******************************")
    try:
        if request.method == 'POST':
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if password == confirm_password:
                uid = request.session.get('uid')
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, "Password reset success!")
                return redirect('login')
            else:
                messages.error(request, "Password do not match!")
                return redirect('resetPassword')
        return render(request, 'accounts/reset_password.html')
    except Exception as error:
        logging.error(f'Error in reset password : {str(error)}')
