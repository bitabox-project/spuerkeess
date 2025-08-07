import random
import string
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import *
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth import logout as auth_logout



User = get_user_model()

# Create your views here.
def index(request):

    return render(request, 'www.spuerkeess.lu/fr/index.html')

def particulier(request):

    return render(request, 'www.spuerkeess.lu/fr/particuliers/index.html')

# def tweenss(request):

#     return render(request, 'www.spuerkeess.lu/fr/tweenz/index.html')

# def axxess(request):

#     return render(request, 'www.spuerkeess.lu/fr/axxess/index.html')

# def professionnel(request):

#     return render(request, 'www.spuerkeess.lu/fr/proffessionnels/index.html')

def generate_id():
    """Génère un ID alphanumérique (lettres MAJ + chiffres) de longueur `num`"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=12))

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Création de l'utilisateur
                user = form.save()
                user.set_password('00000000')  # À remplacer par mot de passe sécurisé en production
                user.save()

                # Création du compte associé
                Compte.objects.create(
                    id=generate_id(),
                    nom="Compte Depot",
                    proprietaire=user,
                    solde=0.0,
                    description='Compte principal',
                    devise='EUR'
                )

                messages.success(request, "Inscription réussie. Vous pouvez vous connecter.")
                return redirect('particulier')

            except Exception as e:
                # Gestion générique des erreurs
                messages.error(request, f"Une erreur est survenue : {str(e)}")
                return redirect('register')
    else:
        form = UserRegisterForm()
    
    return render(request, 'www.spuerkeess.lu/fr/particuliers/outils/onboarding-form/index.html', {
        'form': form,
        'message': messages.get_messages(request)
    })
def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            identifiant = form.cleaned_data['identifiant']
            password = form.cleaned_data['password']
            
            try:
                # Utilisez get() au lieu de filter() pour obtenir un seul objet
                user = User.objects.get(id=identifiant)
                authenticated_user = authenticate(request, email=user.email, password=password)
                
                if authenticated_user is not None:
                    auth_login(request, authenticated_user)
                    messages.success(request, "Connexion réussie!")
                    return redirect('Mon_compte')
                else:
                    messages.error(request, "Mot de passe incorrect")
            except User.DoesNotExist:
                messages.error(request, "Identifiant utilisateur introuvable")
            except Exception as e:
                messages.error(request, f"Une erreur est survenue: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = UserLoginForm()
    
    return render(request, 'manager/login.html', {'form': form})


def logout_view(request):
    """
    Déconnecte l'utilisateur et le redirige vers la page de connexion.
    """
    auth_logout(request)
    return redirect('login') 

def change_password(request):
    if request.method == 'POST':
        identifiant = request.POST.get('identifiant')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        
        # Vérifications côté serveur (double sécurité)
        if len(identifiant) != 10:
            messages.error(request, "Identifiant invalide")
            return redirect('change_password')
        
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return redirect('change_password')
        
        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères")
            return redirect('change_password')
        
        # Ici vous ajouteriez la logique de modification du mot de passe
        # Par exemple :
        try:
            user = User.objects.get(id=identifiant)
            print(user)
            user.set_password(password)
            user.save()
            messages.success(request, "Mot de passe modifié avec succès")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé")
            return redirect('change_password')
    
    return render(request, 'manager/addpassword.html')

# Formulaire Django basique pour Compte
class CompteForm(forms.ModelForm):
    class Meta:
        model = Compte
        fields = ['solde', 'description', 'devise']

# Créer un nouveau compte
@login_required
def add_compte(request):
    if request.method == 'POST':
        try:
            nom = request.POST.get('nom', '').strip()
            description = request.POST.get('description', '').strip()
            devise = request.POST.get('devise', '').strip()
            solde_raw = request.POST.get('solde', '').strip()

            if not description or not devise or not solde_raw or not nom:
                messages.error(request, "Tous les champs sont requis.")
                return redirect('Mon_compte')

            try:
                solde = float(solde_raw)
            except ValueError:
                messages.error(request, "Le solde doit être un nombre valide.")
                return redirect('Mon_compte')

            if solde < 0:
                messages.error(request, "Le solde ne peut pas être négatif.")
                return redirect('Mon_compte')

            Compte.objects.create(
                id=generate_id(),
                nom=nom,
                proprietaire=request.user,
                description=description,
                devise=devise.upper(),
                solde=solde
            )

            messages.success(request, "Nouveau compte ajouté avec succès !")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")

        return redirect('Mon_compte')
    else:
        return redirect('Mon_compte')
# Liste des comptes de l'utilisateur connecté
@login_required
def liste_comptes(request):
    comptes = Compte.objects.filter(proprietaire=request.user)
    return render(request, 'comptes/liste_comptes.html', {'comptes': comptes})

# Voir un seul compte
@login_required
def voir_compte(request, compte_id):
    compte = get_object_or_404(Compte, id=compte_id)
    if compte.proprietaire != request.user:
        return HttpResponseForbidden()
    return render(request, 'comptes/voir_compte.html', {'compte': compte})

# Supprimer un compte
@login_required
def supprimer_compte(request, compte_id):
    compte = get_object_or_404(Compte, id=compte_id)
    if compte.proprietaire != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        compte.delete()
        return redirect('liste_comptes')
    return render(request, 'comptes/supprimer_compte.html', {'compte': compte})

@login_required
def dashboard(request):
    comptes = []
    transactions = []
    try:
        comptes = Compte.objects.filter(proprietaire=request.user)
        transactions = Transaction.objects.filter(user=request.user)
        depot_crypto = DepotCrypto.objects.get(user=request.user)
    except Exception as e:
        # Log l'erreur en prod ou en dev si besoin
        print(f"Erreur lors de la récupération des comptes : {e}")
        comptes = []
        transactions = []

    context = {
        'comptes': comptes,
        'transactions': transactions,
        'depot': depot_crypto
    }
    return render(request, 'manager/dashboard.html', context)

def apropos(request):

    return render(request, 'www.spuerkeess.lu/fr/a-propos-de-nous/decouvrir-la-bcee-histoire-aa-plus-rating-safest-bank-award-fondation-1856/index.html')

def devenirclient(request):

    return render(request, 'www.spuerkeess.lu/fr/particuliers/outils/devenir-client-de-spuerkeess/index.html')


@login_required
def depot_view(request, compte_id):
    # Maintenant tu as accès à compte_id
    compte = get_object_or_404(Compte, id=compte_id, proprietaire=request.user)
    depot = get_object_or_404(Depot, compte=compte_id, utilisateur=request.user)

    if request.method == 'POST':
        montant = float(request.POST.get('montant'))
        print(montant)
        return redirect('Mon_compte')  # redirige vers le dashboard ou autre

    context = {
        'compte': compte,
        'depot': depot
    }
    return render(request, 'manager/depot.html', context)

@login_required
def virement(request):
    comptes = Compte.objects.filter(proprietaire=request.user)
    if request.method == 'POST':
        compte_id = request.POST.get('compte_debit')
        compte_debit = get_object_or_404(Compte, id=compte_id, proprietaire=request.user)
        montant = float(request.POST.get('montant'))

        if montant <= 0:
            messages.error(request, "Le montant doit être supérieur à zéro.")
            return redirect('virement')

        if compte_debit.solde < montant:
            messages.error(request, "Solde insuffisant.")
            return redirect('virement')

        # Enregistrer le virement
        Virement.objects.create(
            compte_debit=compte_debit,
            nom_beneficiaire=request.POST.get('nom_beneficiaire'),
            banque_beneficiaire=request.POST.get('banque_beneficiaire'),
            iban=request.POST.get('iban'),
            bic=request.POST.get('bic'),
            montant=montant,
        )

        messages.success(request, "Virement effectué avec succès.")
        return redirect('Mon_compte')

    return render(request, 'manager/virement.html', {'comptes': comptes})