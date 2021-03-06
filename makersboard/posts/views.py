from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from picklable_itertools import chain
from urllib.parse import quote_plus

from .forms import PostForm
from .models import Post
from users.models import UserProfile


def post_create(request):  # CRUD: Create
    if request.user.is_authenticated():
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, 'Successfully created post.')
            return HttpResponseRedirect(instance.get_absolute_url())
        context = {
            'form': form,
        }
        return render(request, 'post_form.html', context)
    else:
        messages.warning(request, 'You need to be logged in.')


def post_update(request, slug=None):  # CRUD: Update
    instance = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated():
        is_owner = Post.objects.filter(slug=slug).\
            filter(user=request.user)
        if is_owner:
            form = PostForm(request.POST or None,
                            request.FILES or None,
                            instance=instance)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'Post updated.')
                return HttpResponseRedirect(instance.get_absolute_url())
            context = {
                'form': form,
            }
            return render(request, 'post_form.html', context)
        else:
            messages.warning(request, 'You cannot edit another user.')
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.warning(request, 'You need to be logged in to edit.')
        return HttpResponseRedirect(instance.get_absolute_url())


def post_detail(request, slug=None):  # CRUD: Retrieve
    instance = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated():
        is_owner = Post.objects.filter(slug=slug).\
            filter(user=request.user)
        owner = request.user
    else:
        is_owner = False
    share_string = quote_plus(instance.description)
    context = {
        'title': instance.title,
        'instance': instance,
        'share_string': share_string,
        'is_owner': is_owner,
        'owner': owner,
        'is_authenticated': request.user.is_authenticated(),
    }
    return render(request, 'post_detail.html', context)


def post_list(request):  # CRUD: Retrieve
    queryset_list = Post.objects.all()  # .order_by('-timestamp')
    paginator = Paginator(queryset_list, 10)  # Show 10 contacts per page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
        'object_list': queryset,
        'title': 'Maker\'s Board',
    }
    return render(request, 'post_list.html', context)


def post_delete(request, slug=None):  # CRUD: Delete
    instance = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated():
        is_owner = Post.objects.filter(slug=slug).\
            filter(user=request.user)
        if is_owner:
            instance.delete()
            messages.success(request, 'Successfully deleted post.')
            return redirect('posts:list')
        else:
            messages.error(request, 'You cannot delete a post you don\'t own.')
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.error(request, 'You have to be logged in to delete a post.')
        return HttpResponseRedirect(instance.get_absolute_url())


def search(request):
    '''
    queries = request.GET['q'].split()
    queryset_list = Post.objects.all()  # .order_by('-timestamp')
    queryset_list.extend(UserProfile.objects.all())
    for query in queries:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__full_name__icontains=query)
        )
    '''
    queries = request.GET['q'].split()
    results = []
    for query in queries:
        user_results = (UserProfile.objects.filter(
            Q(username__icontains=query) |
            Q(bio__icontains=query) |
            Q(full_name__icontains=query) |
            Q(location__icontains=query)))
        post_results = (Post.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(medium__icontains=query)))
        results = list(chain(results, user_results, post_results))
    paginator = Paginator(results, 10)  # Show 10 contacts per page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = {
        'object_list': queryset,
        'title': 'Search Results',
        'query': query,

    }
    return render(request, 'search_results.html', context)


def post_warning(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    context = {
        'title': instance.title,
        'instance': instance,
    }
    return render(request, 'post_warning.html', context)
