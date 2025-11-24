from django import forms
from .models import Teklif

def tc_kimlik_no_dogrula(tc):
    if not tc or not tc.isdigit() or len(tc) != 11 or tc[0] == '0':
        return False
    digits = list(map(int, tc))
    if (sum(digits[:10]) % 10 != digits[10]):
        return False
    if (((sum(digits[0:9:2]) * 7) - sum(digits[1:8:2])) % 10 != digits[9]):
        return False
    return True

class TeklifForm(forms.ModelForm):
    class Meta:
        model = Teklif
        fields = '__all__'
        widgets = {
            'tc_kimlik_no': forms.TextInput(attrs={'maxlength': '11'})
        }

    def clean_tc_kimlik_no(self):
        tc = self.cleaned_data.get('tc_kimlik_no')
        if tc and not tc_kimlik_no_dogrula(tc):
            raise forms.ValidationError("Geçersiz T.C. Kimlik Numarası")
        return tc