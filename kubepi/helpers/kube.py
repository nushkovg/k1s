from kubepi.cli import logger

import click
import subprocess as s


def kubectl_info(cluster):
    # Get kubectl cluster-info
    try:
        logger.debug('Running: `kubectl cluster-info`')
        result = s.run(['kubectl',
                        'cluster-info',
                        '--context',
                        'k3d-' + cluster],
                       capture_output=True, check=True)
        logger.debug(result.stdout.decode('utf-8'))
        return True
    except s.CalledProcessError as error:
        logger.debug(error.stderr.decode('utf-8'))
        return False
