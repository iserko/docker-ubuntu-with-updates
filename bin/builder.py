#!/usr/bin/env python

import os
from shipper import Shipper, run, command
import subprocess

# DOCKER_URL = "/var/run/docker.sock"
DOCKER_HOST = "localhost:4243"
DOCKER_URL = "tcp://127.0.0.1:4243"
s = Shipper([DOCKER_HOST])

def pmk(t):
    rootdir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(rootdir, t)


def splitimage(name):
    return name.split(':', 1)


@command
def cleanup_containers():
    try:
      subprocess.check_call("docker -H {} ps -a -q | grep -q ''".format(DOCKER_URL), shell=True)
    except subprocess.CalledProcessError, e:
      s.log.debug("No docker containers found, skipping cleanup")
    else:
      cmd = "docker -H={} rm `docker -H {} ps -a -q`".format(DOCKER_URL, DOCKER_URL)
      s.log.debug("About to execute: {}".format(cmd))
      subprocess.check_output(cmd, shell=True)


@command
def cleanup_images():
    find_image_cmd="docker -H {} images".format(DOCKER_URL) + " | awk '/^<none>/ { print $3 }'"
    try:
      test_cmd = find_image_cmd + " | grep -q ''"
      subprocess.check_call(test_cmd, shell=True)
    except subprocess.CalledProcessError, e:
      s.log.debug("No docker images found, skipping cleanup")
    else:
      cmd = "docker -H={} rmi `".format(DOCKER_URL) + find_image_cmd + "`"
      s.log.debug("About to execute: {}".format(cmd))
      subprocess.check_output(cmd, shell=True)

@command
def precise(stamp):
    s.build(
        tag="precise-with-updates:{}".format(stamp),
        path=pmk("precise"))


@command
def export(image, exportto):
    container = s.run(image, "/bin/bash")[0]
    cmd = "docker -H={} export {} | gzip > {}".format(DOCKER_URL, container.id, exportto)
    s.log.debug("About to execute: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)
    s.stop(container)


@command
def flatten(image):
    repo, tag = splitimage(image)
    container = s.run(image, "/bin/bash")[0]

    cmd = "docker -H={} export {} > /tmp/{}.tar".format(DOCKER_URL, container.id, container.id)
    s.log.debug("About to execute: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)

    s.stop(container)

    cmd = "cat /tmp/{}.tar | docker -H={} import - {}:{}".format(container.id, DOCKER_URL, repo, tag)
    s.log.debug("About to execute: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)

    cmd = "rm -f /tmp/{}.tar".format(container.id)
    s.log.debug("About to execute: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)


@command
def retag(image, newname):
    repo, tag = splitimage(newname)
    cmd = "docker -H={} tag -f {} {}:{}".format(DOCKER_URL, image, repo, tag)
    s.log.debug("About to execute: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)



@command
def push(repo):
    s.log.debug("About to upload: {}".format(repo))
    cmd = "docker -H={} push {}".format(DOCKER_URL, repo)
    s.log.debug("About to execute: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)

run()
