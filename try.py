import argparse
from submodule_utils.manifest.arguments import manifest_arguments

@manifest_arguments(default_component_id="try_me")
def create_parser(parser):
    parser.add_argument("--baz", action='store_true')
    subparsers = parser.add_subparsers(dest="subparser", required=True)
    parser_print = subparsers.add_parser("printout")
    parser_print.add_argument("--say", type=str, required=True)

    parser_log = subparsers.add_parser("write-to-log")
    parser_log.add_argument("--log_location", type=str, required=True)
    parser_log.add_argument("--say", type=str, required=True)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.get_args()
    if args.subparser == "write-to-log":
        print(args.log_location)
        print(args.say)
    if args.subparser == "printout":
        print(args.say)