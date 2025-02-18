## Generator specifications

Control the behavior of the data generator using a JSON configuration object known as the "Generator Specification". See the `config_file` folder for [examples](../config_file/examples).

The data generator operates in one of two modes:

* [`generator`](#generator), useful for synthetic event generation.
* [`replay`](#replay), useful for both synthetic and trace-based event generation.

When not specified, the generator defaults to using `generator` mode.

### `generator`

In `generator` mode, workers traverse a number of [`states`](./genspec-states.md) and generates events as they go using [`emitters`](./genspec-emitters.md). Workers are created periodically, according to the [`interarrival`](./genspec-interarrival.md) time.

DO NOT include `type` in the generator specification when using `generator` mode.

This is the default mode, and will be used if no `type` is supplied in the generator configuration.

| Object | Description | Options | Required? |
|---|---|---|---|
| `type` | The type of generator to use. | `generator` | No. |
| [`states`](./genspec-states.md) | A list of states that will be used to generate events. | See [`states`](./genspec-states.md) | Yes |
| [`emitters`](./genspec-emitters.md) | A list of emitters. | See [`emitters`](./genspec-emitters.md) | Yes |
| [`target`](./tarspec.md) | A target specification. | See [`targets`](./tarspec.md) | No |
| `interarrival` | The period of time that elapses before the next worker is started. | A [distribution](./distributions.md) object. | Yes |

In this example, there is just one state: `state_1`. When each worker reaches that state, it uses the `example_record_1` emitter to produce an event with one field called `enum_dim`, where the possible values of that field are selected using a uniform distribution from a list of characters. `target` provides an inline [target specification](./tarspec.md), causing the output to be sent to `stdout`.

There is then a `delay` of 5 seconds before a worker picks the next state from a list of possible `transitions`. In this specification, because the `next` state is the same as the current state, the worker repeatedly enters this state until the generator itself stops.

The `interarrival` distribution is a `constant`, causing new workers to be spawned once every second.

```json
{
  "type": "generator",
  "states": [
    {
      "name": "state_1",
      "emitter": "example_record_1",
      "delay": {
        "type": "constant",
        "value": 5
      },
      "transitions": [
        {
          "next": "state_1",
          "probability": 1
        }
      ]
    }
  ],
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
  ],
  "target": { "type" : "stdout"},
  "interarrival": { "type": "constant", "value": 1 }
}
```

Try this out by saving the above to `example.json` within the `config_file` folder.

The following command will create 10 records and use only one worker:

```bash
python3 generator/DruidDataDriver.py -f example.json -n 10 -m 1
```

This causes the following output.  Notice that each row is spaced 5 seconds apart, since only one worker is generating results.

```json
{"time":"2025-02-18T09:32:16.416","enum_dim":"A"}
{"time":"2025-02-18T09:32:21.426","enum_dim":"C"}
{"time":"2025-02-18T09:32:26.429","enum_dim":"B"}
{"time":"2025-02-18T09:32:31.434","enum_dim":"C"}
{"time":"2025-02-18T09:32:36.440","enum_dim":"B"}
{"time":"2025-02-18T09:32:41.444","enum_dim":"C"}
{"time":"2025-02-18T09:32:46.449","enum_dim":"B"}
{"time":"2025-02-18T09:32:51.453","enum_dim":"A"}
{"time":"2025-02-18T09:32:56.459","enum_dim":"A"}
{"time":"2025-02-18T09:33:01.464","enum_dim":"B"}
```

When run with the `-m 3`, 3 workers are spawned. Since `interarrival` is a `constant` of 1 second, one worker is spawned every second, meaning that rows 1 through 3 are each from different worker threads, and rows 4 through 6 are those workers in their second state, 7 through 9 in their third state, and so on.

```json
{"time":"2025-02-18T09:35:49.618","enum_dim":"A"}
{"time":"2025-02-18T09:35:50.623","enum_dim":"B"}
{"time":"2025-02-18T09:35:51.629","enum_dim":"C"}
{"time":"2025-02-18T09:35:54.626","enum_dim":"B"}
{"time":"2025-02-18T09:35:55.626","enum_dim":"C"}
{"time":"2025-02-18T09:35:56.635","enum_dim":"A"}
{"time":"2025-02-18T09:35:59.632","enum_dim":"A"}
{"time":"2025-02-18T09:36:00.627","enum_dim":"C"}
{"time":"2025-02-18T09:36:01.640","enum_dim":"A"}
{"time":"2025-02-18T09:36:04.635","enum_dim":"A"}
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
