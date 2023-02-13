#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dictator.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        env_check()
        exit(0)
    execute_from_command_line(sys.argv)


def env_check():
    print('Missing necessary packages, performing environment check...')
    try:
        env_setup()
    except ChildProcessError:
        print('Environment auto setup failed. You may try manually.')


def env_setup():
    from subprocess import Popen, PIPE
    win = os.name == 'nt'
    cwd = os.path.dirname(os.path.realpath(__file__))

    def path(*filename):
        sep = os.path.sep
        return cwd + sep + sep.join(filename)

    def venv(filename):
        if win:
            binary = path('venv', 'Scripts', f'{filename}.exe')
        else:
            binary = path('venv', 'bin', filename)
        return binary

    def handle_process(command, msg, error_msg):
        print(msg)
        process = Popen(command, cwd=cwd, stdout=PIPE, shell=True)
        output, _ = process.communicate()
        decoded = output.decode('utf-8')

        if process.poll():
            print(decoded)
            print('ERROR: ' + error_msg)
            raise ChildProcessError()

    # create virtual environment
    if not os.path.exists(venv('python')):
        print('Creating Virtual Environment...')
        from venv import create
        create(env_dir=path('venv'), system_site_packages=False, with_pip=True, clear=True)

    # try installing required packages
    handle_process(
        [venv('pip'), 'install', '-r', path('requirements.txt')],
        "Installing required packages...",
        "Unable to install required packages. Abort."
    )
    args = [venv('python'), 'manage.py'] + sys.argv[1:]
    print('\nVirtual environment has been set up.')
    print("Note: Please use '" + ' '.join(args) + "' to proceed.")


if __name__ == '__main__':
    main()
