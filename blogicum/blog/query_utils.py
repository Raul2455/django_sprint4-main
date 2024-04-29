from django.db.models import Count
from django.utils import timezone

from blog.models import Post

# Переименовываем функцию и файл в соответствии с рекомендациями рецензента.


def query_create_queryset(manager=Post.objects,
                          filters=True, annotations=True):
    """Creates a queryset with select_related, filtering, and annotations."""
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
