from kubepi.cli import logger

import click
import re
import subprocess as s


def k3d_get(cluster):
    # Get k3d clusters
    try:
        logger.debug('Running: `k3d cluster list`')
        result = s.run(['k3d', 'cluster', 'list'],
                       capture_output=True, check=True)
        k3d_clusters = result.stdout.decode('utf-8').splitlines()
        for cluster_info in k3d_clusters:
            found = re.findall('\\b{}\\b'.format(cluster), cluster_info)
            if found:
                return True
        # If cluster is not found
        return False
    except s.CalledProcessError as error:
        logger.critical(error.stderr.decode('utf-8'))
        raise click.Abort()
