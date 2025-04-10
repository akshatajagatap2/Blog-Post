import pytz
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response
from datetime import datetime
from blogpost_management.api_exception import StandardizedException
from blogpost_management.filters.blogpost_filter import BlogPostFilter
from blogpost_management.models import BlogPostModel
from blogpost_management.models.domain_model import Status
from blogpost_management.pagination import CommonPagination
from blogpost_management.serializers.blogpost_serializer import BlogPostSerializer
from utils.decorators import trace_log
from utils.logger import service_logger
from utils.permission import IsAuthenticatedWithSimpleToken


class BlogPostViewSet(NestedViewSetMixin, ModelViewSet):
    model = BlogPostModel
    permission_classes = [IsAuthenticatedWithSimpleToken]
    serializer_class = BlogPostSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend, SearchFilter)
    filterset_class = BlogPostFilter
    pagination_class = CommonPagination
    ordering_fields = '__all__'
    ordering = 'created_at'
    http_method_names = ['post', 'put', 'patch', 'delete', 'get']
    search_fields = ['user__firstname', 'user__lastname', 'user__email']

    def __init__(self, *args, **kwargs):
        super(BlogPostViewSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        self.queryset = BlogPostModel.objects.get_api_queryset()
        return self.queryset

    @trace_log
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"success":True,"message":"Blog Post Created Successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            service_logger.error(str(e))
            raise StandardizedException(error_status=True, error_obj=e, status_code=status.HTTP_400_BAD_REQUEST)

    @trace_log
    def update(self, request, *args, **kwargs):
        try:
            kwargs['partial'] = False
            obj = self.get_object()
            serializer = self.serializer_class(obj, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data = self.serializer_class(obj).data
            return Response({"Success":True,"message":"Blog Post Updated Successfully",
                             "data":response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            service_logger.error(str(e))
            raise StandardizedException(error_status=True,
                                        error_obj=e,
                                        status_code=status.HTTP_400_BAD_REQUEST)

    @trace_log
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = BlogPostSerializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)
        except Exception as e:
            service_logger.error(str(e))
            raise StandardizedException(error_status=True, error_obj=e, status_code=status.HTTP_400_BAD_REQUEST)

    @trace_log
    def retrieve(self, request, *args, **kwargs):
        try:
            data = BlogPostSerializer(self.get_object()).data
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            service_logger.error(str(e))
            raise StandardizedException(error_status=True, error_obj=e, status_code=status.HTTP_400_BAD_REQUEST)

    @trace_log
    def destroy(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            obj.status_id = Status.deleted()
            obj.deleted_at = datetime.now(pytz.utc)
            obj.save()

            return Response('BlogPost deleted successfully', status=status.HTTP_200_OK)
        except Exception as e:
            service_logger.error(str(e))
            raise StandardizedException(error_status=True, error_obj=e, status_code=status.HTTP_400_BAD_REQUEST)
