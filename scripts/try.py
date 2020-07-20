import argparse

def dict_vals(kv):
    try:
        k, v = kv.split("=")
    except:
        raise argparse.ArgumentTypeError(f"value {kv} is not separated by one '='")
    try:
        v = int(v)
    except:
        raise argparse.ArgumentTypeError(f"right side of {kv} should be int")
    return (k, v)

def make_subtype_dict(ll):
    return {k: v for (k, v) in ll}

parser = argparse.ArgumentParser()
parser.add_argument("--subtypes", nargs='+', type=dict_vals,
        default=[['MMRD', 0], ['P53ABN', 1], ['P53WT', 2], ['POLE', 3]],
        help="space separated words describing subtype=groupping pairs for this study. "
        "Example: if doing one-vs-rest on the subtypes MMRD vs P53ABN, P53WT and POLE then "
        "the input should be 'MMRD=0 P53ABN=1 P53WT=1 POLE=1'")
parser.add_argument('--myint', type=int, choices=[0, 1, 2])

args = parser.parse_args()
print(args.subtypes)
print(args.myint)
print(make_subtype_dict(args.subtypes))
