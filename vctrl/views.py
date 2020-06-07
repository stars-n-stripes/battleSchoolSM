from os import chdir, getcwd

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from .models import VM


# Create your views here.
def index(request):
    # Pull all VMs that are accessible by the student
    RevertibleVMs = VM.objects.order_by('-name') & VM.objects.exclude(revertible=False)
    context = {'RevertibleVMs': RevertibleVMs}
    # return HttpResponse("This is the index for the Vagrant Control (vctrl) App.")
    return render(request, 'vctrl/index.html', context)


def revertvm(request):
    # Save cwd so we can return to it; move to the Vagrant project directory
    cwd = getcwd()
    chdir("/") # Debug
    # chdir("/scenario") # TODO: Make this dynamic to wherever the Vagrant directory is
    vm = VM.objects.filter(name=request.POST["vm_name"])[0]

    if vm:
        # Replace with helper function in vagrant.py
        print("I would have run this command: vagrant restore {} clean".format(vm.name)) # Debug
        # Restore previous directory
        chdir(cwd)
        response = HttpResponse("Reverting {}".format(vm.name)) # TODO: Change to view showing VM revert progress
    else:
        response = HttpResponseBadRequest("VM not found")

    # Restore previous directory
    chdir(cwd)
    return response
