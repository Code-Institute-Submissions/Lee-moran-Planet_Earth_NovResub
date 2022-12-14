from . import views
from django.urls import path, include


urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('like/<slug:slug>/', views.PostLike.as_view(), name='post_like'),
    path('all_post', views.AllPosts.as_view(), name='all_post'),
    path('add_blogs/', views.AddBlogs.as_view(), name='add_blogs'),
    path('your_blogs/', views.YourBlogs.as_view(), name='your_blogs'),
    path('<slug:slug>/', views.PostDetails.as_view(), name='post_detail'),
    path('delete_blogs/<int:post_id>/', views.delete_blogs, name='delete_blogs'),
    path('editblog/<int:pk>', views.EditBlog.as_view(), name='editblog'),
    path('search_blog', views.search_blog, name='search_blog'),
]