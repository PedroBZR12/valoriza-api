from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models.company import Company


class ListCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id',
            'companyName',
            'companyAdress',
            'companyCNPJ',
            'companyEmail',
            'companyAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'companyAccountCreatedAt',
        )


class CompanySerializer(serializers.ModelSerializer):
    companyPassword = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Company
        fields = (
            'id',
            'companyName',
            'companyAdress',
            'companyCNPJ',
            'companyEmail',
            'companyPassword',
            'companyAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'companyAccountCreatedAt',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('companyPassword', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.companyPasswordHash = make_password(password)

        instance.save()

        return instance


class CreateCompanySerializer(serializers.ModelSerializer):
    companyPassword = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Company
        fields = (
            'id',
            'companyName',
            'companyAdress',
            'companyCNPJ',
            'companyEmail',
            'companyPassword',
            'companyAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'companyAccountCreatedAt',
        )

    def create(self, validated_data):
        password = validated_data.pop('companyPassword')

        validated_data['companyPasswordHash'] = make_password(password)

        return Company.objects.create(**validated_data)