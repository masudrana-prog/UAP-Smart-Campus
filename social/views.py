from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm

@login_required
def post_list(request):
    posts = Post.objects.filter(is_approved=True).select_related('posted_by').prefetch_related('comments', 'likes')
    return render(request, 'social/post_list.html', {'posts': posts})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_approved=True)
    comments = post.comments.select_related('user').all()
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.user = request.user
            c.save()
            messages.success(request, 'Comment added!')
            return redirect('post_detail', pk=pk)
    user_liked = post.likes.filter(user=request.user).exists()
    return render(request, 'social/post_detail.html', {
        'post': post, 'comments': comments, 'form': form, 'user_liked': user_liked
    })

@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.posted_by = request.user
        post.is_approved = True
        post.save()
        messages.success(request, 'Post published!')
        return redirect('post_list')
    return render(request, 'social/create_post.html', {'form': form})

@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # STRICT: only the post owner OR admin can delete
    if post.posted_by != request.user and not request.user.is_admin_role():
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('post_list')
    return render(request, 'social/confirm_delete.html', {'object': post, 'type': 'post'})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    # STRICT: only the comment owner OR admin can delete
    if comment.user != request.user and not request.user.is_admin_role():
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('post_detail', pk=post_pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted.')
    return redirect('post_detail', pk=post_pk)
