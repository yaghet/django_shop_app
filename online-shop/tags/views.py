from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from tags.models import Tag
from tags.serializers import TagSerializer


class TagListView(APIView):
    def get(self, request: Request) -> Response:
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
