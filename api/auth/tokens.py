from rest_framework_simplejwt.tokens import RefreshToken as _RefreshToken


def generate_tokens(user_data: dict) -> dict:
    """
    Gera um par access/refresh token JWT com claims customizados.

    user_data esperado:
        {
            'user_type': 'client' | 'company' | 'driver',
            'user_id': int,
            'user_name': str,
        }
    """
    # simplejwt exige um objeto com pk; usamos um objeto simples
    class _FakeUser:
        pk = user_data['user_id']

    refresh = _RefreshToken.for_user(_FakeUser())

    # Claims extras no token
    for key, value in user_data.items():
        refresh[key] = value
        refresh.access_token[key] = value
    refresh.access_token['user_type'] = user_data['user_type']
    refresh.access_token['user_id'] = user_data['user_id']
    refresh.access_token['user_name'] = user_data['user_name']

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }