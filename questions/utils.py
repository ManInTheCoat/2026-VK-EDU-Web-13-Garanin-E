import jwt
import time
from django.conf import settings

def get_centrifugo_data(request):
    """Вспомогательный метод для генерации токена и URL Centrifugo"""
    user_id = str(request.user.id) if request.user.is_authenticated else 'anonymous'
    claims = {"sub": user_id, "exp": int(time.time()) + 24 * 60 * 60}
    token = jwt.encode(claims, settings.CENTRIFUGO_TOKEN_HMAC_SECRET_KEY, algorithm='HS256')

    return {
        'centrifugo_token': token,
        'ws_url': settings.CENTRIFUGO_WS_URL,
    }
