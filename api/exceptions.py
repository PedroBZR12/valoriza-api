from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None
    status_code = response.status_code
    if isinstance(exc, ValidationError):
        response.status_code = 422
        code, message = "INVALID_DATA", "Existem campos inválidos."
    elif status_code == 400:
        code, message = "INVALID_DATA", "Existem campos inválidos."
    elif status_code == 401:
        code, message = "UNAUTHORIZED", "Autenticação necessária."
    elif status_code == 403:
        code, message = "FORBIDDEN", "Você não tem permissão para esta operação."
    elif status_code == 404:
        code, message = "NOT_FOUND", "Recurso não encontrado."
    elif status_code == 409:
        code, message = "RESOURCE_CONFLICT", "Conflito com o estado atual do recurso."
    else:
        code, message = "REQUEST_ERROR", "Não foi possível processar a requisição."
    fields = response.data
    response.data = {"error": {"code": code, "message": message, "fields": fields}}
    return response
