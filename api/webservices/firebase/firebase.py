import firebase_admin
import os
from threading import Lock

from django.conf import settings
from firebase_admin import credentials, firestore, auth

_app_lock = Lock()


class FirebaseConfigurationError(RuntimeError):
    pass


def get_firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    with _app_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            credential_path = getattr(settings, 'FIREBASE_CREDENTIALS', None)
            if not credential_path or not os.path.isfile(credential_path):
                raise FirebaseConfigurationError(
                    'Configure FIREBASE_CREDENTIALS with a valid service account file.'
                )
            credential = credentials.Certificate(credential_path)
            return firebase_admin.initialize_app(credential)


def get_firestore_client():
    return firestore.client(app=get_firebase_app())


def generate_firebase_token(user_id, user_type):
    uid = f'{user_type}_{user_id}'
    token = auth.create_custom_token(uid, app=get_firebase_app())

    return token.decode('utf-8') if isinstance(token, bytes) else token