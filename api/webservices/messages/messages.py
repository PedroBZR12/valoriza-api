from api.webservices.chat_service.chat_service import ChatAccessError, ChatNotFoundError
from api.webservices.firebase.firebase import get_firestore_client
from firebase_admin import firestore


def send_message(chat_id, sender_uid, text):
    if not isinstance(text, str):
        raise ValueError("A mensagem deve ser um texto.")

    db = get_firestore_client()

    # Validação básica do conteúdo
    text = text.strip()

    if not text:
        raise ValueError("A mensagem não pode estar vazia.")

    chat_ref = db.collection("chats").document(chat_id)

    # Gera um ID automático para a mensagem
    message_ref = chat_ref.collection("messages").document()

    transaction = db.transaction()

    @firestore.transactional
    def create_message(transaction):

        chat = chat_ref.get(transaction=transaction)

        if not chat.exists:
            raise ChatNotFoundError("Conversa não encontrada.")

        chat_data = chat.to_dict()

        # Verifica se o remetente participa da conversa
        if sender_uid not in (
            chat_data.get("companyId"),
            chat_data.get("clientId")
        ):
            raise ChatAccessError(
                "O usuário não participa desta conversa."
            )

        # Registra a mensagem
        transaction.set(message_ref, {
            "senderId": sender_uid,
            "text": text,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "readAt": None,
        })

        # Atualiza os dados da conversa
        transaction.update(chat_ref, {
            "lastMessage": text,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })

        return message_ref.id

    message_id = create_message(transaction)
    message_snapshot = message_ref.get()
    message_data = message_snapshot.to_dict() or {}

    return {
        "id": message_id,
        "chatId": chat_id,
        "senderId": sender_uid,
        "text": text,
        "createdAt": message_data.get("createdAt"),
        "readAt": message_data.get("readAt"),
    }
