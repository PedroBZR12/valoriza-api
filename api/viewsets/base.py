from rest_framework import viewsets


class ApiModelViewSet(viewsets.ModelViewSet):
    """Use a consistent data envelope for successful single-resource responses."""
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if (response.status_code < 400 and response.data is not None and
                self.action in {"retrieve", "create", "update", "partial_update"} and
                not (isinstance(response.data, dict) and "data" in response.data)):
            response.data = {"data": response.data}
        return response
