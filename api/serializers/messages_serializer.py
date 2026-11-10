from rest_framework import serializers


class CreateChatSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(min_value=1)
    client_id = serializers.IntegerField(min_value=1)


class SendMessageSerializer(serializers.Serializer):
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=5000
    )


class ChatListQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=50)
    cursor = serializers.CharField(required=False, allow_blank=False)


class MessagesQuerySerializer(ChatListQuerySerializer):
    pass