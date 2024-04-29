from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone  # Добавляем импорт timezone

from .forms import CommentEditForm, PostEditForm, UserEditForm
from .mixins import CommonPostMixin, CommentMixin
from .models import Category, Post, User
from .query_utils import create_queryset


class IndexListView(ListView):
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = settings.MAX_POST_ON_PAGE

    def get_queryset(self):
        return create_queryset()


class CategoryListView(IndexListView):
    template_name = 'blog/category.html'

    def get_category(self):
        category_slug = self.kwargs.get('category_slug')
        return get_object_or_404(Category,
                                 slug=category_slug, is_published=True)

    def get_queryset(self):
        category = self.get_category()
        return create_queryset(manager=category.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class ProfileListView(IndexListView):
    template_name = 'blog/profile.html'

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        author = self.get_author()
        filters = True if self.request.user != author else False
        return create_queryset(manager=author.posts, filters=filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentEditForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'
    paginate_by = settings.MAX_POST_ON_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentEditForm(instance=self.object)
        context['comments'] = (
            self.object.comments.all().select_related('author')
        )
        return context

    def get_queryset(self):
        # Используем get_queryset родительского класса
        return super().get_queryset()

    def get_object(self, queryset=None):
        # Получаем объект поста используя queryset из get_queryset
        post = super().get_object(queryset=self.get_queryset())

        # Проверяем условия видимости поста
        if (
            post.author != self.request.user
            and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()
            )
        ):  # Добавляем закрывающую скобку
            raise Http404()

        return post


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(CommonPostMixin, LoginRequiredMixin, UpdateView):
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(CommonPostMixin, LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostEditForm(instance=self.object)
        return context


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass


class ProfileCreateView(CreateView):
    form_class = UserEditForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
