## Generation configuration

Control the behavior of the data generator using a JSON configuration object.

The `config_file` folder contains a number of [examples](../config_file/examples) of configuration files.

If you are using the generator from the command-line, store the configuration in a file inside `config_file` folder, and reference it by name in the `-c` argument.

In this example, the `generator_config.json` file has been stored inside the `config_file` folder. The following command is then run from the command line in the repo root. Note that the `-c` argument excludes the `config_file` folder name as it is relative.

```
python generator/DruidDataDriver.py -c config.json -o target.json -t 5M
```

Do not mix generator configuration and [generator targets](./target.md). From the command line, use the `-o` argument with a separate target configuration file.

## Generator types

The data generator operates in one of two modes. Select which mode to use by setting the top-level `type` field in your generator configuration.

* [`generator`](#generator) (default), useful for synthetic event generation.
* [`replay`](#replay), useful for both synthetic and trace-based event generation.

### `generator`

In `generator` mode, [state machines](./config-states.md) generate events, instantiated based on [`interarrival`](./config-interarrival.md) times.

This is the default type, and will be used if no `type` is supplied in the generator configuration.

| Object | Description | Options | Required? |
|---|---|---|---|
| `type` | The type of generator to use. | `generator` | No |
| [`emitters`](./config-emitters.md) | A list of emitters for this configuration. | See [`emitters`](./config-emitters.md) | Yes |
| [`interarrival`](./config-interarrival.md) | Sets the period of time that elapses between one event being generated and the next. | See [`interarrival`](./config-interarrival.md) | Yes |
| [`states`](./config-states.md) | A list of states associated with each emitter. | See [`states`](./config-states.md) | Yes |

In this example, there is just one state: `state_1`. When that state is reached, the `example_record_1` emitter produces an event with one field called `enum_dim` where the possible values of that field are selected using a uniform distribution from a list of characters.

There is then a `delay` of 1 second and the next state is selected from a list of possible `transitions`. In this configuration, because the `next` state is the same as the current state, this process repeats until the generator itself stops.

```
{
  "type": "generator",
  "states": [
    {
      "name": "state_1",
      "emitter": "example_record_1",
      "delay": {
        "type": "constant",
        "value": 1
      },
      "transitions": [
        {
          "next": "state_1",
          "probability": 1
        }
      ]
    }
  ],
  "interarrival": {
    "type": "constant",
    "value": 1
  },
  "emitters": [
    {
      "name": "example_record_1",
      "dimensions": [
        {
          "type": "enum",
          "name": "enum_dim",
          "values": [
            "A",
            "B",
            "C"
          ],
          "cardinality_distribution": {
            "type": "uniform",
            "min": 0,
            "max": 2
          }
        }
      ]
    }
  ]
}
```

### `replay`

A replay config uses a prerecorded set of event data to simulate the same set of events with the same cadence but with a simulated time clock. It will read the events from a CSV file mapping the primary time column in the data set and replacing it with a simulated time. The job will run for either a simulated duration specified in the "time" property of the launching job or until it produces the number of records requested "total_events".

The "replay" data generation will read each event from the file including all the fields present in the file and produce messages with the same schema. 
- It will parse the timestamp of the event and replace it with a simulated time. 
- The simulated time will start at the timestamp specified in the job's "time_type" property. 
- The simulated clock will advance at the same rate as the events in the file. Once the events in the source file are exhausted it will continue to replay them from the beginning.
- If `null_injection` is specified, the values of the source events for the specified `field`s will be replaced by a null value with a probability of the corresponding `null_probability`. 
- If `time_skipping` is used, every time a record is read from the source file the `skip_probability` is tested. If the probability hits, a random skip time is calculated between `min_skip_duration` and `max_skip_duration` which are expressed in seconds. The generator will then skip source messages until their timestamp is beyond the skip time and then continue with the next message in the file. If the file is exhausted during the skip, replay will continue from the beginning of the file.

The simulation will complete when either the total number of events reaches the job's "total_events" or when the total duration simulated reaches the "time" specified for the job.

If the time simulation starts in the past and reaches the current time, the job will continue issuing events in real-time while still respecting the time between events from the event source file as well as the time skips if `time_skipping` is used.


| Object | Description | Options | Required? |
|---|---|---|---|
| `type` | The type of generator to use. | `replay` | Yes |
| `time_field` | The name of the field in the source file to be used. | | Yes |
| `time_format` | | `nanos` `millis` `seconds` `posix` `epoch` or other [format string](https://docs.python.org/3/library/datetime.html#format-codes) | Yes |
| `source_file` | Local path to the event data file. | `generator` | Yes |
| `source_format` | | `csv` | Yes |
| `null_injections` | An array of [null injectors](#null-injectors). | | No |
| `time_skipping` | A single [time-skip](#time-skipping) object. | | No |

Example:

```
{
  "type": "replay",
  "time_field": "ts",
  "time_format": "epoch",
  "source_file": "data_files/iot_sample.csv",
  "source_format": "csv",
  "null_injection": [
    {
      "field": "humidity",
      "null_probability": 0.05
    },
    {
      "field": "temp",
      "null_probability": 0.01
    }
  ],
  "time_skipping": {
    "skip_probability": 0.01,
    "min_skip_duration": 5,
    "max_skip_duration": 300
  }
}
```

#### NULL injectors

In `replay` mode, whenever a NULL should be produced, provide a list of fields and the probability that they will be null in the `null_injections` field.

```
[
	{
		"field":"<field_name>",
		"null_probability":<probability from 0.0 to 1.0>
	}
]
```

#### Time skipping

```
{"skip_probability": <probability>, "min_skip_duration":<seconds>, "max_skip_duration":<seconds>}
```