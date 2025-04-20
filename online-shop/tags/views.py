from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from tags.models import Tag
from tags.serializers import TagSerializer


class TagListView(APIView):
    permission_classes = (AllowAny,)
    @extend_schema(
        responses=TagSerializer,
        description="Список тегов для продукта (товаров)",
    )
    def get(self, request: Request) -> Response:
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
