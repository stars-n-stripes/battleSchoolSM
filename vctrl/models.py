from datetime import timedelta

from django.db import models
from django.utils import timezone


# Create your models here.
class Scenario(models.Model):
    def __str__(self):
        return self.name

    # def is_expired(self):
    #     return timezone.now() > self.end
    name = models.CharField(max_length=200, default="default")
    dir = models.CharField(max_length=200, default=".")
    description = models.CharField(max_length=200,
                                   default="The default scenario that BSSM loads in the absence of a regular scenario.ini file")
    duration = models.DurationField("Scenario time limit, in hours", default=timedelta(hours=1))
    start = models.DateTimeField(default=timezone.now())
    def remaining(self):
        # Return either the remaining duration or zero if the scenario has expired
        return min((self.start + self.duration) - timezone.now(), timedelta(0))



class VM(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=64)
    in_scope = models.BooleanField("Whether or not this VM is in scope for this challenge.", default=True)
    revertible = models.BooleanField("Whether or not the student is allowed to revert this machine.", default=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)

class Flag(models.Model):
    def __str__(self):
        if self.captured:
            return "Captured Flag for {}".format(self.vm.name)
        else:
            return "Uncaptured Flag for {}".format(self.vm.name)

    text = models.CharField(max_length=200)
    vm = models.ForeignKey(VM, on_delete=models.CASCADE)
    captured = models.BooleanField("Whether or not the student has found this flag.", default=False)


class Student(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    kali = models.ForeignKey(VM, on_delete=models.CASCADE)

# VAGRANT HELPER FUNCTIONS
