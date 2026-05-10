from django.contrib.auth.models import User
from django.db.models import F
from questions.models import Tag

def sidebar_data(request):
    tags_qs = Tag.objects.order_by('-questions_count')[:8]

    css_classes = [
        'text-dark',
        'text-danger fw-bold fs-5',
        'text-success fw-bold',
        'text-warning'
    ]

    popular_tags = []
    for i, tag in enumerate(tags_qs):
        popular_tags.append({
            'name': tag.name,
            'css': css_classes[i % len(css_classes)]
        })

    best_members_qs = User.objects.select_related('profile').order_by(F('profile__answers_count').desc(nulls_last=True))[:5]

    best_members = []
    for user in best_members_qs:
        if hasattr(user, 'profile') and user.profile.nickname:
            best_members.append(user.profile.nickname)
        else:
            best_members.append(user.username)

    return {
        'popular_tags': popular_tags,
        'best_members': best_members
    }
