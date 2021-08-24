from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from main import services
from main.paginations import CustomPagination
from main.permissions import IsAuthorPermission
from main.serializers import *


class LikedMixin:
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        obj = self.get_object()
        services.add_like(obj, request.user)
        return Response()

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        obj = self.get_object()
        services.remove_like(obj, request.user)
        return Response()

    @action(detail=True, methods=['get'])
    def get_users(self, request, pk=None):
        obj = self.get_object()
        users = services.get_users(obj)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class PermissionMixin:
    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission, ]
        else:
            permissions = []
        return [permission() for permission in permissions]


class VacancyViewSet(LikedMixin, PermissionMixin, ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['company_name']
    search_fields = ['position']
    pagination_class = CustomPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    @action(detail=False, methods=['get'])
    def liked(self, request, pk=None):
        likeList = Like.objects.filter(user=request.user)
        list_ = [VacancyImage.objects.get(id=like.object_id) for like in likeList]
        serializer = VacancySerializer(list_, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def added(self, request, pk=None):
        queryset = Vacancy.objects.filter(author=request.user)
        serializers = VacancySerializer(queryset, many=True)
        return Response(serializers.data, status.HTTP_200_OK)


class CommentViewSet(PermissionMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context


class AddStarRatingView(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.order_by('author')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission]
        elif self.action in ['create']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAdminUser]
        return [permission() for permission in permissions]
