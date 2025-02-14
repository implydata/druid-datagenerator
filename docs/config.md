## Generation configuration

Generator configurations are JSON objects that define how the data generator will behave.

| Object | Description | Options | Required? |
|---|---|---|---|
| [`type`](#generator-types) | The type of generator to use. | [__`generator`__](#generator) [`replay`](#replay) | No |
| Options | A list of fields that set the behavior of this `type` of generator. | See each `type`. | Yes |

Provide the configuration as a JSON object using either the `-c` command-line argument and full file path relative to `config_file`, or by piping from `stdin`. It's recommended to store JSON configuration files in the `config_file` folder, where you will also find several [examples](../config_file/examples).

In this example, the `generator_config.json` file has been stored inside the `config_file` folder. The following command is then run from the command line in the repo root. Note that the `-c` argument excludes the `config_file` folder name as it is relative.

```
python generator/DruidDataDriver.py -c generator_config.json -o generator_output.json -t 5M
```

Do not mix generator configuration and [generator targets](./target.md). From the command line, use the `-o` argument with a separate target configuration file.

### Generator types

The data generator operates in one of two modes.

* [`generator`](#generator) (default), useful for synthetic event generation.
* [`replay`](#replay), useful for both synthetic and trace-based event generation.

#### `generator`

`generator` is the default type, and will be used if no `type` is supplied in the JSON document.

| Object | Description | Options | Required? |
|---|---|---|---|
| [`type`](./config-types.md) | The type of generator to use. | __`generator`__ | No |
| [`emitters`](./config-emitters.md) | A list of emitters for this configuration. | See [`emitters`](./config-emitters.md) | Yes |
| [`interarrival`](./config-interarrival.md) | Sets the period of time that elapses between one event being generated and the next. | See [`interarrival`](./config-interarrival.md) | Yes |
| [`states`](./config-states.md) | A list of states associated with each emitter. | See [`states`](./config-states.md) | Yes |


In generator mode, a [state machine](./config-states.md) is created for each emitter, instantiated based on [`interarrival`](./config-interarrival.md).

Use state machines to simulate events from different types of producer, such as a device (IoT) or website visitor (clickstream).

Each state machine is probabilistic. State transitions may be stochastic based on probabilities.

Each state in the state machine performs four operations:

- First, the state sets any variable values
- Next, the state emits a record (based on an emitter description)
- The state delays for some period of time (based on a distribution)
- Finally, the state selects and transitions to a different state (based on a probabilistic transition table)

Emitters are record generators that output records as specified in the emitter description.

Each state employs a single emitter, but the same emitter may be used by many states.

The config JSON has the following format:

Data Generator Job:
```
{
  "type": "generator" 
  "emitters": [...], 
  "interarrival": {...},
  "states": [...]
}
```
- The _type_ of job can be either "generator" (the default) or "replay"
- The _emitters_ list is a list of record generators.
- The _interarrival_ object describes the inter-arrival times (i.e., inverse of the arrival rate) of entities to the state machine
- The _states_ list is a description of the state machine


#### `replay`

| Object | Description | Options | Required? |
|---|---|---|---|
| [`type`](./config-types.md) | The type of generator to use. | `replay` | Yes |

A replay config uses a prerecorded set of event data to simulate the same set of events with the same cadence but with a simulated time clock. It will read the events from a CSV file mapping the primary time column in the data set and replacing it with a simulated time. The job will run for either a simulated duration specified in the "time" property of the launching job or until it produces the number of records requested "total_events".

The config properties for a replay job are:

- time_field - the name of the field in the source file to be used
- time_format - nanos, millis, seconds, posix/epoch or a valid [format string](https://docs.python.org/3/library/datetime.html#format-codes) 
- source_file - local path to the event data file
- source_format - only "csv" is supported for now
- null_injections - (optional) an array of null injectors in the form `[{"field":"<field_name>","null_probability":<probability from 0.0 to 1.0>},...]`
- time_skipping: - (optional) a single object in the form `{"skip_probability": <probability>, "min_skip_duration":<seconds>, "max_skip_duration":<seconds>}`
Example:
```json
{
  "type": "replay",
  "time_field": "ts",
  "time_format": "epoch",
  "source_file": "data_files/iot_sample.csv",
  "source_format": "csv",
  "null_injection": [ {"field": "humidity", "null_probability": 0.05 }, {"field": "temp", "null_probability": 0.01}],
  "time_skipping": {"skip_probability": 0.01, "min_skip_duration": 5, "max_skip_duration": 300}
}
```

The "replay" data generation will read each event from the file including all the fields present in the file and produce messages with the same schema. 
- It will parse the timestamp of the event and replace it with a simulated time. 
- The simulated time will start at the timestamp specified in the job's "time_type" property. 
- The simulated clock will advance at the same rate as the events in the file. Once the events in the source file are exhausted it will continue to replay them from the beginning.
- If `null_injection` is specified, the values of the source events for the specified `field`s will be replaced by a null value with a probability of the corresponding `null_probability`. 
- If `time_skipping` is used, every time a record is read from the source file the `skip_probability` is tested. If the probability hits, a random skip time is calculated between `min_skip_duration` and `max_skip_duration` which are expressed in seconds. The generator will then skip source messages until their timestamp is beyond the skip time and then continue with the next message in the file. If the file is exhausted during the skip, replay will continue from the beginning of the file.

The simulation will complete when either the total number of events reaches the job's "total_events" or when the total duration simulated reaches the "time" specified for the job.

If the time simulation starts in the past and reaches the current time, the job will continue issuing events in real-time while still respecting the time between events from the event source file as well as the time skips if `time_skipping` is used.
