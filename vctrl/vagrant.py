import asyncio
import configparser
import datetime
import logging
import os
import re
import subprocess

from vctrl.models import VM, Scenario
from django.conf import settings
from datetime import timedelta

# Before we can run anything in this module, we need to get the Scenario, or if there is none, try to create one.
# FIXME: Should we plan for more than one scenario to be in the Database?

# TODO: Figure out whether or not hard coding this is absolutely necessary
# CONFIG_FILE = "/scenario/scenario.ini"
CONFIG_FILE = settings.SCENARIO_CONFIG


try:
    SCENARIO = Scenario.objects.get(pk=1)
    SCENARIO_DIRECTORY = SCENARIO.dir

except Exception as e:
    logging.error("Exception raised during vagrant.py import: {}".format(e.__str__()))
    parser = configparser.ConfigParser()
    try:
        with open(CONFIG_FILE, "r") as ini_file:
            logging.debug("load_scenario: reading config from file in /scenario")
            parser.read_file(ini_file)
        s_name = parser.get("Scenario", "name")
        s_duration = timedelta(hours=int(parser.get("Scenario", "duration")))

        s_description = parser.get("Scenario", "description")
        s_dir = "/scenario"
        # TODO: Do we want to put in an option to set this value?
        s_start = datetime.datetime.now()
        init_scenario = Scenario(name=s_name, start=s_start, dir=s_dir, duration=s_duration)
        init_scenario.save()

    except FileNotFoundError:
        # Load the default Scenario config located in the app root
        logging.debug(
            "vagrant.py couldn't find a scenario.ini file in {}, creating default Scenario".format(CONFIG_FILE))
        init_scenario = Scenario()
        init_scenario.save()
        SCENARIO = init_scenario
        SCENARIO_DIR = init_scenario.dir


async def vagrant_cmd(*args):
    """
    Runs a vagrant command asynchronously
    :param str vcmd: Shell command to run
    :return:
    """
    proc = await asyncio.create_subprocess_exec(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args)
    stdout, stderr = await proc.communicate()

    print("{} exited with status code {}".format(args[0], proc.returncode))
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


def update_scenario():
    # Reruns the SCENARIO variable selection from import
    # Skip if we already have a Scenario that's not the default
    # This is mainly designed for the interim between server load and Scenario insertion
    global SCENARIO
    global SCENARIO_DIRECTORY

    if SCENARIO.name != "default":
        logging.debug("update_scenario: Non-default Scenario found, skipping update")
        return

    try:
        SCENARIO = Scenario.objects.get(pk=1)
        SCENARIO_DIRECTORY = SCENARIO.dir
        logging.debug("update_scenario: Scenario has been updated to {}".format(SCENARIO.name))

    except Exception as e:
        logging.error("Exception raised during vagrant.py import: {}".format(e.__str__()))
        # raise Exception("No Scenario found! Please make sure there's a scenario in the database")
        # Create an empty Scenario
        logging.warning("vagrant.py: Could not find scenario in database; creating empty Scenario")
        # Try to pull Scenario information from the environment
        # SCENARIO = Scenario()
        # SCENARIO.dir = '.'
        # SCENARIO.save()
        # SCENARIO = Scenario.objects.get(pk=1)
        SCENARIO = Scenario()
        SCENARIO_DIRECTORY = "."
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
    logging.warning("scenario_status: Moving cwd from {} -> {}".format(old_cwd, SCENARIO_DIRECTORY))
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

    if not vms:
        logging.warning("sync_vms: No VMs reported by scenario_status, no action taken")
        return

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


def revert_vm(name, snapshot_name="clean", output=True):
    """
    Use a subprocess command to make a vagrant revert call and track its output
    :param name:
    :param snapshot_name:
    :param bool output: Whether or not we would like the output to be returned
    :return A tuple with the standard output and error buffers from the vagrant process
    :rtype tuple(str, str)
    """
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    # subprocess.Popen(["vagrant restore {} clean".format(vm.name)])
    proc = subprocess.run(["vagrant", "restore", name, snapshot_name], capture_output=True)
    logging.debug("revert_vm STDOUT: {}".format(proc.stdout))
    logging.warning("revert_vm STDERR: {}".format(proc.stderr))

    os.chdir(old_cwd)
    return (proc.stdout, proc.stderr)


def snapshot_vm(name, snapshot_name="clean"):
    """
    Create a snapshot of the given VM with the default VM name "clean"
    :param name:
    :param snapshot_name:
    :return:
    """
    old_cwd = os.getcwd()
    os.chdir(SCENARIO_DIRECTORY)
    proc = subprocess.run(["vagrant", "snapshot", "save", name, snapshot_name], capture_output=True)
    logging.debug("snapshot_vm STDOUT: {}".format(proc.stdout))
    logging.warning("snapshot_vm STDERR: {}".format(proc.stderr))
    os.chdir(old_cwd)

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
