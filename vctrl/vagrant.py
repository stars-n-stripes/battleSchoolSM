import logging
import os
import re
import subprocess

from .models import VM, Scenario

SCENARIO_DIRECTORY = '/scenario'
# Before we can run anything in this module, we need to get the Scenario, or if there is none, try to create one.
# FIXME: Should we plan for more than one scenario to be in the Database?
SCENARIO = Scenario.objects.get(pk=1)

if not SCENARIO:
    # raise Exception("No Scenario found! Please make sure there's a scenario in the database")
    # Create an empty Scenario
    logging.warning("vagrant.py: Could not find scenario in database; creating empty Scenario")
    SCENARIO = Scenario()
    SCENARIO.save()


def scenario_status(name=None, status=None):
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
    :rtype: dict
    https://docs.python.org/3/library/re.html
    """
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    status_re = re.compile(r"^(?P<name>\w[^ {2,}]+)\s+(?P<status>.+) \(.+\)", flags=re.MULTILINE)
    # Make a vagrant status call and collect STDOUT
    proc = subprocess.run(["vagrant", "status"], capture_output=True)
    out = proc.stdout.decode("utf-8")
    # Extract the VMs and their status with regex
    matches = re.findall(status_re, out)
    if not matches:
        logging.error('scenario_status: No VMs were extracted by "vagrant status". This should only happen if all'
                      'Vagrant machines are destroyed or the scenario directory is incorrect')
        return None

    s_status = []

    for match in matches:
        status = match[1]
        name = match[0]
        s_status.append(VM(name=name, status=status, scenario=SCENARIO))
    os.chdir(old_cwd)
    return s_status


def sync_vms():
    """
    Using get_vms for data collection, create a Django VM model for each machine in the scenario and saves it to
    the database. Avoids adding redundant VMs
    :return: None
    """
    vms = scenario_status()
    for vm in vms:
        logging.debug("sync_vms: Processing vm: {}".format(vm.name))
        # Check if that VM is in the database already
        db_vm = VM.objects.filter(name=vm.name)
        if db_vm:
            # Push the status to the current VM
            logging.debug("sync_vms: VM exists in database, updating status only")
            db_vm[0].status = vm.status
            db_vm[0].save()
        else:
            # Save this temporary VM to the database
            logging.debug("sync_vms: VM does not exist, saving temporary VM to database")
            SCENARIO.vm_set.create(name=vm.name, status=vm.status)


def revert_vm(name, snapshot_name="clean"):
    """
    Use a subprocess command to make a vagrant revert call and track its output
    :param name:
    :param snapshot_name:
    :return:
    """
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    # subprocess.Popen(["vagrant restore {} clean".format(vm.name)])
    proc = subprocess.run(["vagrant", "restore", name, snapshot_name], capture_output=True)
    # TODO: Finish implementation.
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
