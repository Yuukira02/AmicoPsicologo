app_name = "blog"

from django.urls import path
from .views import *

urlpatterns = [
    path("read/<str:pk>", ReadPostView.as_view(), name="read"), 

    path("myblogs/", MyBlogs.as_view(), name="myblogs"),

    path("create", CreateBlogView.as_view(), name="create"), 
    path("update/<str:pk>", UpdateBlogView.as_view(), name="update"), 
    path("delete/<str:pk>", DeleteBlogView.as_view(), name="delete"),

    path("", search, name="all"),
    path("search/<str:sstring>/<str:topic>/", BlogSearchView.as_view(), name="search_results"),
   
]