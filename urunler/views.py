import uuid
import json
import iyzipay

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Urun
from .models import Teklif



def urun_listesi(request):
    urunler = Urun.objects.all()
    #print(f"Toplam ürün: {urunler.count()}")
    return render(request, 'urunler/urun_listesi.html', {'urunler': urunler})

def urun_detay(request, id):
    urun = get_object_or_404(Urun, id=id)
    if request.method == "POST":
        urun_id = request.POST.get("urun_id")
        ad = request.POST.get("ad")
        soyad = request.POST.get("soyad")
      
        tc = request.POST.get('tc_kimlik_no')
        telefon = request.POST.get('cep_telefonu')
        eposta = request.POST.get('eposta')
        belge = request.FILES.get('belge')

        try:
            Teklif.objects.create(
                urun=urun,
                ad=ad,
                soyad=soyad,                
                tc_kimlik_no=tc,
                cep_telefonu=telefon,
                eposta=eposta,
                belge=belge
            )
            return redirect('teklif_basarili')
        except Exception as e:
            print("Hata oluştu:", e)
            messages.error(request, "Teklif iletilemedi. Lütfen daha sonra tekrar deneyiniz.")

    return render(request, "urunler/urun_detay.html", {"urun": urun})

def teklif_basarili(request):
    return render(request, 'urunler/teklif_basarili.html')

from django.shortcuts import render, get_object_or_404
from .models import TeklifCevap

def odeme_sayfasi(request, cevap_id):
    cevap = get_object_or_404(TeklifCevap, pk=cevap_id)

    # Taksit tutarı hesapla (bölme hatasına karşı korumalı)
    birim_taksit = round(cevap.taksitli_fiyat / cevap.taksit_sayisi, 2) if cevap.taksit_sayisi else 0

    context = {
        "sigorta_sirketi": cevap.sigorta_sirketi.ad,
        "urun_ad": cevap.teklif.urun.sigorta_tipi,
        "pesin": cevap.pesin_fiyat,
        "taksit_sayisi": cevap.taksit_sayisi,
        "birim_taksit": birim_taksit
    }
    return render(request, "odeme/sayfa.html", context)



options = {
    'api_key': settings.IYZICO_API_KEY,
    'secret_key': settings.IYZICO_SECRET_KEY,
    'base_url': settings.IYZICO_BASE_URL
}
def iyzico_odeme_baslat(request):
    conversation_id = str(uuid.uuid4())
    total_fiyat = "100.0"  # Örnek tutar – teklif.fiyat vs. dinamikleşebilir

    options = {
        'api_key': settings.IYZICO_API_KEY,
        'secret_key': settings.IYZICO_SECRET_KEY,
        'base_url': settings.IYZICO_BASE_URL
    }

    request_data = {
        "locale": "tr",
        "conversationId": conversation_id,
        "price": total_fiyat,
        "paidPrice": total_fiyat,
        "currency": "TRY",
        "callbackUrl": "https://seninsiten.com/odeme-sonuc/",
        "basketId": "B67832",
        "paymentGroup": "PRODUCT",
        "enabledInstallments": [2, 3, 6, 9],
        "buyer": {
            "id": "BY789",
            "name": "Haluk",
            "surname": "Demir",
            "email": "haluk@example.com",
            "identityNumber": "11111111110",
            "registrationAddress": "Ankara, Yenimahalle",
            "city": "Ankara",
            "country": "Türkiye",
            "ip": request.META.get("REMOTE_ADDR", "127.0.0.1")
        },
        "billingAddress": {
            "contactName": "Haluk Demir",
            "city": "Ankara",
            "country": "Türkiye",
            "address": "Yenimahalle"
        },
        "basketItems": [
            {
                "id": "URUN001",
                "name": "Kasko Sigortası",
                "category1": "Sigorta",
                "itemType": "PHYSICAL",
                "price": total_fiyat
            }
        ]
    }

    checkout_form = iyzipay.CheckoutFormInitialize().create(request_data, options).read()
    checkout_dict = json.loads(checkout_form)
    return redirect(checkout_dict["paymentPageUrl"])



@csrf_exempt  # Çünkü iyzico POST isteği yapar
def odeme_sonuc(request):
    if request.method == "POST":
        status = request.POST.get("status")
        conversation_id = request.POST.get("conversationId")

        if status == "success":
            # Burada teklif veya ödeme kaydı güncellenebilir
            return render(request, "odeme/basarili.html")
        else:
            return render(request, "odeme/basarisiz.html")
    return HttpResponse(status=400)
