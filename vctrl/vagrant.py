import os
import re

SCENARIO_DIRECTORY = '/scenario'


def get_vms(name=None, status=None):
    """
    Execute a subprocess that collects information on currently running VMs in the scenario directory.
    If "status" is specified, returns only the VMs that match the given status.
    :param str status: Filter results by a particular status. Valid statuses include:
        running
        suspended
        not created
        not running
    :param str name: A specific VM in the scenario to get information on
    :return: A list of each VM in the scenario by name
    :rtype: list(VM)
    https://docs.python.org/3/library/re.html
    """
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    status_re = re.compile(r"^(?P<name>\w[^ {2,}]+)\s+(?P<status>.+) \(.+\)", flags=re.MULTILINE)
    # TODO: Implement.
    os.chdir(old_cwd)
    raise NotImplementedError


def sync_vms():
    """
    Using get_vms for data collection, create a Django VM model for each machine in the scenario and saves it to
    the database.
    :return: None
    """
    vms = get_vms()
    for vm in vms:
        # Create, then save a VM model
        vm.save()


def revert_vm(name, snapshot_name="clean"):
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    # subprocess.Popen(["vagrant restore {} clean".format(vm.name)])
    # TODO: Implement.
    os.chdir(old_cwd)
    raise NotImplementedError


def snapshot_vm(name, snapshot_name="clean"):
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    # TODO: Implement.
    os.chdir(old_cwd)
    raise NotImplementedError


def sync_scenario():
    """
    Read the Vagrantfile and use it to define Scenario(s) for the database
    :return:
    """
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    # TODO: Implement.
    os.chdir(old_cwd)
    raise NotImplementedError
