"""
Install:
  pipenv install --dev

Usage:
  make.py [<command>] [options]
  make.py -h | --help

Commands:
  build       Create wheel.
  deploy      Publish on pypi.
  test        Run tests.
  bump        Run interactive deployment sequence.
  git         Run interactive git sequence.

Options:
  -h, --help  Show this screen.
"""
import subprocess as sp
from cmdi import print_summary
from buildlib import buildmisc, git, wheel, project, yaml
from docopt import docopt

proj = yaml.loadfile('Project')


class Cfg:
    version = proj['version']
    registry = 'pypi'


def build(cfg: Cfg):
    return wheel.cmd.build(clean_dir=True)


def deploy(cfg: Cfg):
    return wheel.cmd.push(clean_dir=True, repository=cfg.registry)


def test(cfg: Cfg):
    sp.run(['python', '-m', 'tests'])


def bump(cfg: Cfg):
    results = []

    if project.prompt.should_bump_version():
        result = project.cmd.bump_version()
        cfg.version = result.val
        results.append(result)

    if wheel.prompt.should_push('PYPI'):
        results.append(deploy(cfg))

    new_release = cfg.version != proj['version']

    results.extend(git.seq.bump_git(cfg.version, new_release))

    return results


def run():

    cfg = Cfg()
    args = docopt(__doc__)
    results = []

    if args["<command>"] == 'build':
        results.append(build(cfg))

    elif args["<command>"] == 'deploy':
        results.append(deploy(cfg))

    elif args["<command>"] == 'test':
        test(cfg)

    elif args["<command>"] == 'git':
        results.append(git.seq.bump_git(cfg.version, new_release=False))

    elif args["<command>"] == 'bump':
        results.extend(bump(cfg))

    if not args["<command>"]:
        print(__doc__)
    else:
        print_summary(results)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('\n\nScript aborted by user.')
