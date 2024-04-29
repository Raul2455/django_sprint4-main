from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from blog.models import Post, Comment
from blog.forms import CommentEditForm, PostEditForm


class CommonPostMixin:
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    form_class = PostEditForm

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get(self.pk_url_kwarg))
        if post.author != request.user:
            return redirect('blog:post_detail',
                            post_id=kwargs.get(self.pk_url_kwarg))
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(
            Comment,
            pk=kwargs.get('comment_id'),
            post__id=kwargs.get('post_id')
        )
        if self.comment.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )
