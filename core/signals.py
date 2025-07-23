from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.task import send_welcome_email
from .models import Compte, Transaction
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_transaction_id():
    return get_random_string(length=12).upper()


@receiver(post_save, sender=User)
def send_welcome_email_on_creation(sender, instance, created, **kwargs):
    if created:
        send_welcome_email(instance)

@receiver(pre_save, sender=Compte)
def create_transaction_on_solde_change(sender, instance, **kwargs):
    if not instance.pk:
        # Nouveau compte — aucune transaction à créer
        return

    try:
        old_instance = Compte.objects.get(pk=instance.pk)
    except Compte.DoesNotExist:
        return

    # Vérifie si le solde a changé
    if instance.solde != old_instance.solde:
        difference = instance.solde - old_instance.solde
        if difference > 0:
            type_transac = 'depot'
        else:
            type_transac = 'virement'

        Transaction.objects.create(
            id=generate_transaction_id(),
            type=type_transac,
            compte=instance,
            user=instance.proprietaire,
            montant=abs(difference)
        )
