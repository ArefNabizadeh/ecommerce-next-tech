from django.contrib.auth import get_user_model

User = get_user_model()


def user_context(request):
    return {'user': request.user,
            'is_authenticated': request.user.is_authenticated, }
