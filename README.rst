Arconfig
========

Save/Load your options to/into config

.. code-block:: python

	>>> from arconfig import GenConfigAction, LoadConfigAction
	>>> parser = argparse.ArgumentParser()
	>>> parser.add_argument("--config", action=LoadConfigAction) # add it before another options
	>>> parser.add_argument("--gen-config", action=GenConfigAction)
	>>> parser.add_argument('-s', action='store', dest='simple_value', help='Store a simple value')
	>>> parser.add_argument('-c', action='store_const', dest='constant_value',
	... const='value-to-store', help='Store a constant value')
	>>> parser.add_argument('-t', action='store_true', default=False,
	... dest='boolean_switch', help='Set a switch to true')
	>>> parser.add_argument('-f', action='store_false', default=False,
	... dest='boolean_switch', help='Set a switch to false')

Generate simple config

.. code-block:: json

	$ python script.py --gen-config
	{
	 "simple_value": null,
	 "constant_value": null,
	 "config": null,
	 "boolean_switch": false
	}


And load it

.. code-block:: json

	$ python argparse_config.py --gen-config > /tmp/test.json
	$ python argparse_config.py --config=/tmp/test.json
	{
	 "simple_value": null,
	 "constant_value": null,
	 "config": null,
	 "gen_config": false,
	 "boolean_switch": false
	}


All another arguments overwrite the config values (but counter are added).
