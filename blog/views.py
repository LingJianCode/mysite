from django.shortcuts import render_to_response,get_object_or_404
from .models import Blog,BlogType,ReadNum
from django.core.paginator import Paginator
from django.db.models import Count
from datetime import datetime

def get_blog_list_common_date(blogs_all_list, request):
    paginator = Paginator(blogs_all_list, 10)
    page_num = request.GET.get('page',1)
    page_of_blogs = paginator.get_page(page_num)
    currenter_page_num = page_of_blogs.number
    page_range = [ x for x in range(max(currenter_page_num - 2, 1) , min(currenter_page_num + 3, paginator.num_pages+1))]
    #判断添加第一页和最后一页，和判断是否需要省略号
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取月份归档文章数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_dates_dict[blog_date] = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()

    context = {}
    context['blogs'] = page_of_blogs
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['page_range'] = page_range
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_date(blogs_all_list, request)
    return render_to_response('blog/blog_list.html', context)

def blog_list_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_date(blogs_all_list, request)
    context['blog_type'] = blog_type
    return render_to_response('blog/blog_list_with_type.html', context)


def blog_list_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_date(blogs_all_list, request)
    context['blog_date'] = "%s年%s月" % (year, month)
    return render_to_response('blog/blog_list_with_date.html', context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    if not request.COOKIES.get('%s_blog_read' % blog.pk):
        if ReadNum.objects.filter(blog=blog).count():
            #记录存在
            readnum = ReadNum.objects.get(blog=blog)
        else:
            #记录不存在
            readnum = ReadNum(blog=blog)
        #阅读量+1
        readnum.read_num += 1
        readnum.save()
    context = {}
    context['previours_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first() 
    context['blog'] = blog
    response = render_to_response('blog/blog_detail.html', context)
    #设置cookie来判断阅读数
    response.set_cookie('%s_blog_read' % blog.pk,'true', max_age=60, expires=datetime)
    return response
