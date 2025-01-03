from django.conf import settings

from django.contrib import admin
from django.urls import path
from bloomer import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.feed, name='feed'),
    path('feed', views.feed, name='feed'),
    path('map', views.map, name='map'),
    path('prof', views.prof, name='prof'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name='user_login'),
    path('postpage', views.postpage, name='postpage'),
    path('upload', views.upload_post, name='upload_post'),
    path('upload1', views.upload_profile, name='upload_profile'),
    path('user_posts/<str:username>/', views.user_posts, name='user_posts'),
    path('follow_us/<str:username>/', views.follow_user, name='follow_user'),
    path('following_list/<str:username>/', views.following_list, name='following_list'),
    path('followers_list/<str:username>/', views.followers_list, name='followers_list'),
    path('update_steps/', views.update_steps, name='update_steps'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)