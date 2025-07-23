import string
import random
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.core.validators import MinValueValidator


def generate_unique_id():
    """Génère un ID numérique aléatoire avec `num` chiffres"""
    range_start = 10**(10 - 1)
    range_end = (10**10) - 1
    return str(random.randint(range_start, range_end))



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.id = generate_unique_id()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Assistant(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_unique_id, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    def __str__(self):
        return f"{self.nom.upper()} {self.prenom.title()}"



class User(AbstractBaseUser,PermissionsMixin):
    id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False, default=generate_unique_id)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name='assistant',blank=True, null=True)
    sexe = models.CharField(max_length=10, choices=[('M', 'Homme'), ('F', 'Femme')])
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20,blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100,blank=True, null=True)
    pays_naissance = models.CharField(max_length=100,blank=True, null=True)
    nationalite1 = models.CharField(max_length=50,blank=True, null=True)
    nationalite2 = models.CharField(max_length=50, blank=True, null=True)
    etat_civil = models.CharField(max_length=50,blank=True, null=True)
    nom_conjoint = models.CharField(max_length=100, blank=True, null=True)
    adresse = models.CharField(max_length=255,blank=True, null=True)
    pays_residence = models.CharField(max_length=100,blank=True, null=True)
    agence = models.CharField(max_length=100,blank=True, null=True)
    profession = models.CharField(max_length=100,blank=True, null=True)
    cnioupassport = models.FileField(upload_to='documents/cni_passport/',blank=True, null=True)
    relevecompte = models.FileField(upload_to='documents/releve_compte/',blank=True, null=True)
    preuveadresse = models.FileField(upload_to='documents/preuve_adresse/',blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UserManager()

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.email}"

class Compte(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_unique_id, editable=False)
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comptes')
    nom = models.TextField(blank=True, null=True)
    solde = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    devise = models.CharField(max_length=10, default='EUR')

    def __str__(self):
        return f"Compte {self.id} - Propriétaire : {self.proprietaire.nom} {self.proprietaire.prenom}"
    

class Depot(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_unique_id, editable=False)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    banque = models.CharField(max_length=100)
    guichet = models.CharField(max_length=50)
    rib = models.CharField(max_length=50)
    iban = models.CharField(max_length=50)
    bic = models.CharField(max_length=50)
    domiciliation = models.TextField()
    montant = models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Depot {self.montant} € - {self.utilisateur.email}"
    
class Virement(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_unique_id, editable=False)
    compte_debit = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='virements_emis')
    nom_beneficiaire = models.CharField(max_length=255)
    banque_beneficiaire = models.CharField(max_length=255)
    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=11)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_virement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Virement de {self.montant} depuis {self.compte_debit}'
    

TRANSACTION_TYPES = (
    ('depot', 'Dépôt'),
    ('virement', 'Virement'),
)

class Transaction(models.Model):
    id = models.CharField(primary_key=True, max_length=12, editable=False)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    compte = models.ForeignKey('Compte', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.type.upper()} — {self.montant} € — {self.compte.id}"
    

class DepotCrypto(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('USDT_SOL', 'USDT (Solana)'),
        ('USDT_ETH', 'USDT (Ethereum)'),
        ('USDT_BSC', 'USDT (BSC)'),
    ]
    

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='depots_crypto',
        verbose_name="Utilisateur"
    )
    
    crypto_type = models.CharField(
        max_length=10,
        choices=CRYPTO_CHOICES,
        verbose_name="Type de cryptomonnaie"
    )
    
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        validators=[MinValueValidator(0.00000001)],
        verbose_name="Montant déposé"
    )
    
    btc_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        verbose_name="Adresse Bitcoin"
    )
    
    usdt_sol_address = models.CharField(
        max_length=44,
        blank=True,
        null=True,
        verbose_name="Adresse USDT (Solana)"
    )
    
    usdt_eth_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        verbose_name="Adresse USDT (Ethereum)"
    )
    
    usdt_bsc_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        verbose_name="Adresse USDT (BSC)"
    )
    
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Dépôt Cryptomonnaie"
        verbose_name_plural = "Dépôts Cryptomonnaie"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.crypto_type} - {self.amount}"

