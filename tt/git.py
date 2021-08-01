import os
import re
import subprocess

VERSION_PAT = re.compile(r'.*git\s+version\s+(\d+)[.](\d+)(?:[.](\d+))?\s*')
GIT_ENV = {'GIT_TERMINAL_PROMPT': '0'}
SAFE_CWD = os.path.expanduser('~')


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


def safecwd():
    try:
        return os.getcwd()
    except:
        # Git won't run if cwd is invalid. Set cwd to something that should always exist.
        cwd = SAFE_CWD
        os.chdir(cwd)
        return cwd


def clone(remote, local):
    oldcwd = safecwd()
    os.chdir(SAFE_CWD)
    try:
        if os.path.exists(local):
            raise Exception('Path %s already exists.' % local)
        run_git(['clone', remote, local])
    finally:
        os.chdir(oldcwd)


def pull(local):
    if not os.path.isdir(os.path.join(local, '.git')):
        raise Exception('Path %s does not exist or is not a git repo.')
    oldcwd = os.getcwd()
    os.chdir(local)
    try:
        proc = run_git(['pull', '--ff-only'])
    finally:
        os.chdir(oldcwd)


def get_history(path):
    oldcwd = os.getcwd()
    folder, fname = os.path.split(path)
    os.chdir(folder)
    try:
        proc = run_git(['log', "--pretty=%h,%an,%at", fname])
        return proc.stdout.decode('utf-8').strip().split('\n')
    finally:
        os.chdir(oldcwd)


if __name__ == '__main__':
    clone('https://github.com/dhh1128/tt.git', '/Users/dhardman/code/tt2')
    pull('/Users/dhardman/code/tt2')