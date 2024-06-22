"""
URL configuration for mon_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from mon_blog.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', go_to_index),
    path('avis/', go_to_avis),
    path('loisirs/', go_to_loisirs),
    path('contact/', go_to_contact),
    path('foot/', go_to_foot_posts),
    path('anime/', go_to_anime_posts),
    path('game/', go_to_game_posts),
    path('other/', go_to_other_posts),
    path('post-<int:post_id>/', go_to_post),
    path('creer-avis/', create_avis),
    path('nouveau-post/', publish),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
