#!/usr/bin/env python

import os
import subprocess

import click

formula = "dummy"
BASEDIR = os.path.abspath(os.path.dirname(__file__))


@click.group()
def cli():
    pass

image_choice = click.argument("image", type=click.Choice(["centos7", "jessie"]))


@cli.command(help="Build an image")
@image_choice
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
        tag += "_salted"
    subprocess.check_call(["docker", "build", "-t", tag, "-f", dockerfile, "."])
    return tag


@cli.command(help="Spawn an interactive shell in a new container")
@image_choice
@click.pass_context
def dev(ctx, image):
    tag = ctx.invoke(build, image=image)
    subprocess.call([
        "docker", "run", "-i", "-t", "--rm", "--hostname", image,
        "-v", "{0}/test/minion.conf:/etc/salt/minion.d/minion.conf".format(BASEDIR),
        "-v", "{0}/{1}:/srv/formula/{1}".format(BASEDIR, formula),
        tag, "/bin/bash",
    ])


@cli.command(help="Run tests against a provisioned container",
             context_settings={"allow_extra_args": True})
@click.pass_context
@image_choice
def test(ctx, image):
    import pytest
    tag = ctx.invoke(build, image=image, salt=True)
    docker_id = subprocess.check_output([
        "docker", "run", "-d", "--hostname", image,
        "-v", "{0}/test/minion.conf:/etc/salt/minion.d/minion.conf".format(BASEDIR),
        "-v", "{0}/{1}:/srv/formula/{1}".format(BASEDIR, formula),
        tag, "tail", "-f", "/dev/null",
    ]).strip()
    try:
        ctx.exit(pytest.main(["--hosts=docker://" + docker_id] + ctx.args))
    finally:
        subprocess.check_call(["docker", "rm", "-f", docker_id])


if __name__ == "__main__":
    cli()
