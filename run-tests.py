#!/usr/bin/env python
import os
import sys
import subprocess

formula = "dummy"
BASEDIR = os.path.abspath(os.path.dirname(__file__))


def build(image, salt=False):
    dockerfile = "test/{0}.Dockerfile".format(image)
    tag = "{0}-formula:{1}".format(formula, image)
    if salt:
        dockerfile_content = open(dockerfile).read()
        dockerfile_content += "\n" + "\n".join([
            "ADD test/minion.conf /etc/salt/minion.d/minion.conf",
            "ADD {0} /srv/formula/{0}".format(formula),
            "RUN salt-call --retcode-passthrough state.sls {0}".format(formula),
        ]) + "\n"
        dockerfile = "test/{0}_salted.Dockerfile".format(image)
        with open(dockerfile, "w") as f:
            f.write(dockerfile_content)
    subprocess.check_call(["docker", "build", "-t", tag, "-f", dockerfile, "."])
    return tag


def dev(image):
    tag = build(image)
    subprocess.call([
        "docker", "run", "-i", "-t", "--rm", "--hostname", image,
        "-v", "{0}/test/minion.conf:/etc/salt/minion.d/minion.conf".format(BASEDIR),
        "-v", "{0}/{1}:/srv/formula/{1}".format(BASEDIR, formula),
        tag, "/bin/bash",
    ])


def test(image):
    import pytest
    tag = build(image, salt=True)
    docker_id = subprocess.check_output([
        "docker", "run", "-d", "--hostname", image,
        "-v", "{0}/test/minion.conf:/etc/salt/minion.d/minion.conf".format(BASEDIR),
        "-v", "{0}/{1}:/srv/formula/{1}".format(BASEDIR, formula),
        tag, "tail", "-f", "/dev/null",
    ]).strip()
    try:
        sys.exit(pytest.main(["--hosts", "docker://" + docker_id] + sys.argv[3:]))
    finally:
        subprocess.check_call(["docker", "rm", "-f", docker_id])


if __name__ == "__main__":
    {
        "build": build,
        "dev": dev,
        "test": test,
    }[sys.argv[1]](sys.argv[2])
