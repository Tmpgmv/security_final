"""
URL configuration for master_pol project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

from django.contrib.auth.decorators import login_required

from django.urls import path, include
from django.conf import settings  # PREP
from django.conf.urls.static import static  # PREP
from general.views import HtmlGeneratorView, JsonGeneratorView
from home.views import HomeView
from rest_framework import routers

from product_list.views import ProductListView

"""
    См. комментарий в general/view_mixins.py.
    Чтобы все заработало, нужно URL для CRUD делать по образцу (в части path и name).
    Пример URL для условной модели Plane:

    urlpatterns = [
        path("plane/detail/<int:pk>", PlaneDetailView.as_view(), name="plane_detail"),
        path("plane/update/<int:pk>", PlaneUpdateView.as_view(), name="plane_update"),
        path("plane/delete/<int:pk>", PlaneDeleteView.as_view(), name="plane_delete"),
        path("plane/create", PlaneCreateView.as_view(), name="plane_create"),
        path("plane/list", PlaneListView.as_view(), name="plane_list"),
    ]
    

    Используйте генератор кода http://127.0.0.1:8000/generator


"""
router = routers.DefaultRouter()

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/', include('allauth.urls')),
    path("admin/", admin.site.urls),
    #path("", include(router.urls)),
    path("", login_required(HomeView.as_view()), name="home"),
    path("products/", login_required(ProductListView.as_view()), name="products"),

]

urlpatterns += i18n_patterns(

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
