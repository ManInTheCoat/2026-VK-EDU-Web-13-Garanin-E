from django.core.cache import cache
from questions.tasks import update_popular_tags_cache, update_best_users_cache

def sidebar_data(request):
    cached_tags = cache.get('popular_tags')
    cached_users = cache.get('best_users')

    if cached_tags is None:
        update_popular_tags_cache()
        cached_tags = cache.get('popular_tags') or []

    if cached_users is None:
        update_best_users_cache()
        cached_users = cache.get('best_users') or []

    css_classes = [
        'text-dark',
        'text-danger fw-bold fs-5',
        'text-success fw-bold',
        'text-warning'
    ]

    popular_tags = []
    for i, tag in enumerate(cached_tags):
        popular_tags.append({
            'name': tag.name,
            'css': css_classes[i % len(css_classes)]
        })

    best_members = []
    for user in cached_users:
        if hasattr(user, 'profile') and user.profile.nickname:
            best_members.append(user.profile.nickname)
        else:
            best_members.append(user.username)

    return {
        'popular_tags': popular_tags,
        'best_members': best_members
    }
