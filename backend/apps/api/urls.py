from django.urls import path

from apps.api import views

urlpatterns = [
    path("vehicles/makes/", views.makes),
    path("vehicles/makes/<slug:make>/models/", views.models_for_make),
    path("vehicles/models/<slug:model>/generations/", views.generations_for_model),
    path("vehicles/generations/<slug:gen>/trims/", views.trims_for_generation),
    path("vehicles/generations/<slug:gen>/engines/", views.engines_for_generation),
    path("vehicles/generations/<slug:gen>/groups/", views.groups_for_generation),
    path("vehicles/resolve/", views.resolve_vehicle),
    path("page/", views.page),
    path("categories/", views.categories),
    path("shop/<slug:slug>/", views.shop_category),
    path("products/<slug:slug>/", views.product_detail),
    path("products/<slug:slug>/fits/", views.product_fits),
    path("search/", views.search),
    path("seo/changed/", views.seo_changed),
]
