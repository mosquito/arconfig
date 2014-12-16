#!/usr/bin/env python
# encoding: utf-8

import argparse
import json


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

    def _default_or_value(self, ns, dest, default):
        if getattr(ns, dest, None):
            val = getattr(ns, dest)
            return val if val else default
        else:
            return default

    def resolver(self, arg, ns):
        if isinstance(arg, (argparse._HelpAction, argparse._VersionAction, self.__class__, GenConfigAction, LoadConfigAction)):
            pass
        elif isinstance(arg, (argparse._AppendAction, argparse._AppendConstAction)):
            if arg.dest not in self._config:
                self._config[arg.dest] = list()

            if isinstance(arg, argparse._AppendConstAction):
                self._config[arg.dest].append(arg.const)
            else:
                self._config[arg.dest].append(self._default_or_value(ns, arg.dest, arg.default))
        elif isinstance(arg, (argparse._SubParsersAction)):
            pass
        else:
            self._config[arg.dest] = self._default_or_value(ns, arg.dest, arg.default)


    def __call__(self, parser, ns, *args, **kwargs):
        for o in parser._actions:
            self.resolver(o, ns)

        print json.dumps(self._config, indent=True, encoding='utf-8', sort_keys=True)
        parser.exit()


class LoadConfigAction(argparse._StoreAction):
    def __init__(self, option_strings, dest):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "Load configuration from file"

    def __call__(self, parser, namespace, values, option_string=None):
        cfg = json.load(open(values, "rb"))
        for key, val in cfg.items():
            setattr(namespace, key, val)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gen-config", action=GenConfigAction)
    parser.add_argument("--config", action=LoadConfigAction)

    parser.add_argument('-s', action='store', dest='simple_value', help='Store a simple value')
    parser.add_argument('-c', action='store_const', dest='constant_value', const='value-to-store', help='Store a constant value')
    parser.add_argument('-t', action='store_true', default=False, dest='boolean_switch', help='Set a switch to true')
    parser.add_argument('-f', action='store_false', default=False, dest='boolean_switch', help='Set a switch to false')
    parser.add_argument('-a', action='append', dest='collection', default=[], help='Add repeated values to a list')
    parser.add_argument('-A', action='append_const', dest='const_collection', const='value-1-to-append', default=[], help='Add different values to list')
    parser.add_argument('-B', action='append_const', dest='const_collection', const='value-2-to-append', help='Add different values to list')
    parser.add_argument('-z', action='count', dest='test_count')

    group = parser.add_argument_group("Test")
    group.add_argument('-C', action='append_const', dest='const_collection', const='value-1-to-append', default=[], help='Add different values to list')
    group.add_argument('-D', action='append_const', dest='const_collection', const='value-2-to-append', help='Add different values to list')
    group.add_argument('-v', action='count', dest='test_count1')

    options = parser.parse_args()

    print json.dumps(options.__dict__, indent=1, sort_keys=True)
