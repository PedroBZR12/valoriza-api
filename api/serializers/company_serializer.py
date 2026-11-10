from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models import Company


class CompanySerializer(serializers.ModelSerializer):
    company_email = serializers.EmailField(max_length=127)
    company_password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Company
        fields = ("id", "company_name", "company_adress", "company_cnpj", "company_email",
                  "company_password", "company_account_created_at")
        read_only_fields = ("id", "company_account_created_at")

    def create(self, validated_data):
        password = validated_data.pop("company_password")
        return Company.objects.create(company_password_hash=make_password(password), **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("company_password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.company_password_hash = make_password(password)
        instance.save()
        return instance


class CreateCompanySerializer(CompanySerializer):
    company_password = serializers.CharField(write_only=True, required=True, allow_blank=False)
