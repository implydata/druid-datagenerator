## Generation configuration

Configuration files define how the data generator will produce data.

In command-line mode, the configuration file is specified in the command line using the `-c` argument.

Configuration files are stored the `config_file` folder.

| Object | Description |
|---|---|
| [`emitters`](./config-emitters.md) | A list of emitters for this configuration. |
| [`interarrival`](./config-interarrival.md) | Sets the period of time that elapses between one event being generated and the next. |
| [`states`](./config-states.md) | A list of states associated with each emitter. |

It is not possible to set the `target` in the generation configuration file. Instead, use the `-o` argument and create a separate [target](#./target.md) configuration file.