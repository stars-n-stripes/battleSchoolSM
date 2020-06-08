from django.apps import AppConfig


# from .models import Scenario, VM
# from . import vagrant


class VctrlConfig(AppConfig):
    name = 'vctrl'
    verbose_name = "Vagrant Control"

    def ready(self):
        # Startup code here
        pass
