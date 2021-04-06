import functools
import argparse
import yaml

from submodule_utils.arguments import AIMArgumentParser
from submodule_utils.manifest.experiment import ExperimentManifest

def walk_experiment_manifest(data):
    """Convert dict extracted from YAML into a raw arguments to pass into argparse.ArgumentParser.parse_args()

    Parameters
    ----------
    data : dict
        dict extracted from YAML manifest.

    Returns
    -------
    list of str
        Raw arguments to pass into argparse.ArgumentParser.parse_args()
    """
    items = list(data.items())
    items.sort(key=lambda item: 1 if isinstance(item[1], dict) else 0)
    args = [ ]
    for key, value in items:
        if isinstance(value, dict):
            """key-value specifies a subcommand argument
            """
            args.append(key)
            args.extend(walk_experiment_manifest(value))
        else:
            """key specifies a -k if key only has one letter (i.e. key == k) or --key otherwise. 
            """
            if len(key) == 1:
                """Add one letter argument -k
                """
                args.append(f"-{key}")
            else:
                """Add a multi-letter argument --key
                """
                args.append(f"--{key}")
            if isinstance(value, list):
                """Argument has a list of values
                """
                args.extend(map(str, value))
            elif value is None:
                """Argument does not have a value.
                """
                pass
            else:
                """Argument has a single value.
                """
                args.append(str(value))
    return args


class AIMManifestArgumentManager(object):
    """Decorator class to use on a create_parser() function to create a manager for receiving arguments from command line and the experiment manifest.

    Attributes
    ----------
    create_parser : function
        Function that adds arguments, argument groups, subparsers, ...etc to argparse.ArgumentParser

    description : str
        The description to use in argparse.ArgumentParser

    epilog : epilog
        The epilog to use in argparse.ArgumentParser

    default_component_id : str
        The default component ID to search for when reading experiment manifest.
    """

    def __init__(self, create_parser,
            default_component_id=None, description=None, epilog=None):
        self.create_parser = create_parser
        self.description = description
        self.epilog = epilog
        self.default_component_id = default_component_id

    def get_experiment_manifest_args(self, experiment_manifest_file, component_id):
        """Get arguments from a manifest file.

        Parameters
        ----------
        experiment_manifest_file : str
            Path to experiment manifest YAML file.
        
        Returns
        -------
        argparse.Namespace
            The arguments
        """
        parser = argparse.ArgumentParser(description=self.description, epilog=self.epilog)
        self.create_parser(parser)
        experiment_manifest = ExperimentManifest(experiment_manifest_file)
        component_manifest = experiment_manifest.get_component_config(component_id)
        raw_args = walk_experiment_manifest(component_manifest)
        args, unparsed = parser.parse_known_args(raw_args)
        return args

    def get_cmdline_args(self, argv=None):
        """Get arguments from a command line.

        Returns
        -------
        argparse.Namespace
            The arguments
        """
        parser = AIMArgumentParser(description=self.description, epilog=self.epilog)
        subparsers_config = parser.add_subparsers(dest='config_method',
                required=True,
                parser_class=AIMArgumentParser,
                help="Choose whether to use arguments from experiment manifest or from commandline")

        parser_experiment_manifest = subparsers_config.add_parser("from-experiment-manifest",
                help="Use experiment manifest")
        parser_experiment_manifest.add_argument('experiment_manifest_location')
        parser_experiment_manifest.add_argument("--component_id", type=str,
                default=self.default_component_id)

        parser_arguments = subparsers_config.add_parser("from-arguments",
                help="Use arguments")

        self.create_parser(parser_arguments)
        if argv:
            args, unparsed = parser.parse_known_args(argv)
        else:
            args, unparsed = parser.parse_known_args()
        return args
    
    def get_args(self, argv=None):
        """Either gets arguments from the command line, or reads arguments from provided manifest file if from-experiment-manifest is specified from the command line.

        Returns
        -------
        argparse.Namespace
            The arguments
        """
        if argv:
            args = self.get_cmdline_args(argv=argv)
        else:
            args = self.get_cmdline_args()
        if args.config_method == 'from-experiment-manifest':
            if args.component_id:
                return self.get_experiment_manifest_args(
                        args.experiment_manifest_location, args.component_id)
            else:
                raise Exception('neither default_component_id or component_id is provided')
        else:
            return args

class manifest_arguments(object):
    """Decorator class to use on a create_parser() function to create a manager for receiving arguments from command line and the experiment manifest.

    How to use: in your component's entry point create a create_parser() function with manifest_arguments() as a decorator like so:

    ```
    @manifest_arguments(description=description, epilog=epilog)
    def create_parser(parser):
        parser.add_argument('--foo', action='store_true')
        parser.add_argument('--bar', type=str, required=True)
        ....
    ```

    Then calling create_parser() will return an AIMArgumentManager instance which acts like a argparse.ArgumentParser factory allowing you to specify the source of the arguments. In addition to adding the arguments specified inside create_parser(), it adds the subcommands 'from-arguments' and 'from-experiment-manifest'.

    ```
    parser = create_parser()
    config = parser.get_args()
    ```

    If app.py is the entrypoint to your component and you want to you commandline arguments, then you can use the subcommand 'from-arguments' like so.

    ```
    python app.py from-arguments --foo --bar baz
    ```

    If app.py is the entrypoint to your component, your component is named 'try_me', and you want to use arguments from a manifest YAML file at /path/to/experiments.yaml with contents like the below.

    ```
    ---
    try_me:
        foo: ~
        bar: baz
    ```

    Then you can use the subcommand 'from-experiment-manifest' like so.

    ```
    python app.py from-experiment-manifest /path/to/experiments.yaml  --component_id try_me
    ```
    """
    def __init__(self, default_component_id=None, description=None, epilog=None):
        self.default_component_id = default_component_id
        self.description = description
        self.epilog = epilog

    def __call__(self, create_parser):
        def wrapper():
            return AIMManifestArgumentManager(create_parser,
                    default_component_id=self.default_component_id,
                    description=self.description, epilog=self.epilog)
        return functools.update_wrapper(wrapper, create_parser)
