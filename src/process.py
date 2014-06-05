# -*- coding: utf-8 -*-
import os
import subprocess
import signal


def _subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def sudo(*cmd, **kwargs):
    kwargs['run_as_root'] = True
    return execute(*cmd, **kwargs)

def execute(*cmd, **kwargs):
    """Helper method to execute command with optional retry.

    If you add a run_as_root=True command, don't forget to add the
    corresponding filter to etc/nova/rootwrap.d !

    :param cmd:                Passed to subprocess.Popen.
    :param process_input:      Send to opened process.
    :param ignore_exit_code:   Ignore exit code.
    :param check_exit_code:    Single bool, int, or list of allowed exit
                               codes.  Defaults to [0].  Raise
                               exception.ProcessExecutionError unless
                               program exits with one of these code.
    :param delay_on_retry:     True | False. Defaults to True. If set to
                               True, wait a short amount of time
                               before retrying.
    :param attempts:           How many times to retry cmd.
    :param run_as_root:        True | False. Defaults to False. If set to True,
                               the command is run with rootwrap.

    :raises exception.ProcessExecutionError:

    :returns: a tuple, (stdout, stderr) from the spawned process, or None if
             the command fails.
    """
    process_input = kwargs.pop('process_input', None)
    check_exit_code = kwargs.pop('check_exit_code', [0])
    ignore_exit_code = kwargs.pop('ignore_exit_code', [0])
    if isinstance(check_exit_code, bool):
        ignore_exit_code = not check_exit_code
        check_exit_code = [0]
    elif isinstance(check_exit_code, int):
        check_exit_code = [check_exit_code]
    #delay_on_retry = kwargs.pop('delay_on_retry', True)
    attempts = kwargs.pop('attempts', 1)
    run_as_root = kwargs.pop('run_as_root', False)
    shell = kwargs.pop('shell', False)

    if len(kwargs):
        raise Exception('Got unknown keyword args '
                        'to utils.execute: %r' % kwargs)

    if run_as_root and os.geteuid() != 0:
        cmd = ['sudo'] + list(cmd)

    cmd = map(str, cmd)

    while attempts > 0:
        attempts -= 1
        try:
            _PIPE = subprocess.PIPE  # pylint: disable=E1101

            if os.name == 'nt':
                preexec_fn = None
                close_fds = False
            else:
                preexec_fn = _subprocess_setup
                close_fds = True

            obj = subprocess.Popen(cmd,
                                   stdin=_PIPE,
                                   stdout=_PIPE,
                                   stderr=_PIPE,
                                   close_fds=close_fds,
                                   preexec_fn=preexec_fn,
                                   shell=shell)
            result = None
            if process_input is not None:
                result = obj.communicate(process_input)
            else:
                result = obj.communicate()
            obj.stdin.close()  # pylint: disable=E1101
            _returncode = obj.returncode  # pylint: disable=E1101
            if not ignore_exit_code and _returncode not in check_exit_code:
                (stdout, stderr) = result
                raise Exception('{0}, {1}'.format(stdout, stderr))
            return result
        except:
            raise 
        finally:
            pass

