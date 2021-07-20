from .commands import syntax


def match_command(argv):
    return syntax.cmd


def main(argv = None):
    if not argv:
        import sys
        argv = sys.argv
    try:
        cmd = match_command(argv[1])
    except:
        cmd = syntax.cmd
    cmd(argv[2:])


if __name__ == '__main__':
    main()