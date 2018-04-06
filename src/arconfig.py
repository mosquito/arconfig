#!/usr/bin/env python
# encoding: utf-8

import argparse
import json
import sys
import re


def build_config(parser, ns):

    config = {}

    def default_or_value(ns, dest, default):
        if default is argparse.SUPPRESS:
            default = None
        if hasattr(ns, dest):
            val = getattr(ns, dest, default)
            return val if val else default
        else:
            return default

    def resolver(arg, ns):
        if isinstance(arg, (argparse._HelpAction, argparse._VersionAction, GenConfigAction, LoadConfigAction)):
            pass
        elif isinstance(arg, (argparse._AppendAction, argparse._AppendConstAction)):
            if arg.dest not in config:
                config[arg.dest] = list()
            elif isinstance(arg, argparse._AppendConstAction):
                config[arg.dest].append(arg.const)
            else:
                config[arg.dest].append(default_or_value(ns, arg.dest, arg.default))
        else:
            config[arg.dest] = default_or_value(ns, arg.dest, arg.default)

    for o in parser._actions:
        if isinstance(o, argparse._SubParsersAction):
            config[o.dest] = {}
            for k, s in o.choices.items():
                config[o.dest][k] = build_config(s, ns)
        else:
            resolver(o, ns)

    return config


class GenConfigAction(argparse.Action):

    def __init__(self, option_strings, dest, default=False, required=False, help=None):
        super(self.__class__, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=True,
            default=default,
            required=required,
            help="Create example of the config_file.json"
        )

        self._config = {}

    def __call__(self, parser, ns, *args, **kwargs):
        config = build_config(parser, ns)
        print(json.dumps(config, indent=True, sort_keys=True))
        parser.exit()


ARGV = set(filter(lambda x: re.match('^[\w\.]+$', x), sys.argv[1:]))


def config_loader(cfg, namespace, type_map):

    for key, val in cfg.items():

        if isinstance(val, dict):
            try:
                k = (set(val.keys()) & ARGV)
                if k:
                    _key = k.pop()
                    setattr(namespace, key, _key)
                    config_loader(val[_key], namespace, type_map[key][_key])
            except KeyError:
                pass
        elif val is not None:
            vtype = type_map.get(key)
            setattr(namespace, key, vtype(val) if vtype else val)


def type_gen(parser, type_map):

    for action in parser._actions:

        if isinstance(action, (argparse._HelpAction, argparse._VersionAction, GenConfigAction, LoadConfigAction)):
            pass
        elif isinstance(action, (argparse._AppendAction, argparse._AppendConstAction)):
            pass
        elif isinstance(action, (argparse._StoreFalseAction, argparse._StoreTrueAction)):
            type_map[action.dest] = bool
        elif isinstance(action, (argparse._SubParsersAction,)):
            for key, parser in action.choices.items():
                if action.dest not in type_map:
                    type_map[action.dest] = {}
                type_map[action.dest][key] = type_gen(parser, dict())
        else:
            type_map[action.dest] = action.type if action.type else str

    return type_map


class LoadConfigAction(argparse._StoreAction):
    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest, **kwargs)
        self.help = "Load configuration from file"

    def __call__(self, parser, namespace, values, option_string=None):
        type_map = type_gen(parser, dict())
        config_loader(json.load(open(values)), namespace, type_map)
        return


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--gen-config", action=GenConfigAction)
    parser.add_argument("--config", action=LoadConfigAction)

    parser.add_argument('-s', action='store', dest='simple_value',
                        help='Store a simple value')
    parser.add_argument('-c', action='store_const', dest='constant_value', const='value-to-store',
                        help='Store a constant value')
    parser.add_argument('-t', action='store_true', default=False, dest='boolean_switch',
                        help='Set a switch to true')
    parser.add_argument('-f', action='store_false', default=False, dest='boolean_switch',
                        help='Set a switch to false')
    parser.add_argument('-a', action='append', dest='collection', default=[],
                        help='Add repeated values to a list')
    parser.add_argument('-A', action='append_const', dest='const_collection', const='value-1-to-append', default=[],
                        help='Add different values to list')
    parser.add_argument('-B', action='append_const', dest='const_collection', const='value-2-to-append',
                        help='Add different values to list')
    parser.add_argument('-z', action='count', dest='test_count')

    group = parser.add_argument_group("Test")
    group.add_argument('-C', action='append_const', dest='const_collection', const='value-1-to-append', default=[],
                       help='Add different values to list')
    group.add_argument('-D', action='append_const', dest='const_collection', const='value-2-to-append',
                       help='Add different values to list')
    group.add_argument('-v', action='count', dest='test_count1')

    options = parser.parse_args()

    print(json.dumps(options.__dict__, indent=1, sort_keys=True))
