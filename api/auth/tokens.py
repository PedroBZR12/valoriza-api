from rest_framework_simplejwt.tokens import RefreshToken


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
    refresh = RefreshToken()

    refresh['user_id'] = user_data['user_id']
    refresh['user_type'] = user_data['user_type']
    refresh['user_name'] = user_data['user_name']

    access = refresh.access_token

    access['user_id'] = user_data['user_id']
    access['user_type'] = user_data['user_type']
    access['user_name'] = user_data['user_name']

    return {
        'access': str(access),
        'refresh': str(refresh),
    }