import datetime
import json
import random
from threading import Thread

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from arashsport.models import UserWishList, Product
from user_auth.forms import ProfileForm
from user_auth.models import User


def session_is_valid(request):
    if request.user.is_authenticated:
        return redirect('arashsport:home')
    if request.session.get('otp') is None:
        return JsonResponse({'status': 'not valid'})
    else:
        return JsonResponse({'status': 'valid'})

def send_otp_code(request):
    if request.user.is_authenticated:
        return redirect('arashsport:home')
    otp = request.session.get('otp')
    if otp is None:
        email = json.loads(request.body)['email']
        request.session['otp'] = otp = {'email': email}
    if json.loads(request.body)['email'] != '' and json.loads(request.body)['email'] != otp['email']:
        request.session['otp']['email'] = json.loads(request.body)['email']
    expire_time = datetime.datetime.min if otp.get(
        'expire_time') is None else datetime.datetime.fromisoformat(otp.get('expire_time'))
    if expire_time < datetime.datetime.now():
        code = ''.join(random.choices('0123456789', k=6))
        expire_time = datetime.datetime.now() + datetime.timedelta(seconds=55)
        request.session['otp'].update({'code': code, 'expire_time': expire_time.isoformat()})

        email_obj = EmailMessage(
            subject='کد ورود',
            to=[request.session.get('otp')['email']],
            body=f'{code}'
        )
        # Thread(target=email_obj.send,kwargs={'fail_silently':False}).start()
        request.session.modified = True
        print(code)
        return JsonResponse({'status': 'ok', 'msg': 'کد تایید با موفقیت ارسال گردید'})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('arashsport:home')
    if request.method == "POST":
        (user, created) = User.objects.get_or_create(email=request.session['otp']['email'])
        current_date = datetime.datetime.now()
        expire_time = datetime.datetime.fromisoformat(request.session.get('otp')['expire_time'])
        code_session = request.session.get('otp')['code']
        if code_session == request.POST['code'] and user and expire_time > current_date:
            del request.session['otp']
            login(request, user)
            if created:
                messages.info(request, 'حساب کاربری با موفقیت ایجاد شد')
            else:
                messages.info(request, 'با موفقیت وارد شدید')

            return redirect('arashsport:home')
        elif code_session != request.POST['code'] or expire_time <= current_date:
            messages.error(request, 'کد تایید نا معتبر است')
        elif not user:
            messages.error(request, 'ایمیل نامعتبر هست')

        context = {'req_value': request.POST}
    if request.method == 'GET':
        context = {}

    return render(request, 'html/user_auth/register.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'با موفقیت خارج شدید')
    return redirect('arashsport:home')

def profile_view(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        form = ProfileForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
    if request.method == 'GET':
        form = ProfileForm(instance=request.user)
    context = {
        'form': form,
        'wish_lists':Product.objects.filter(wishes__user=request.user)
    }
    return render(request,'html/user_auth/profile.html',context)

