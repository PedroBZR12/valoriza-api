INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
    'apps',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}