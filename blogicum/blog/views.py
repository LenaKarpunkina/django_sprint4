from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post
from .utils import paginate_queryset


def index(request):
    post_list = (
        Post.objects.with_comments_count()
        .published()
        .select_related('location', 'category', 'author')
        .order_by('-pub_date')
    )
    page_obj = paginate_queryset(request, post_list)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    post_list = (
        Post.objects.with_comments_count()
        .published()
        .filter(category=category)
        .select_related('location', 'author')
        .order_by('-pub_date')
    )
    page_obj = paginate_queryset(request, post_list)
    return render(request, 'blog/category.html', {'category': category, 'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if post.author != request.user:
        category_is_published = post.category and post.category.is_published
        
        if not (post.is_published and 
                category_is_published and 
                post.pub_date <= timezone.now()):
            raise Http404
      
    form = CommentForm()
    comments = post.comments.select_related('author').order_by('created_at')
    
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts_query = (
        Post.objects.with_comments_count()
        .filter(author=profile_user)
        .order_by('-pub_date')
    )
    
    if request.user != profile_user:
        posts_query = posts_query.published()
    
    page_obj = paginate_queryset(request, posts_query)
    context = {'profile': profile_user, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    form = PostForm(request.POST or None, files=request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


@login_required
def delete_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    
    return render(request, 'blog/delete_post.html', {'post': instance})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    form = CommentForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    
    return render(request, 'blog/comment.html', {'form': form, 'comment': instance})


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)
    
    return render(request, 'blog/comment.html', {'comment': instance})