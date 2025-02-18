## Synthetic floating point numbers

When a [field generator](./fieldgen.md) type is  `float`, random floating point numbers are created.

| Field | Description | Possible values | Required? | Default |
|---|---|---|---|---|
| `type` | The data type for the dimension. | `float` | Yes ||
| `name` | The unique name for the dimension. | String | Yes ||
| `cardinality` | Indicates the number of unique values for this dimension. Use zero for unconstrained cardinality. | Integer | Yes ||
| `cardinality_distribution` | Skews the cardinality selection of the generated values. | A [distribution](./distributions.md) object. | Yes, if `cardinality` not 0.||
| `percent_missing` | The stochastic frequency for omitting this dimension from records (inclusive). | Integer between 0 and 100. | No. | 0 |
| `percent_nulls` | The stochastic frequency (inclusive) for generating null values. | Integer between 0 and 100. | No. | 0 |
| `distribution` | Specifies the distribution of the numbers generated. | A [distribution](./distributions.md) object. | Yes. ||
| `precision` | The number of digits after the decimal. | Integer | No. | Full precision. |

In this example, there is just one state (`state_1`) and therefore one state listed in `transitions`, causing the data generator to always return to `state_1`.

The emitter for `state_1` is `example_event_1`, which emits the following dimensions:

* `service` is an `enum` dimension, selecting one of the `values` using a `normal` `cardinality_distribution` [distribution](./distributions.md) object, causing withdrawals to appear more than deposits.
* `account_id` is a synthetic string of numbers with a constant length of 16.
* `amt` is a float with an `exponential` distribution that has a mean value of `50000`.
* `result` is another `enum` dimension indicating whether the transaction was successful or not.

```
{
  "states": [
    {
      "name": "state_1",
      "emitter": "example_event_1",
      "delay": {
        "type": "uniform",
        "min": 1000,
        "max": 25000
      },
      "transitions": [ { "next": "state_1", "probability": 1 } ]
    }
  ],
  "interarrival": {
    "type": "uniform",
    "min": 1000,
    "max": 25000
  },
  "emitters": [
    {
      "name": "example_event_1",
      "dimensions": [
        {
          "type": "enum",
          "name": "service",
          "values": ["/api/deposit","/api/withdraw"],
          "cardinality_distribution": { "type": "normal", "mean": 1, "stddev": 0.5 }
        },
        {
          "type": "string",
          "name": "account_id",
          "chars": "0123456789",
          "length_distribution": { "type": "constant", "value": 16 }, "cardinality": 0
        },
        {
          "type": "float",
          "name": "amt",
          "distribution": { "type": "exponential", "mean":50000 }, "cardinality": 0,
          "precision": 2
        },
        {
          "type": "enum",
          "name": "result",
          "values": ["fail","success"],
          "cardinality_distribution": { "type": "normal", "mean": 2, "stddev": 1 }
        }
      ]
    }
  ]
}
```

This is an example of the output:

```
{"time":"1965-09-23T08:12","service":"/api/withdraw","account_id":"7431619535047847","amt":12667.48,"result":"success"}
{"time":"1965-09-23T12:21:26.139","service":"/api/withdraw","account_id":"5781087885140068","amt":111413.46,"result":"success"}
{"time":"1965-09-23T12:38:54.794","service":"/api/withdraw","account_id":"3130599031665446","amt":49792.34,"result":"fail"}
{"time":"1965-09-23T12:56:36.786","service":"/api/withdraw","account_id":"1053843187271804","amt":23673.06,"result":"fail"}
{"time":"1965-09-23T15:22:51.680","service":"/api/withdraw","account_id":"9568324760011287","amt":37671.47,"result":"success"}
{"time":"1965-09-23T18:03:12.137","service":"/api/withdraw","account_id":"4322611339413197","amt":48198.53,"result":"success"}
{"time":"1965-09-23T19:07:36.020","service":"/api/withdraw","account_id":"1815911749890494","amt":9563.61,"result":"success"}
{"time":"1965-09-23T19:55:39.606","service":"/api/deposit","account_id":"7756949864252754","amt":5484.89,"result":"fail"}
{"time":"1965-09-23T20:20:07.973","service":"/api/deposit","account_id":"9154057313396407","amt":45905.47,"result":"success"}
{"time":"1965-09-23T20:43:16.923","service":"/api/deposit","account_id":"8583774707217756","amt":47095.43,"result":"success"}
```