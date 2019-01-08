from django.shortcuts import render_to_response,render,redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from django.urls import reverse
import datetime

from read_statistics.utils import get_seven_days_read_data, get_today_hot_data
from blog.models import Blog
from .forms import LoginForm,RegForm

def get_seven_day_hotdata():
    today = timezone.now().date()
    date = today -  datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date) \
                        .values('id','title') \
                        .annotate(read_num_sum=Sum('read_details__read_num')) \
                        .order_by('-read_num_sum')
    return blogs[:7]



def home(request):
    context = {}
    ct = ContentType.objects.get_for_model(Blog)
    read_count_list, dates = get_seven_days_read_data(ct)
    today_hot_data = get_today_hot_data(ct)

    seven_day_hotdata = cache.get('seven_day_hotdata')
    if seven_day_hotdata is None:
        seven_day_hotdata = get_seven_day_hotdata()
        cache.set('seven_day_hotdata', get_seven_day_hotdata, 10)
        print('calc')
    else:
        print('use cache')

    context['read_nums'] = read_count_list
    context['dates'] = dates
    context['today_hot_data'] = today_hot_data
    context['seven_day_hotdata'] = seven_day_hotdata
    return render(request, 'home.html', context)

def login(request):
    #如果是POST请求就是登陆，其他则是请求页面
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        #验证是否有效
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)

def register(request):
    if request.method == "POST":
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            password = reg_form.cleaned_data['password']
            email = reg_form.cleaned_data['email']
            #创建用户,这里顺序不一致会导致注册报错
            user = User.objects.create_user(username, email, password)
            user.save()
            #登陆
            user = auth.authenticate(username=username, password=password)  
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)
