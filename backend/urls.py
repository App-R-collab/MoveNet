from django.urls import path, include
from . import urls_auth


from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(urls_auth)),

]
