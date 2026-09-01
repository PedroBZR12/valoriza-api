import re
from django.contrib.auth.hashers import check_password
from api.models.client import Client
from api.models.company import Company
from api.models.deliverydriver import Driver


def _only_digits(value: str) -> str:
    return re.sub(r'\D', '', value or '')


def _is_email(value: str) -> bool:
    return '@' in value


def authenticate_user(identifier: str, password: str) -> dict | None:
    """
    Tenta autenticar nos 3 modelos (Client, Company, Driver).
    Aceita email, CPF (11 dígitos) ou CNPJ (14 dígitos).

    Retorna:
        {'user_type': 'client'|'company'|'driver', 'user_id': int, 'user_name': str}
    ou None se não encontrado / senha errada.
    """
    identifier = identifier.strip()
    digits     = _only_digits(identifier)
    by_email   = _is_email(identifier)

    # ── Client ───────────────────────────────────────────────────────────────
    client = None
    if by_email:
        client = Client.objects.filter(clientEmail__iexact=identifier).first()
    elif len(digits) == 11:
        client = Client.objects.filter(clientCPF=digits).first()

    if client and check_password(password, client.clientPasswordHash):
        return {'user_type': 'client', 'user_id': client.id, 'user_name': client.clientName}

    # ── Company ───────────────────────────────────────────────────────────────
    company = None
    if by_email:
        company = Company.objects.filter(companyEmail__iexact=identifier).first()
    elif len(digits) == 14:
        company = Company.objects.filter(companyCNPJ=digits).first()

    if company and check_password(password, company.companyPasswordHash):
        return {'user_type': 'company', 'user_id': company.id, 'user_name': company.companyName}

    # ── Driver ────────────────────────────────────────────────────────────────
    driver = None
    if by_email:
        driver = Driver.objects.filter(driverEmail__iexact=identifier).first()
    elif len(digits) == 11:
        driver = Driver.objects.filter(driverCPF=digits).first()

    if driver and check_password(password, driver.driverPasswordHash):
        return {'user_type': 'driver', 'user_id': driver.id, 'user_name': driver.driverName}

    return None