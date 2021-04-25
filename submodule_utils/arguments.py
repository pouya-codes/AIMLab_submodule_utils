import functools
import argparse
import os
import yaml

from submodule_utils import DATASET_ORIGINS, BALANCE_PATCHES_OPTIONS

def dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        try:
            os.makedirs(s, exist_ok=True)
            return s
        except:
            raise argparse.ArgumentTypeError(f"readable_dir:{s} is not a valid path")

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError(f'{v} is not a Bollean value, boolean value expected.')

def file_path(s):
    if os.path.isfile(s):
        return s
    else:
        raise argparse.ArgumentTypeError(f"readable_file:{s} is not a valid path")

def output_file_path(s):
    try:
        os.makedirs(os.path.dirname(s), exist_ok=True)
        return s
    except:
        raise argparse.ArgumentTypeError(f"readable_file:{s} is not a valid path")

def positive_int(i):
    i = int(i)
    if i <= 0:
        raise argparse.ArgumentTypeError(f"{i} is an invalid positive int value")
    return i

def float_less_one(f):
    f = float(f)
    if f < 0.0 or f > 1.0:
        raise argparse.ArgumentTypeError(f"{f} should be in range 0 <= f <= 1")
    return f

def dataset_origin(s):
    if s.lower() in DATASET_ORIGINS:
        return s.lower()
    else:
        raise argparse.ArgumentTypeError(f"dataset type {s} has not been implemented")

def balance_patches_options(s):
    if '=' in s:
        k, v = s.split('=')
        if k.lower() in BALANCE_PATCHES_OPTIONS:
            return (k.lower(), int(v),)
        else:
            raise argparse.ArgumentTypeError(f'balance patches option {k} has not been implemented')
    if s.lower() in BALANCE_PATCHES_OPTIONS:
        return s.lower()
    else:
        raise argparse.ArgumentTypeError(f'balance patches option {s} has not been implemented')

def str_kv(kv):
    """Used to identify and convert key=value arguments into a tuple (key, value). Value stays as a str.
    This is to be passed as the type when calling argparse.ArgumentParser.add_argument()

    Parameters
    ----------
    kv: str
        a key=value argument

    Returns
    -------
    tuple
        (key, value) from key=value
    """
    try:
        k, v = kv.split("=")
    except:
        raise argparse.ArgumentTypeError(f"value {kv} is not separated by one '='")
    return (k, v)

def int_kv(kv):
    """Used to identify and convert key=value arguments into a tuple (key, int(value)). Value is converted into an int.
    This is to be passed as the type when calling argparse.ArgumentParser.add_argument()

    Parameters
    ----------
    kv: str
        a key=value argument

    Returns
    -------
    tuple
        (key, int(value)) from key=value
    """
    try:
        k, v = kv.split("=")
    except:
        raise argparse.ArgumentTypeError(f"value {kv} is not separated by one '='")
    try:
        v = int(v)
    except:
        raise argparse.ArgumentTypeError(f"right side of {kv} should be int")
    return (k, v)

def subtype_kv(kv):
    """Used to identify and convert key=value arguments into a tuple (key.upper(), int(value)).
    For example: MMRd=0 becomes (MMRD, int(0))
    This is to be passed as the type when calling argparse.ArgumentParser.add_argument()

    Parameters
    ----------
    kv: str
        a key=value argument

    Returns
    -------
    tuple
        (key.upper(), int(value)) from key=value
    """
    try:
        k, v = kv.split("=")
    except:
        raise argparse.ArgumentTypeError(f"value {kv} is not separated by one '='")
    k = k.upper()
    try:
        v = int(v)
    except:
        raise argparse.ArgumentTypeError(f"right side of {kv} should be int")
    return (k, v)

KV_TYPES = (str_kv, int_kv, subtype_kv)

def make_dict(ll):
    return {k: v for (k, v) in ll}

class ParseKVToDictAction(argparse.Action):
    """
    """
    def __init__(self, option_strings, dest, nargs=None, type=None, **kwargs):
        if nargs != '+':
            raise argparse.ArgumentTypeError(f"ParseKVToDictAction can only be used for arguments with nargs='+' but instead we have nargs={nargs}")
        if type not in KV_TYPES:
            raise argparse.ArgumentTypeError(f"ParseKVToDictAction can only be used for arguments with type=dict_str_vals or type=dict_num_vals but instead we have type={type}")
        super(ParseKVToDictAction, self).__init__(option_strings, dest,
                nargs=nargs, type=type, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, option_string.lstrip('-'), make_dict(values))

class CustomHelpFormatter(
        argparse.RawTextHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter):
    """
    TODO: trying to make help string look better
    """
    def add_argument(self, action):
        if action.help is not None:
            action.help += '\n'
        super().add_argument(action)

    def _format_action(self, action):
        s = super()._format_action(action)
        return s + '\n'

class AIMArgumentParser(argparse.ArgumentParser):
    """Modified argparse.ArgumentParser that uses CustomHelpFormatter
    """
    def __init__(self, *args, description=None, epilog=None, **kwargs):
        super().__init__(*args,
                formatter_class=CustomHelpFormatter,
                description=description, epilog=epilog, **kwargs)
