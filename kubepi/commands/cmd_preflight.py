from kubepi.cli import pass_environment, logger

import click
import subprocess as s


@click.command('preflight', short_help='Preflight checks')
@click.pass_context
@pass_environment
def cli(ctx, kube_context):
    """Preflight checks to ensure all tools and versions are present"""
    # Check go
    try:
        go_ver = s.run(['go', 'version'],
                       capture_output=True, check=True)
        logger.info('Found go.')
        logger.debug(go_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('go not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('go version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check docker
    try:
        docker_ps = s.run(['docker', 'ps'],
                          capture_output=True, check=True)
        logger.info('Found docker.')
        logger.debug(docker_ps.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('docker not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('`docker ps` returned something unexpected: ' +
                        error.stderr.decode('utf-8'))
        logger.critical('Please ensure the docker daemon is running and that '
                        'your user is part of the docker group. See README')

    # Check helm 3
    try:
        helm_ver = s.run(['helm', 'version', '--short'],
                         capture_output=True, check=True)
        # Check that we have helm 3
        if helm_ver.stdout.decode('utf-8')[1] != "3":
            logger.error(
                'Old version of helm detected when running "helm" from PATH.')
        else:
            logger.info('Found helm.')
            logger.debug(helm_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('helm not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('helm version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check k3d
    try:
        k3d_ver = s.run(['k3d', 'version'],
                        capture_output=True, check=True)
        logger.info('Found k3d.')
        logger.debug(k3d_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('k3d not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('k3d version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check skaffold
    try:
        skaffold_ver = s.run(['skaffold', 'version'],
                             capture_output=True, check=True)
        logger.info('Found skaffold.')
        logger.debug(skaffold_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('skaffold not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('skaffold version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check kubectl
    try:
        kubectl_ver = s.run(['kubectl', 'version', '--client=true'],
                            capture_output=True, check=True)
        logger.info('Found kubectl.')
        logger.debug(kubectl_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('kubectl not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('kubectl version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))
