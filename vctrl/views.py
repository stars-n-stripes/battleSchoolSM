from os import getcwd

from django.shortcuts import render

from . import vagrant
from .models import VM, Scenario


# Create your views here.
def index(request):
    # Update the Scenario and sync the VM database
    vagrant.update_scenario()
    vagrant.sync_vms()
    # Pull all VMs that are accessible by the student
    RevertibleVMs = VM.objects.order_by('-name') & VM.objects.exclude(revertible=False)
    Scenarios = Scenario.objects.order_by('-name')
    context = {'RevertibleVMs': RevertibleVMs, "Scenarios": Scenarios}
    # return HttpResponse("This is the index for the Vagrant Control (vctrl) App.")
    return render(request, 'vctrl/index.html', context)


def cancel_scenario(request):
    # Accepts POST page for scenario cancel
    # Probably just a redirect back to index
    pass


def revertvm(request):
    # Save cwd so we can return to it; move to the Vagrant project directory
    cwd = getcwd()
    # chdir("/") # Debug
    # chdir("/scenario") # TODO: Make this dynamic to wherever the Vagrant directory is
    vm = VM.objects.filter(name=request.POST["vm_name"])[0]

    if vm:
        # Replace with helper function in vagrant.py
        # print("I would have run this command: vagrant restore {} clean".format(vm.name)) # Debug
        # asyncio.run(vagrant.vagrant_cmd("vagrant", "revert", vm.name, "clean"))
        vagrant.revert_vm(vm.name)
        # Restore previous directory
        # chdir(cwd)
        context = {"Message": "Reverted {}".format(vm.name)}  # TODO: Change to view showing VM revert progress
        return render(request, 'vctrl/revertvm.html', context)
    else:
        context = {"Message": "Could not find VM {}".format(vm.name)}
        return render(request, 'vctrl/revertvm.html', context)


def load_scenario(request):
    pass
