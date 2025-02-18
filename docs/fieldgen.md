## Field generators

Field generators are JSON objects that appear in emitter [`dimensions`](./genspec-emitters.md) and state [`variables`](./genspec-states.md).

Whenever a worker encounters a field generator, whether via an emitter dimension list or a state variable, it generates a key (`name`) and a value.

The value that is generated depends on the field generator `type`. Available field generator types are:

* [`timestamp`](./type-timestamp.md) generates a timestamp between a range.
* [`string`](./type-string.md) creates a synthetic string, optionally limited to a specific list of characters.
* [`int`](./type-int.md) generates whole numbers.
* [`float`](./type-float.md) generates floating point numbers.
* [`ipaddress`](./type-ipaddress.md) creates a network IP address.
* [`counter`](./type-counter.md) creates an incrementing integer.
* [`enum`](#enum)
* [`object`](#object)
* [`list`](#list)

For information, including examples, see the individual pages for each field generator type.

#### `enum`

Enum field generators specify the set of all possible values, as well as a distribution for selecting from the set.

Enums have the following format:

```
{
  "type": "enum",
  "name": "<dimension name>",
  "values": [...],
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:

- <i>name</i> is the name of the dimension
- <i>values</i> is a list of the values
- <i>cardinality_distribution</i> informs the cardinality selection of the generated values
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)

#### `object`

Object field generators create nested data.

- <i>name</i> is the name of the object
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated objects (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)
- <i>dimensions</i> is a list of nested dimensions

```json
{
  "emitters": [
    {
      "name": "example_record_1",
      "dimensions": [
        {
          "type": "object",
          "name": "Obj1",
          "cardinality": 0,
          "dimensions": [
            {
              "type": "enum",
              "name": "enum_dim",
              "values": ["A", "B", "C"],
              "cardinality_distribution": { "type": "uniform", "min": 0, "max": 2 }
            },
            {
              "type": "string",
              "name": "string_dim",
              "length_distribution": { "type": "constant", "value": 5 },
              "cardinality": 0,
              "chars": "ABC123"
            },
            {
              "type": "int",
              "name": "int_dim",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "exponential", "mean": 5 }
            },
            {
              "type": "float",
              "name": "dim_float",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "normal", "mean": 5, "stddev": 2 },
              "precision": 3
            },
            {
              "type": "timestamp",
              "name": "dim_timestamp",
              "distribution": { "type": "uniform", "min": "2008-09-03T10:00:00.0Z", "max": "2008-09-03T20:00:00.0Z" },
              "cardinality": 0
            },
            {
              "type": "ipaddress",
              "name": "dim_ip",
              "distribution": { "type": "uniform", "min": 2130706433, "max": 2130706440 },
              "cardinality": 0
            }
          ]
        },
        {
          "type": "object",
          "name": "Obj2",
          "cardinality": 3,
          "cardinality_distribution": { "type": "uniform", "min": 0, "max": 2 },
          "dimensions": [
            {
              "type": "enum",
              "name": "enum_dim",
              "values": ["A", "B", "C"],
              "cardinality_distribution": { "type": "uniform", "min": 0, "max": 2 }
            },
            {
              "type": "string",
              "name": "string_dim",
              "length_distribution": { "type": "constant", "value": 5 },
              "cardinality": 0,
              "chars": "ABC123"
            },
            {
              "type": "int",
              "name": "int_dim",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "exponential", "mean": 5 }
            },
            {
              "type": "float",
              "name": "dim_float",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "normal", "mean": 5, "stddev": 2 },
              "precision": 3
            },
            {
              "type": "timestamp",
              "name": "dim_timestamp",
              "distribution": { "type": "uniform", "min": "2008-09-03T10:00:00.0Z", "max": "2008-09-03T20:00:00.0Z" },
              "cardinality": 0
            },
            {
              "type": "ipaddress",
              "name": "dim_ip",
              "distribution": { "type": "uniform", "min": 2130706433, "max": 2130706440 },
              "cardinality": 0
            }
          ]
        }
      ]
    }
  ],
  "interarrival": { "type": "constant", "value": 1 },
  "states": [
    {
      "name": "state_1",
      "emitter": "example_record_1",
      "delay": { "type": "constant", "value": 1 },
      "transitions": [{ "next": "state_1", "probability": 1.0 }]
    }
  ]
}
```

#### `list`

list field generators create lists of dimesions.

- <i>name</i> is the name of the object
- <i>length_distribution</i> describes the length of the resulting list as a distribution
- <i>selection_distribution</i> informs the generator which elements to select for the list from the elements list
- <i>elements</i> is a list of possible dimensions the generator may use in the generated list
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated lists (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)

The data generator creates a list that is the length of a sample from the <i>length_distribution</i>.

The types of the elements of the list are selected from the <i>elements</i> list by using an index into the elements list that is determined by sampling from the <i>selection_distribution</i>.

The other field values (e.g., <i>cardinality</i>, <i>percent_nulls</i>, etc.) operate like the other types, but in this case apply to the entire list.

```json
{
  "emitters": [
    {
      "name": "example_record_1",
      "dimensions": [
        {
          "type": "list",
          "name": "List1",
          "length_distribution": { "type": "uniform", "min": 1, "max": 3 },
          "selection_distribution": { "type": "uniform", "min": 0, "max": 5 },
          "cardinality": 0,
          "elements": [
            {
              "type": "enum",
              "name": "enum_dim",
              "values": ["A", "B", "C"],
              "cardinality_distribution": { "type": "uniform", "min": 0, "max": 2 }
            },
            {
              "type": "string",
              "name": "string_dim",
              "length_distribution": { "type": "constant", "value": 5 },
              "cardinality": 0,
              "chars": "ABC123"
            },
            {
              "type": "int",
              "name": "int_dim",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "exponential", "mean": 5 }
            },
            {
              "type": "float",
              "name": "dim_float",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "normal", "mean": 5, "stddev": 2 },
              "precision": 3
            },
            {
              "type": "timestamp",
              "name": "dim_timestamp",
              "distribution": { "type": "uniform", "min": "2008-09-03T10:00:00.0Z", "max": "2008-09-03T20:00:00.0Z" },
              "cardinality": 0
            },
            {
              "type": "ipaddress",
              "name": "dim_ip",
              "distribution": { "type": "uniform", "min": 2130706433, "max": 2130706440 },
              "cardinality": 0
            }
          ]
        },
        {
          "type": "list",
          "name": "List2",
          "length_distribution": { "type": "uniform", "min": 1, "max": 3 },
          "selection_distribution": { "type": "uniform", "min": 0, "max": 5 },
          "cardinality": 3,
          "cardinality_distribution": { "type": "uniform", "min": 0, "max": 2 },
          "elements": [
            {
              "type": "enum",
              "name": "enum_dim",
              "values": ["A", "B", "C"],
              "cardinality_distribution": { "type": "uniform", "min": 0, "max": 2 }
            },
            {
              "type": "string",
              "name": "string_dim",
              "length_distribution": { "type": "constant", "value": 5 },
              "cardinality": 0,
              "chars": "ABC123"
            },
            {
              "type": "int",
              "name": "int_dim",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "exponential", "mean": 5 }
            },
            {
              "type": "float",
              "name": "dim_float",
              "distribution": { "type": "uniform", "min": 0, "max": 1000 },
              "cardinality": 10,
              "cardinality_distribution": { "type": "normal", "mean": 5, "stddev": 2 },
              "precision": 3
            },
            {
              "type": "timestamp",
              "name": "dim_timestamp",
              "distribution": { "type": "uniform", "min": "2008-09-03T10:00:00.0Z", "max": "2008-09-03T20:00:00.0Z" },
              "cardinality": 0
            },
            {
              "type": "ipaddress",
              "name": "dim_ip",
              "distribution": { "type": "uniform", "min": 2130706433, "max": 2130706440 },
              "cardinality": 0
            }
          ]
        }
      ]
    }
  ],
  "interarrival": { "type": "constant", "value": 1 },
  "states": [
    {
      "name": "state_1",
      "emitter": "example_record_1",
      "delay": { "type": "constant", "value": 1 },
      "transitions": [{ "next": "state_1", "probability": 1.0 }]
    }
  ]
}
```