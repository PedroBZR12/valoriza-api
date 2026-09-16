from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models.company import Company


class ListCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id',
            'company_name',
            'company_adress',
            'company_cnpj',
            'company_email',
            'company_account_created_at',
        )
        read_only_fields = (
            'id',
            'company_account_created_at',
        )


class CompanySerializer(serializers.ModelSerializer):
    company_password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Company
        fields = (
            'id',
            'company_name',
            'company_adress',
            'company_cnpj',
            'company_email',
            'company_password',
            'company_account_created_at',
        )
        read_only_fields = (
            'id',
            'company_account_created_at',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('company_password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.company_password_hash = make_password(password)

        instance.save()

        return instance


class CreateCompanySerializer(serializers.ModelSerializer):
    company_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Company
        fields = (
            'id',
            'company_name',
            'company_adress',
            'company_cnpj',
            'company_email',
            'company_password',
            'company_account_created_at',
        )
        read_only_fields = (
            'id',
            'company_account_created_at',
        )

    def create(self, validated_data):
        password = validated_data.pop('companyPassword')

        validated_data['company_password_hash'] = make_password(password)

        return Company.objects.create(**validated_data)
