from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Compte)
admin.site.register(Assistant)
admin.site.register(Depot)
admin.site.register(Virement)
admin.site.register(Transaction)
admin.site.register(DepotCrypto)

admin.site.site_header = "Administration Spuerkeess"
admin.site.site_title = "Dashboard Spuerkeess"
admin.site.index_title = "Welcome on Dashboard Spuerkeess"


