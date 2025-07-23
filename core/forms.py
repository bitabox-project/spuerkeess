from django import forms
from .models import User


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'nom', 'prenom', 'assistant','sexe', 'email', 'telephone',
            'date_naissance', 'lieu_naissance', 'pays_naissance',
            'nationalite1', 'nationalite2', 'etat_civil', 'nom_conjoint',
            'adresse', 'pays_residence', 'agence', 'profession',
            'cnioupassport', 'relevecompte', 'preuveadresse'
        ]



class UserLoginForm(forms.Form):
    identifiant = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
