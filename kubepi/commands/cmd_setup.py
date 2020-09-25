from kubepi.cli import pass_environment, logger
from git import Repo

import click
import click_spinner
import subprocess as s
import docker
import ipaddress
import urllib.request
import os
import stat
import tarfile

# Setup group of commands


@click.group('setup', short_help='Setup infrastructure services')
@click.pass_context
@pass_environment
def cli(ctx, kube_context):
    """Setup infrastructure services on kubernetes.
    The name of the context is taken from the option --kube-context
    which defaults to 'k1s'"""
    pass


# Fetch all binaries for the dependencies
@cli.command('init', short_help='Initialize dependencies')
@click.pass_context
@pass_environment
def init(ctx, kube_context):
    """Download binaries for all dependencies"""

    # Figure out what kind of OS we are on
    ostype = os.uname().sysname.lower()

    # Kubectl parameters
    kubectl_stable = s.check_output(
        ['curl', '-s', 'https://storage.googleapis.com/kubernetes-release/release/stable.txt']).decode('utf-8')
    kubectl_url = 'https://storage.googleapis.com/kubernetes-release/release/{}/bin/linux/arm/kubectl'.format(
        kubectl_stable.split('\n')[0])

    # Helm parameters
    helm_url = 'https://get.helm.sh/helm-v3.3.1-{}-arm.tar.gz'.format(ostype)

    # K3D parameters
    k3d_url = 'https://github.com/rancher/k3d/releases/download/v3.0.1/k3d-{}-arm'.format(
        ostype)

    # Skaffold parameters
    skaffold_url = 'https://github.com/nushkovg/skaffold/releases/download/v1.14.0-arm/skaffold-{}-arm'.format(
        ostype)

    with click_spinner.spinner():
        # Download kubectl
        logger.info('Downloading kubectl...')
        urllib.request.urlretrieve(kubectl_url, 'bin/kubectl')
        st = os.stat('bin/kubectl')
        os.chmod('bin/kubectl', st.st_mode | stat.S_IEXEC)
        logger.info('kubectl downloaded')

        # Download helm
        logger.info('Downloading helm...')
        urllib.request.urlretrieve(helm_url, 'bin/helm.tar.gz')
        tar = tarfile.open('bin/helm.tar.gz', 'r:gz')
        for member in tar.getmembers():
            if member.name == 'helm':
                tar.extract('helm', 'bin')
        tar.close()
        os.remove('bin/helm.tar.gz')
        logger.info('helm downloaded!')

        # Download k3d
        logger.info('Downloading k3d...')
        urllib.request.urlretrieve(k3d_url, 'bin/k3d')
        st = os.stat('bin/k3d')
        os.chmod('bin/k3d', st.st_mode | stat.S_IEXEC)
        logger.info('k3d downloaded')

        # Download skaffold
        logger.info('Downloading skaffold...')
        urllib.request.urlretrieve(skaffold_url, 'bin/skaffold')
        st = os.stat('bin/skaffold')
        os.chmod('bin/skaffold', st.st_mode | stat.S_IEXEC)
        logger.info('skaffold downloaded')

    logger.info('All dependencies downloaded to bin/')
    logger.info('IMPORTANT: Please add the path to your user profile to ' +
                os.getcwd() + '/bin directory at the beginning of your PATH')
    logger.info('$ echo export PATH=' + os.getcwd() + '/bin:$PATH >> ~/.profile')
    logger.info('$ source ~/.profile')
