from kubepi.cli import pass_environment, logger
from kubepi.helpers.git import get_submodules, get_repo
from kubepi.type import semver

import click
import click_spinner
import git
import os
import subprocess as s

# App group of commands


@click.group('platform', short_help='Platform commands')
@click.pass_context
@pass_environment
def cli(ctx, kube_context):
    """Platform commands to help with handling the codebase and repo"""
    pass


@cli.command('init', short_help='Initialize platform components')
@click.argument('submodules',
                required=True,
                default='all')
@click.argument('repopath',
                required=True,
                type=click.Path(exists=True),
                default=os.getcwd())
@click.pass_context
@pass_environment
def init(ctx, kube_context, submodules, repopath):
    """Init the platform by doing submodule init and checkout
    all submodules on master"""

    # Get the repo from arguments defaults to cwd
    repo = get_repo(repopath)
    submodules = get_submodules(repo, submodules)

    with click_spinner.spinner():
        repo.submodule_update()
    logger.info('Platform initialized.')


@cli.command('info', short_help='Get info on platform')
@click.pass_context
@pass_environment
def info(ctx, kube_context):
    """Get info on platform and platform components"""
    kube_context = ctx.kube_context

    try:
        gw_url = s.run(['kubectl',
                        '--context',
                        'k3d-' + kube_context,
                        '-n',
                        'traefik',
                        'get',
                        'service',
                        'traefik',
                        '-o',
                        'jsonpath={.status.loadBalancer.ingress[0].ip}'],
                       capture_output=True, check=True)
        logger.info('Platform can be accessed through the URL:')
        logger.info('http://' + gw_url.stdout.decode('utf-8'))
    except s.CalledProcessError as error:
        logger.debug(error.stderr.decode('utf-8'))
        raise click.Abort()


@cli.command('token', short_help='Get the platform token')
@click.pass_context
@pass_environment
def token(ctx, kube_context):
    """Get the platform token required by Kubernetes Dashboard"""
    kube_context = ctx.kube_context

    try:
        proc1 = s.Popen(['kubectl',
                         '--context',
                         'k3d-' + kube_context,
                         '-n',
                         'monitoring',
                         'describe',
                         'secret',
                         'k1s-admin'],
                        stdout=s.PIPE)
        proc2 = s.Popen(['grep', 'token:'],
                        stdin=proc1.stdout, stdout=s.PIPE, universal_newlines=True)
        proc1.stdout.close()
        out = proc2.communicate()[0]
        logger.info('The platform token is:\n')
        logger.info(out)
    except s.CalledProcessError as error:
        logger.debug(error.stderr.decode('utf-8'))
        raise click.Abort()


@cli.command('release', short_help='Make a platform release')
@click.argument('version',
                type=semver.BasedVersionParamType(),
                required=True)
@click.argument('submodules',
                required=True,
                default='all')
@click.argument('repopath',
                required=True,
                type=click.Path(exists=True),
                default=os.getcwd())
@click.pass_context
@pass_environment
def release(ctx, kube_context, version, submodules, repopath):
    """Release platform by tagging platform repo and
    tagging all individual components (git submodules)
    using their respective SHA that the submodules point at"""

    # Get the repo from arguments defaults to cwd
    repo = get_repo(repopath)
    submodules = get_submodules(repo, submodules)

    # TODO: Tag platform and all submodules at their respective SHAs
    pass

# TODO: beautify output, check if remotes are ahead, warn anti-pattern


@cli.command('version', short_help='Get all versions of components')
@click.argument('submodules',
                required=True,
                default='all')
@click.argument('repopath',
                required=True,
                type=click.Path(exists=True),
                default=os.getcwd())
@click.pass_context
@pass_environment
def version(ctx, kube_context, submodules, repopath):
    """Check versions of microservices in git submodules
    You can provide a comma separated list of submodules
    or you can use 'all' for all submodules"""

    # Get the repo from arguments defaults to cwd
    repo = get_repo(repopath)
    submodules = get_submodules(repo, submodules)

    # Do something with the submodules
    all_sm_details = []
    with click_spinner.spinner():
        for submodule in submodules:
            logger.debug('Switched to submodule: ' + submodule)
            sm_details = {}
            sm_details['repo'] = submodule
            # Are we on an active branch? on a tag? if not then get sha?
            try:
                smrepo = git.Repo(submodule)
                sm_details['present'] = True
            except git.InvalidGitRepositoryError as error:
                logger.warning(submodule + ': not present')
                sm_details['present'] = False
                all_sm_details.append(sm_details)
                continue

            # Get branch
            try:
                branch = smrepo.active_branch.name
                sm_details['branch'] = branch

                # Check if remotes are ahead or behind
                origin = smrepo.remotes.origin
                origin.fetch()
                commits_behind = smrepo.iter_commits(branch +
                                                     '..origin/' + branch)
                commits_ahead = smrepo.iter_commits('origin/' + branch +
                                                    '..' + branch)
                sm_details['commits_ahead'] = sum(1 for c in commits_ahead)
                sm_details['commits_behind'] = sum(1 for c in commits_behind)
            except TypeError as error:
                sm_details['branch'] = ''
                logger.debug(error)

            # Check if we point to any tags
            points_at_tag = smrepo.git.tag('--points-at', 'HEAD')
            sm_details['tag'] = points_at_tag

            # Get sha of HEAD
            sha = smrepo.head.commit.hexsha
            sm_details['sha'] = sha

            # Add submodule details to the list
            all_sm_details.append(sm_details)

    logger.debug('Received following details about the platform submodules:')
    logger.debug(all_sm_details)
    for sm_details in all_sm_details:
        logger.info(sm_details['repo'] + ':')
        logger.info(u'\u2023' + ' Branch: ' + sm_details['branch'])
        logger.info(u'\u2023' + ' SHA: ' + sm_details['sha'])
        if sm_details['tag']:
            logger.info(u'\u2023' + ' Tag: ' + sm_details['tag'])
        if sm_details['commits_ahead'] > 0:
            logger.info(u'\u2023' + ' Ahead by: ' +
                        str(sm_details['commits_ahead']) + ' commits')
        if sm_details['commits_behind'] > 0:
            logger.info(u'\u2023' + ' Behind by: ' +
                        str(sm_details['commits_behind']) + ' commits')
