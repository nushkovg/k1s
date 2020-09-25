from kubepi.cli import pass_environment, logger
from kubepi.helpers import k3d, kube

import click
import click_spinner
import subprocess as s
import docker
from time import sleep

# K3D group of commands


@click.group('k3d', short_help='Manage k3d clusters')
@click.pass_context
@pass_environment
def cli(ctx, kube_context):
    """Manage k3d clusters.
    The name of the cluster is taken from the option --kube-context
    which defaults to 'k1s'"""
    pass


@cli.command('create', short_help='Create cluster')
@click.pass_context
@pass_environment
def create(ctx, kube_context):
    """Create a k3d cluster"""
    # Check if k3d cluster is already created
    kube_context = ctx.kube_context
    if k3d.k3d_get(kube_context):
        logger.error('K3D cluster \'' + kube_context + '\' already exists')
        raise click.Abort()

    # Create the k3d cluster
    try:
        logger.debug('Running: `k3d cluster create`')
        create_cluster = s.run(['k3d',
                                'cluster',
                                'create',
                                '--k3s-server-arg',
                                '--no-deploy=traefik',
                                '--port',
                                '80:80@loadbalancer',
                                '--port',
                                '443:443@loadbalancer',
                                '--port',
                                '8080:8080@loadbalancer',
                                kube_context],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not create k3d cluster' +
                        error.stderr.decode('utf-8'))

    # Create required namespaces
    namespaces = [kube_context, 'traefik', 'monitoring']

    for ns in namespaces:
        ns_exists = s.run(['kubectl',
                        'get',
                        'ns',
                        ns,
                        '--context',
                        'k3d-' + kube_context],
                        capture_output=True)
        if ns_exists.returncode != 0:
            try:
                app_ns = s.run(['kubectl',
                                'create',
                                'ns',
                                ns,
                                '--context',
                                'k3d-' + kube_context],
                            check=True, stdout=s.DEVNULL)
            except s.CalledProcessError as error:
                logger.error('Something went wrong with namespace: ' +
                            error.stderr.decode('utf-8'))
                raise click.Abort()
        else:
            logger.info('Skipping creation of ' + ns + ' namespace '
                        'since it already exists.')

    # Apply traefik CRD definitions
    try:
        crd_path = 'infrastructure/k1s-traefik/manifests/001-crds.yaml'
        logger.debug('Running: `kubectl apply -f {}`'.format(crd_path))
        create_cluster = s.run(['kubectl',
                                'apply',
                                '-f',
                                crd_path],
                               check=True, stdout=s.DEVNULL)
    except s.CalledProcessError as error:
        logger.critical('Could not apply traefik CRDs' +
                        error.stderr.decode('utf-8'))


@cli.command('delete', short_help='Delete cluster')
@click.pass_context
@pass_environment
def delete(ctx, kube_context):
    """Delete a k3d cluster"""
    # Check if the k3d cluster exists
    kube_context = ctx.kube_context
    if not k3d.k3d_get(kube_context):
        logger.error('K3D cluster \'' + kube_context + '\' doesn\'t exist')
        raise click.Abort()

    # Delete the k3d cluster
    try:
        logger.debug('Running: `k3d cluster delete`')
        create_cluster = s.run(['k3d',
                                'cluster',
                                'delete',
                                kube_context],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not delete k3d cluster' +
                        error.stderr.decode('utf-8'))


@cli.command('status', short_help='Cluster status')
@click.pass_context
@pass_environment
def status(ctx, kube_context):
    """Check the status of the k3d cluster"""
    # Check if the cluster exists
    kube_context = ctx.kube_context
    if k3d.k3d_get(kube_context):
        if kube.kubectl_info(kube_context):
            logger.info('K3D cluster \'' + kube_context + '\' is running')
        else:
            logger.error('Cluster not running. Please start the cluster')
            raise click.Abort()
    else:
        logger.error('K3D cluster \'' + kube_context + '\' does not exist.')


@cli.command('start', short_help='Start cluster')
@click.pass_context
@pass_environment
def start(ctx, kube_context):
    """Start k3d cluster"""
    # Check the cluster status
    kube_context = ctx.kube_context
    if k3d.k3d_get(kube_context):
        if kube.kubectl_info(kube_context):
            logger.info('K3D cluster \'' + kube_context +
                        '\' is already running')
            raise click.Abort()
    elif not k3d.k3d_get(kube_context):
        logger.error('K3D cluster \'' + kube_context + '\' doesn\'t exist')
        raise click.Abort()

    # Start the k3d cluster
    try:
        logger.debug('Running: `k3d cluster start`')
        create_cluster = s.run(['k3d',
                                'cluster',
                                'start',
                                kube_context],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not start k3d cluster' +
                        error.stderr.decode('utf-8'))


@cli.command('stop', short_help='Stop cluster')
@click.pass_context
@pass_environment
def stop(ctx, kube_context):
    """Stop k3d cluster"""
    # Check the cluster status
    kube_context = ctx.kube_context
    if k3d.k3d_get(kube_context):
        if not kube.kubectl_info(kube_context):
            logger.info('K3D cluster \'' + kube_context +
                        '\' is already stopped')
            raise click.Abort()
    elif not k3d.k3d_get(kube_context):
        logger.error('K3D cluster \'' + kube_context + '\' doesn\'t exist')
        raise click.Abort()

    # Stop the k3d cluster
    try:
        logger.debug('Running: `k3d cluster stop`')
        create_cluster = s.run(['k3d',
                                'cluster',
                                'stop',
                                kube_context],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not stop k3d cluster' +
                        error.stderr.decode('utf-8'))
