from django.template.response import TemplateResponse
from apps.core.constants import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def custom_400(request, exception):
    return TemplateResponse(request, "errors/400.html", status=HTTP_400_BAD_REQUEST)


def custom_403(request, exception):
    return TemplateResponse(request, "errors/403.html", status=HTTP_403_FORBIDDEN)


def custom_404(request, exception):
    return TemplateResponse(request, "errors/404.html", status=HTTP_404_NOT_FOUND)


def custom_500(request):
    return TemplateResponse(
        request, "errors/500.html", status=HTTP_500_INTERNAL_SERVER_ERROR
    )
