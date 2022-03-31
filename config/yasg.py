
from django.urls import URLPattern, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
      title="EBSHOP",
      default_version='v1',
      description="Test description",
      license=openapi.License(name="EBS License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpattern = [
   path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]