from api.webservices.firebase.firebase import get_firestore_client
from firebase_admin import firestore


class ChatNotFoundError(LookupError):
    pass


class ChatAccessError(PermissionError):
    pass


class ChatValidationError(ValueError):
    pass


def _chat_data(snapshot):
    data = snapshot.to_dict() or {}
    return {**data, "id": snapshot.id}


def _require_participant(chat_data, user_uid):
    if user_uid not in (chat_data.get("companyId"), chat_data.get("clientId")):
        raise ChatAccessError("O usuário não participa desta conversa.")


def create_chat(company_id, client_id, requester_uid):
    company_uid = f"company_{company_id}"
    client_uid = f"client_{client_id}"
    if requester_uid not in (company_uid, client_uid):
        raise ChatAccessError("O usuário não participa desta conversa.")

    db = get_firestore_client()
    chat_id = f"company_{company_id}_client_{client_id}"
    chat_ref = db.collection("chats").document(chat_id)
    transaction = db.transaction()

    @firestore.transactional
    def create_if_not_exists(transaction):
        chat = chat_ref.get(transaction=transaction)
        if chat.exists:
            data = chat.to_dict() or {}
            if data.get("companyId") != company_uid or data.get("clientId") != client_uid:
                raise ChatAccessError("Os participantes da conversa são inválidos.")
            return

        transaction.set(chat_ref, {
            "companyId": company_uid,
            "clientId": client_uid,
            "lastMessage": "",
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })

    create_if_not_exists(transaction)
    return get_chat(chat_id, requester_uid)


def get_chat(chat_id, user_uid):
    snapshot = get_firestore_client().collection("chats").document(chat_id).get()
    if not snapshot.exists:
        raise ChatNotFoundError("Conversa não encontrada.")

    data = _chat_data(snapshot)
    _require_participant(data, user_uid)
    return data


def list_chats(user_uid, user_type, limit=50, cursor=None):
    field = {"client": "clientId", "company": "companyId"}.get(user_type)
    if not field:
        raise ChatAccessError("Tipo de usuário não autorizado.")

    chats = get_firestore_client().collection("chats")
    query = chats.where(field, "==", user_uid).order_by(
        "updatedAt", direction=firestore.Query.DESCENDING
    )
    if cursor:
        cursor_snapshot = chats.document(cursor).get()
        if not cursor_snapshot.exists or (cursor_snapshot.to_dict() or {}).get(field) != user_uid:
            raise ChatValidationError("Cursor de conversa inválido.")
        query = query.start_after(cursor_snapshot)

    snapshots = list(query.limit(limit + 1).stream())
    has_more = len(snapshots) > limit
    page = snapshots[:limit]
    return {
        "items": [_chat_data(snapshot) for snapshot in page],
        "nextCursor": page[-1].id if has_more and page else None,
    }


def get_messages(chat_id, user_uid, limit=50, cursor=None):
    get_chat(chat_id, user_uid)
    messages = get_firestore_client().collection("chats").document(chat_id).collection("messages")
    query = messages.order_by("createdAt", direction=firestore.Query.DESCENDING)
    if cursor:
        cursor_snapshot = messages.document(cursor).get()
        if not cursor_snapshot.exists:
            raise ChatValidationError("Cursor de mensagem inválido.")
        query = query.start_after(cursor_snapshot)

    snapshots = list(query.limit(limit + 1).stream())
    has_more = len(snapshots) > limit
    page = snapshots[:limit]
    next_cursor = page[-1].id if has_more and page else None
    page.reverse()
    return {
        "items": [{"id": snapshot.id, **(snapshot.to_dict() or {})} for snapshot in page],
        "nextCursor": next_cursor,
    }


def mark_messages_read(chat_id, user_uid):
    get_chat(chat_id, user_uid)
    db = get_firestore_client()
    messages = db.collection("chats").document(chat_id).collection("messages")
    batch = db.batch()
    updated = 0

    for snapshot in messages.where("readAt", "==", None).stream():
        data = snapshot.to_dict() or {}
        if data.get("senderId") == user_uid:
            continue
        batch.update(snapshot.reference, {"readAt": firestore.SERVER_TIMESTAMP})
        updated += 1
        if updated % 450 == 0:
            batch.commit()
            batch = db.batch()

    if updated % 450:
        batch.commit()
    return {"chatId": chat_id, "updatedCount": updated}