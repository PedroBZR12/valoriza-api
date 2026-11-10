from api.auth.permissions import AccountResourcePermission
from api.models import Company
from api.serializers.company_serializer import CompanySerializer, CreateCompanySerializer
from api.viewsets.base import ApiModelViewSet


class CompanyViewSet(ApiModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = (AccountResourcePermission,)
    account_role = "company"

    def get_queryset(self):
        payload = self.request.auth.payload if self.request.auth else {}
        if payload.get("user_type") == "admin":
            return Company.objects.all().order_by("id")
        return Company.objects.filter(pk=payload.get("user_id"))

    def get_serializer_class(self):
        return CreateCompanySerializer if self.action == "create" else CompanySerializer
