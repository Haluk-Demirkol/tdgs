from django.contrib import admin, messages
from django.utils.html import format_html
from django.core.mail import send_mail
from django.utils.timezone import now
from .models import SigortaSirketi
from .models import Urun, Teklif, TeklifCevap
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# --- URUN ADMIN ---

@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ['sigorta_tipi', 'gorsel_onizleme']
    readonly_fields = ['gorsel_onizleme']

    def gorsel_onizleme(self, obj):
        if obj.gorsel:
            return format_html(
                '<img src="{}" width="100" height="auto" '
                'style="border:1px solid #ccc; border-radius:4px;" />',
                obj.gorsel.url
            )
        return "Görsel yok"

    gorsel_onizleme.short_description = "Önizleme"

# --- INLINE: TEKLIFCEVAP ---
class TeklifCevapInline(admin.TabularInline):
    model = TeklifCevap
    extra = 3
    readonly_fields = ['eposta_gonderildi', 'gonderim_tarihi', 'eposta_gonderen', 'gonderim_bilgisi']
    autocomplete_fields = ['sigorta_sirketi']    
    
    def gonderim_bilgisi(self, obj):
        if obj.eposta_gonderildi:
            return f"{obj.gonderim_tarihi.strftime('%d.%m.%Y %H:%M')} - {obj.eposta_gonderen}"
        return "—"
    gonderim_bilgisi.short_description = "Gönderildiğinde"

class EpostaDurumuFilter(admin.SimpleListFilter):
    title = "E-posta Durumu"
    parameter_name = "eposta_durumu"

    def lookups(self, request, model_admin):
        return [
            ('bekliyor', 'Bekleyen Teklifler'),
            ('gonderildi', 'Gönderilen Teklifler'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'bekliyor':
            return queryset.filter(cevaplar__eposta_gonderildi=False).distinct()
        if self.value() == 'gonderildi':
            return queryset.filter(cevaplar__eposta_gonderildi=True).distinct()


# --- TEKLIF ADMIN ---

@admin.register(Teklif)
class TeklifAdmin(admin.ModelAdmin):
    list_display = ['urun', 'ad', 'soyad', 'eposta', 'cep_telefonu', 'created_at', 'eposta_durumu']
    list_filter = ['urun', 'created_at', EpostaDurumuFilter]
    readonly_fields = ['created_at']
    inlines = [TeklifCevapInline]
    actions = ['teklif_eposta_gonder']
    
    def eposta_durumu(self, obj):
        varsa = obj.cevaplar.filter(eposta_gonderildi=True).exists()
        renk = "#28a745" if varsa else "#f30606"  # yeşil veya gri
        yazi = "Gönderildi" if varsa else "Bekliyor"
        return format_html(
            '<span style="color:{}; font-weight:bold;">● {}</span>',
                renk,
                yazi
    )

    eposta_durumu.short_description = "E-posta Durumu"
    

    @admin.action(description="Seçilen tekliflere e-posta gönder")
    def teklif_eposta_gonder(self, request, queryset):
        basarili = 0

        for teklif in queryset:
            cevaplar = teklif.cevaplar.filter(eposta_gonderildi=False)
            if not cevaplar.exists():
                continue

            context = {
            "urun_ad": teklif.urun.sigorta_tipi,
            "alici": teklif.ad + " " + teklif.soyad,
            "teklifler": [
        {
            "sira": c.sira,
            "sigorta_sirketi": c.sigorta_sirketi.ad,
            "pesin": c.pesin_fiyat,
            "taksitli": c.taksitli_fiyat,
            "birim_taksit": round(c.taksitli_fiyat / c.taksit_sayisi, 2) if c.taksit_sayisi > 0 else 0,
            "taksit_sayisi": c.taksit_sayisi,
            "odeme_linki": f"http://127.0.0.1:8000/odeme/{c.id}/"

        }
        for c in cevaplar
    ]
}

            try:
                html_icerik = render_to_string("email/teklif.html", context)

                msg = EmailMultiAlternatives(
                    subject="Sigorta Teklifiniz",
                    body="Tarayıcınız HTML desteklemiyorsa bu mesajı düz metin olarak görüyorsunuz.",
                    from_email="info@seninsiten.com",
                    to=[teklif.eposta]
                )
                msg.attach_alternative(html_icerik, "text/html")
                msg.send()

                for c in cevaplar:
                    c.eposta_gonderildi = True
                    c.gonderim_tarihi = now()
                    c.eposta_gonderen = request.user
                    c.save()

                basarili += 1

            except Exception as e:
                messages.error(request, f"{teklif.eposta} için gönderim hatası: {str(e)}")

        if basarili > 0:
            messages.success(request, f"{basarili} teklif için HTML e-posta başarıyla gönderildi.")




@admin.register(SigortaSirketi)
class SigortaSirketiAdmin(admin.ModelAdmin):
    list_display = ['ad', 'sira']
    ordering = ['sira']
    search_fields = ['ad']  # 👈 bu satır zorunlu autocomplete için



