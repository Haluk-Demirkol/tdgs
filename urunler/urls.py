from django.urls import path
from . import views

urlpatterns = [
    path('', views.urun_listesi, name='urun_listesi'),
    path('urun/<int:id>/', views.urun_detay, name='urundetay'),
    path('urunler/', views.urun_listesi, name='urunler'),
    path('teklif-basarili/', views.teklif_basarili, name='teklif_basarili'),
    path("odeme/<int:cevap_id>/", views.odeme_sayfasi, name="odeme_sayfasi"),
    path("odeme-sonuc/", views.odeme_sonuc, name="odeme_sonuc"),


]


