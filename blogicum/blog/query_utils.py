from django.db.models import Count
from django.utils import timezone

# Пустая строка между группами импортов
from blog.models import Post


def create_queryset(manager=Post.objects, filters=True, annotations=True):
    """Создает набор запросов с select_related, фильтрацией и аннотациями."""
    queryset = manager.select_related(
        'author',
        'location',
        'category'
    )
    if filters:
        queryset = queryset.filter(
            pub_date__lt=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    if annotations:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return queryset
