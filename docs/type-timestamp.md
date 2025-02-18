## Synthetic timestamps

When a [field generator](./fieldgen.md) type is `timestamp`, an ISO format datetime is produced.

| Field | Description | Possible values | Required? | Default |
|---|---|---|---|---|
| `type` | The data type for the dimension. | `timestamp` | Yes ||
| `name` | The unique name for the dimension. | String | Yes ||
| `cardinality` | Indicates the number of unique values for this dimension. Use zero for unconstrained cardinality. | Integer | Yes ||
| `cardinality_distribution` | Skews the cardinality selection of the generated values. | A [distribution](./distributions.md) object. | Yes, if `cardinality` not 0.||
| `percent_missing` | The stochastic frequency for omitting this dimension from records (inclusive). | Integer between 0 and 100. | No. | 0 |
| `percent_nulls` | The stochastic frequency (inclusive) for generating null values. | Integer between 0 and 100. | No. | 0 |
| `distribution` | Describes the distribution of timestamp values the driver generates, with the dates given in ISO format. | A [distribution](./distributions.md) object. | Yes ||

In this example, there are two states: `state_1` and `state_2`. There is a 20% probability that the data generator will switch to `state_2` after `state_1`.

The emitter for `state_1` is `example_event_1`. This emits a simple [`string`](#string) as `emitter_number`, and `timestamp` in the range between 1st January 2020 at 3pm and 1st January 2020 at 8pm. `percent_nulls` adds a 25% chance that the value is null.

The emitter for `state_2` is `example_event_2` which also emits a simple string containing the emitter number. The `timestamp` for these events lie between 1st and 2nd of January 1920.

```
{
  "states": [
    {
      "name": "state_1",
      "emitter": "example_event_1",
      "delay": {
        "type": "constant",
        "value": 0.1
      },
      "transitions": [
        {
          "next": "state_1",
          "probability": 0.8
        },
        {
          "next": "state_2",
          "probability": 0.2
        }
      ]
    },
    {
      "name": "state_2",
      "emitter": "example_event_2",
      "delay": {
        "type": "constant",
        "value": 0.1
      },
      "transitions": [
        {
          "next": "state_1",
          "probability": 1.0
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
      "name": "example_event_1",
      "dimensions": [
        {
          "type": "string",
          "name": "emitter_number",
          "chars": "1",
          "length_distribution": { "type": "constant", "value": 1 }, "cardinality": 0
        },
        {
          "type": "timestamp",
          "name": "timestamp",
          "percent_nulls": 25,
          "cardinality": 0,
          "distribution": {
            "type": "uniform",
            "min": "2020-01-01T15:00",
            "max": "2020-01-01T20:00"
          }
        }
      ]
    },
    {
      "name": "example_event_2",
      "dimensions": [
        {
          "type": "string",
          "name": "emitter_number",
          "chars": "2",
          "length_distribution": { "type": "constant", "value": 1 }, "cardinality": 0
        },
        {
          "type": "timestamp",
          "name": "timestamp",
          "percent_nulls": 25,
          "cardinality": 0,
          "distribution": {
            "type": "uniform",
            "min": "1920-01-01",
            "max": "1920-01-02"
          }
        }
      ]
    }
  ]
}
```

This is an example of the output:

```
{"time":"2025-02-17T15:31:27.213","emitter_number":"1","timestamp":"2020-01-01T16:21:26.763"}
{"time":"2025-02-17T15:31:27.323","emitter_number":"1","timestamp":"2020-01-01T19:55:08.589"}
{"time":"2025-02-17T15:31:27.424","emitter_number":"1","timestamp":"2020-01-01T19:08:42.125"}
{"time":"2025-02-17T15:31:27.526","emitter_number":"1","timestamp": null}
{"time":"2025-02-17T15:31:27.632","emitter_number":"1","timestamp":"2020-01-01T19:14:46.070"}
{"time":"2025-02-17T15:31:27.736","emitter_number":"2","timestamp":"1920-01-01T01:04:10.144"}
{"time":"2025-02-17T15:31:27.842","emitter_number":"1","timestamp":"2020-01-01T16:33:39.371"}
{"time":"2025-02-17T15:31:27.945","emitter_number":"2","timestamp":"1920-01-01T17:32:15.567"}
{"time":"2025-02-17T15:31:28.051","emitter_number":"1","timestamp":"2020-01-01T18:25:38.457"}
{"time":"2025-02-17T15:31:28.155","emitter_number":"2","timestamp":"1920-01-01T22:53:57.637"}
```