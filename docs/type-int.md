## Synthetic integers

When a [field generator](./fieldgen.md) type is `int`, a random integer is created.

| Field | Description | Possible values | Required? | Default |
|---|---|---|---|---|
| `type` | The data type for the dimension. | `int` | Yes ||
| `name` | The unique name for the dimension. | String | Yes ||
| `cardinality` | Indicates the number of unique values for this dimension. Use zero for unconstrained cardinality. | Integer | Yes ||
| `cardinality_distribution` | Skews the cardinality selection of the generated values. | A [distribution](./distributions.md) object. | Yes, if `cardinality` not 0.||
| `percent_missing` | The stochastic frequency for omitting this dimension from records (inclusive). | Integer between 0 and 100. | No. | 0 |
| `percent_nulls` | The stochastic frequency (inclusive) for generating null values. | Integer between 0 and 100. | No. | 0 |
| `distribution` | Specifies the distribution of the numbers generated, with each rounded to the nearest integer value. | A [distribution](./distributions.md) object. | Yes. ||

In this example, there is just one state (`state_1`) and therefore one state listed in `transitions`, causing the data generator to always return to `state_1`.

The emitter for `state_1` is `example_event_1`, which emits the following dimensions:

* `user` is an `enum` dimension, selecting one of the `values` using a `uniform` `cardinality_distribution` [distribution](./distributions.md) object.
* `whiteboard_pen_delta` - the change in the number of whiteboard pens each person owns - is an `int` selected using a `normal` `distribution` with a `mean` of 0 and standard deviation (`stddev`) of 4.
* `cups_of_coffee_consumed` is an int generated using an `exponential` `distribution`, meaning that - on average - 25 cups of coffee are consumed, but the distribution is exponential.

```
{
  "states": [
    {
      "name": "state_1",
      "emitter": "example_event_1",
      "delay": {
        "type": "uniform",
        "min": 5,
        "max": 10
      },
      "transitions": [ { "next": "state_1", "probability": 1 } ]
    }
  ],
  "interarrival": {
    "type": "constant",
    "value": 3600
  },
  "emitters": [
    {
      "name": "example_event_1",
      "dimensions": [
        {
          "type": "enum",
          "name": "user",
          "values": ["Aisha", "Mateo", "Chen", "Fatima", "Liam", "Kwame", "Elena", "Noah", "Tenzing", "Keisha"],
          "cardinality_distribution": { "type": "uniform", "min": 0, "max": 9 }
        },
        {
          "type": "int",
          "name": "whiteboard_pen_delta",
          "distribution": { "type": "normal", "mean": 0, "stddev": 4 }, "cardinality": 0
        },
        {
          "type": "int",
          "name": "cups_of_coffee_consumed",
          "distribution": { "type": "exponential", "mean": 25 }, "cardinality": 0
        }
      ]
    }
  ]
}
```

This is an example of the output:

```
{"time":"2042-09-23T11:03:03.402","user":"Elena","whiteboard_pen_delta":0,"cups_of_coffee_consumed":7}
{"time":"2042-09-23T11:03:10.723","user":"Keisha","whiteboard_pen_delta":0,"cups_of_coffee_consumed":5}
{"time":"2042-09-23T11:03:17.208","user":"Tenzing","whiteboard_pen_delta":0,"cups_of_coffee_consumed":74}
{"time":"2042-09-23T11:03:28.188","user":"Noah","whiteboard_pen_delta":-4,"cups_of_coffee_consumed":0}
{"time":"2042-09-23T11:03:34.053","user":"Fatima","whiteboard_pen_delta":1,"cups_of_coffee_consumed":5}
{"time":"2042-09-23T11:03:41.417","user":"Mateo","whiteboard_pen_delta":0,"cups_of_coffee_consumed":8}
{"time":"2042-09-23T11:03:46.727","user":"Tenzing","whiteboard_pen_delta":0,"cups_of_coffee_consumed":77}
{"time":"2042-09-23T11:03:54.689","user":"Elena","whiteboard_pen_delta":-3,"cups_of_coffee_consumed":31}
{"time":"2042-09-23T11:04:01.295","user":"Elena","whiteboard_pen_delta":0,"cups_of_coffee_consumed":13}
{"time":"2042-09-23T11:04:08.081","user":"Kwame","whiteboard_pen_delta":3,"cups_of_coffee_consumed":21}
```