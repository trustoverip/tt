import os
import re
import subprocess

VERSION_PAT = re.compile(r'.*git\s+version\s+(\d+)[.](\d+)(?:[.](\d+))?\s*')
GIT_ENV = {'GIT_TERMINAL_PROMPT': '0'}


def is_installed():
    proc = subprocess.run(['git', '--version'], capture_output=True)
    return str(proc.stdout) if proc.returncode == 0 else None


def run_git(args):
    cmd = ['git'] + args
    proc = subprocess.run(cmd, env=GIT_ENV, capture_output=True)
    if proc.returncode:
        print("Command \"git %s\" failed with exit code %d." % (' '.join(args), proc.returncode))
        raise Exception(proc.stderr.decode('utf-8'))
    return proc


def clone(remote, local):
    if os.path.exists(local):
        raise Exception('Path %s already exists.' % local)
    run_git(['clone', remote, local])


def pull(local):
    if not os.path.isdir(os.path.join(local, '.git')):
        raise Exception('Path %s does not exist or is not a git repo.')
    curdir = os.getcwd()
    os.chdir(local)
    try:
        proc = run_git(['pull', '--ff-only'])
    finally:
        os.chdir(curdir)


if __name__ == '__main__':
    clone('https://github.com/dhh1128/tt.git', '/Users/dhardman/code/tt2')
    pull('/Users/dhardman/code/tt2')