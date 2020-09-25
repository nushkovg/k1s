from kubepi.cli import logger
import click
import git


def get_repo(repopath):
    try:
        return git.Repo(repopath, odbt=git.GitDB)
    except git.InvalidGitRepositoryError:
        logger.critical('The repo path ' + repopath + ' is not a git repo')
        raise click.Abort()


def get_submodules(repo, submodules):
    # Based on provided submodules through arguments set the repo objects
    # that we want to work with
    if submodules == 'all':
        submodules = repo.submodules
        submodule_list = []
        for submodule in submodules:
            submodule_list.append(submodule.name)
        submodules = submodule_list
    else:
        submodules = submodules.split(',')
        submodule_list = []
        for submodule in submodules:
            submodule_list.append('platform/' + submodule)
        submodules = submodule_list
    logger.debug('The provided submodules are:')
    logger.debug(submodules)

    return(submodules)
