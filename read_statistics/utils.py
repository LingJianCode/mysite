import datetime
from django.contrib.contenttypes.models import ContentType
from .models import ReadNum,ReadDetail
from django.utils import timezone
from django.db.models import Sum


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        readnum, created = ReadNum.objects.get_or_create(content_type = ct, object_id = obj.pk)
        readnum.read_num += 1
        readnum.save()

        date = timezone.now().date()
        readdetail, created = ReadDetail.objects.get_or_create(content_type = ct, object_id = obj.pk, date=date)
        readdetail.read_num += 1
        readdetail.save()
    return key

def get_seven_days_read_data(content_type):
    today = timezone.now().date()

    dates = []
    read_count_list = []
    for i in range(6, -1 , -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_detail = ReadDetail.objects.filter(content_type=content_type, date=date)
        read_count = read_detail.aggregate(read_count=Sum('read_num'))
        read_count_list.append(read_count['read_count'] or 0)

    return read_count_list, dates


def get_today_hot_data(content_type):
    date = timezone.now().date()
    today_hot_data = ReadDetail.objects.filter(content_type=content_type, date=date).order_by('-read_num')
    #返回前7条
    return today_hot_data[:7]
