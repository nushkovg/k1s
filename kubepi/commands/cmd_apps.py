from kubepi.cli import pass_environment, logger

import click
import subprocess as s

# App group of commands


@click.group('apps', short_help='App commands')
@click.pass_context
@pass_environment
def cli(ctx, kube_context):
    """Application specific commands such as creation of kubernetes
    objects such as namespaces, configmaps etc. The name of the
    context is taken from the option --kube-context
    which defaults to 'k1s'"""
    pass


# Namespace setup
@cli.command('namespace', short_help='Create namespace')
@click.argument('name',
                required=True)
@click.pass_context
@pass_environment
def ns(ctx, kube_context, name):
    """Create a namespace"""
    kube_context = ctx.kube_context

    # Create a namespace in kubernetes
    ns_exists = s.run(['kubectl',
                       'get',
                       'ns',
                       name,
                       '--context',
                       'k3d-' + kube_context],
                      capture_output=True)
    if ns_exists.returncode != 0:
        try:
            app_ns = s.run(['kubectl',
                            'create',
                            'ns',
                            name,
                            '--context',
                            'k3d-' + kube_context],
                           capture_output=True, check=True)
            logger.info('Created a namespace for ' + name)
        except s.CalledProcessError as error:
            logger.error('Something went wrong with namespace: ' +
                         error.stderr.decode('utf-8'))
            raise click.Abort()
    else:
        logger.info('Skipping creation of ' + name + ' namespace '
                    'since it already exists.')
