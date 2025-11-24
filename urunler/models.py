from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Urun(models.Model):
    sigorta_tipi = models.CharField(max_length=100)
    aciklama = models.TextField()
    gorsel = models.ImageField(upload_to="urun_resimleri/")
  



    def __str__(self):
        return self.sigorta_tipi

class Teklif(models.Model):
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    ad = models.CharField("Ad", max_length=50, null=True, blank=True)
    soyad = models.CharField("Soyad", max_length=50, null=True, blank=True)
    tc_kimlik_no = models.CharField("T.C. Kimlik No", max_length=11, blank=True, null=True)
    cep_telefonu = models.CharField(max_length=20)
    eposta = models.EmailField()
    belge = models.FileField(upload_to="teklif_belgeleri/", blank=True, null=True)
    tarih = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"{self.urun.sigorta_tipi} - {self.eposta}"
    
class SigortaSirketi(models.Model):
    ad = models.CharField(max_length=100)
    sira = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sira']  # Kullanıcı sırasına göre listelenir

    def __str__(self):
        return self.ad

class TeklifCevap(models.Model):
    sigorta_sirketi = models.ForeignKey(SigortaSirketi, on_delete=models.SET_NULL, null=True, blank=True)
    teklif = models.ForeignKey('Teklif', on_delete=models.CASCADE, related_name='cevaplar')
    sira = models.PositiveIntegerField(null=True, blank=True)
    pesin_fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    taksit_sayisi = models.IntegerField()
    taksitli_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    eposta_gonderildi = models.BooleanField(default=False)
    gonderim_tarihi = models.DateTimeField(null=True, blank=True)
    eposta_gonderen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.sira:
            max_sira = TeklifCevap.objects.filter(teklif=self.teklif).aggregate(models.Max('sira'))['sira__max'] or 0
            self.sira = max_sira + 1
        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.teklif.urun} - Teklif {self.sira}"
    



def tc_kimlik_no_dogrula(tc):
    if not tc or not tc.isdigit() or len(tc) != 11 or tc[0] == '0':
        return False

    digits = list(map(int, tc))
    if (sum(digits[:10]) % 10 != digits[10]):
        return False
    if (((sum(digits[0:9:2]) * 7) - sum(digits[1:8:2])) % 10 != digits[9]):
        return False
    return True



