from django.apps import AppConfig


# from .models import Scenario, VM
# from . import vagrant


class VctrlConfig(AppConfig):
    name = 'vctrl'
    verbose_name = "Vagrant Control"

    def ready(self):
        # Startup code here
        # TODO: Add code here to populate the database with the VMs in the scenario, as well as the Scenario itself.
        from . import vagrant
        vagrant.sync_vms()
