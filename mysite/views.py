from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
import datetime
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data
from blog.models import Blog

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
