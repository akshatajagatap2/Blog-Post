from django.db import models
import uuid

from blogpost_management.models.common_model import CommonFields
from user_management.models.users_model import Users


class BlogPostModel(CommonFields):
    """
    This table stores detailed user assessment information
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True,
                          help_text="Unique identifier for the blog post.")
    author = models.ForeignKey(to=Users, on_delete=models.CASCADE, related_name='author',
                               help_text="User who authored the blog post.")

    title = models.CharField(max_length=255, null=True, blank=True, help_text="Title of the blog post.")
    body = models.TextField(null=True, blank=True, help_text="Main content of the blog post.")

    description = models.CharField(max_length=255, null=True, blank=True,
                                   help_text="Short summary or description of the blog post.")
    category = models.CharField(max_length=100, null=True, blank=True,
                                help_text="Category or tag to classify the blog post (e.g., Tech, Lifestyle, News).")

    class Meta:
        db_table = 'blogpost_table'
        app_label = 'blogpost_management'
