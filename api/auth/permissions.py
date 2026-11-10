from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def get_payload(request) -> dict | None:
    """Lê o payload JWT sem exigir User do Django."""
    auth = JWTAuthentication()
    try:
        header = auth.get_header(request)
        if header is None:
            return None
        raw_token = auth.get_raw_token(header)
        validated  = auth.get_validated_token(raw_token)
        return validated.payload
    except (InvalidToken, TokenError):
        return None


class ChatPermission(BasePermission):
    message = 'Você não tem permissão para acessar esta conversa.'

    def has_permission(self, request, view):
        payload = get_payload(request)

        if not payload:
            return False

        return payload.get('user_type') in (
            'client',
            'company',
            'admin'
        )

    def has_object_permission(self, request, view, obj):
        payload = get_payload(request) or {}

        user_type = payload.get('user_type')
        user_id = payload.get('user_id')

        if user_type == 'admin':
            return True

        if user_type == 'client':
            return str(obj.get('clientId')) == f'client_{user_id}'

        if user_type == 'company':
            return str(obj.get('companyId')) == f'company_{user_id}'

        return False

class IsAuthenticatedCustom(BasePermission):
    message = 'Autenticação necessária.'

    def has_permission(self, request, view):
        payload = get_payload(request)
        return payload is not None and 'user_type' in payload


# ── Regras de acesso por recurso ──────────────────────────────────────────────
#
#   Client  → lê Company e Driver  |  edita só si mesmo
#   Company → lê Client e Driver   |  edita só si mesma
#   Driver  → lê Client e Company  |  edita só si mesmo
#   Admin   → tudo
#
WRITE_ACTIONS = {'update', 'partial_update', 'destroy'}


class ClientViewPermission(BasePermission):
    message = 'Você não tem permissão para acessar dados de clientes.'

    def has_permission(self, request, view):
        payload = get_payload(request)
        if not payload:
            return False
        user_type = payload.get('user_type')
        action    = getattr(view, 'action', None)
        if user_type == 'admin':
            return True
        if action in WRITE_ACTIONS:
            return user_type == 'client'
        return user_type in ('client', 'company', 'driver')

    def has_object_permission(self, request, view, obj):
        payload   = get_payload(request)
        user_type = payload.get('user_type')
        user_id   = payload.get('user_id')
        action    = getattr(view, 'action', None)
        if user_type == 'admin':
            return True
        if action in WRITE_ACTIONS:
            return user_type == 'client' and obj.id == user_id
        if user_type == 'client':
            return obj.id == user_id
        return user_type in ('company', 'driver')


class CompanyViewPermission(BasePermission):
    message = 'Você não tem permissão para acessar dados de empresas.'

    def has_permission(self, request, view):
        payload = get_payload(request)
        if not payload:
            return False
        user_type = payload.get('user_type')
        action    = getattr(view, 'action', None)
        if user_type == 'admin':
            return True
        if action in WRITE_ACTIONS:
            return user_type == 'company'
        return user_type in ('client', 'company', 'driver')

    def has_object_permission(self, request, view, obj):
        payload   = get_payload(request)
        user_type = payload.get('user_type')
        user_id   = payload.get('user_id')
        action    = getattr(view, 'action', None)
        if user_type == 'admin':
            return True
        if action in WRITE_ACTIONS:
            return user_type == 'company' and obj.id == user_id
        if user_type == 'company':
            return obj.id == user_id
        return user_type in ('client', 'driver')


class DriverViewPermission(BasePermission):
    message = 'Você não tem permissão para acessar dados de motoristas.'

    def has_permission(self, request, view):
        payload = get_payload(request)
        if not payload:
            return False
        user_type = payload.get('user_type')
        action    = getattr(view, 'action', None)
        if user_type == 'admin':
            return True
        if action in WRITE_ACTIONS:
            return user_type == 'driver'
        return user_type in ('client', 'company', 'driver')

    def has_object_permission(self, request, view, obj):
        payload   = get_payload(request)
        user_type = payload.get('user_type')
        user_id   = payload.get('user_id')
        action    = getattr(view, 'action', None)
        if user_type == 'admin':
            return True
        if action in WRITE_ACTIONS:
            return user_type == 'driver' and obj.id == user_id
        if user_type == 'driver':
            return obj.id == user_id
        return user_type in ('client', 'company')


class AccountResourcePermission(BasePermission):
    """Authenticated profile access; writes are limited to the matching account."""
    def has_permission(self, request, view):
        payload = get_payload(request)
        if not payload:
            return False
        return request.method in ('GET', 'HEAD', 'OPTIONS') or payload.get('user_type') in (
            getattr(view, 'account_role', None), 'admin'
        )

    def has_object_permission(self, request, view, obj):
        payload = get_payload(request) or {}
        if payload.get('user_type') == 'admin':
            return True
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return payload.get('user_type') == view.account_role and obj.pk == payload.get('user_id')


class TokenUserPermission(BasePermission):
    """Require one of the custom JWT account types for non-account resources."""
    def has_permission(self, request, view):
        payload = get_payload(request)
        if not payload or payload.get('user_type') not in ('client', 'company', 'driver', 'admin'):
            return False
        return not hasattr(view, 'can_perform_action') or view.can_perform_action(request, payload)

    def has_object_permission(self, request, view, obj):
        payload = get_payload(request) or {}
        return view.user_can_access_object(request, obj, payload)
