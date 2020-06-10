import logging
import os
import subprocess

from celery import Celery

# Simple task manager using this guide:
# https://docs.celeryproject.org/en/stable/getting-started/first-steps-with-celery.html#first-steps

# TODO: Add rabbitmq backend to build script
app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
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
    os.chdir("/scenario")  # TODO: Figure out how not to hard-code this
    # subprocess.Popen(["vagrant restore {} clean".format(vm.name)])
    proc = subprocess.run(["vagrant", "restore", name, snapshot_name], capture_output=True)
    logging.debug("revert_vm STDOUT: {}".format(proc.stdout))
    logging.warning("revert_vm STDERR: {}".format(proc.stderr))

    os.chdir(old_cwd)
    return (proc.stdout, proc.stderr)
