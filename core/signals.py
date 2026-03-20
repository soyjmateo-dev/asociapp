#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from django.db import transaction
#from core.models import Organizacion
#from core.services.tenant_provisioning import TenantProvisioningService


#@receiver(post_save, sender=Organizacion)
#def create_tenant_database(sender, instance, created, **kwargs):
#    print("🔥 SIGNAL DISPARADA:", instance.slug, "created=", created)

#    if created:
#        def provision():
#            TenantProvisioningService.provision_tenant(
#                slug=instance.slug,
#                admin_email=f"admin@{instance.slug}.com",
#                admin_password="cambiar123"
#            )

#        transaction.on_commit(provision)
