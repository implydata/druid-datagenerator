## Event emitters

Emitters define the data that will be created by the data generator when a particular [state](./generator-states.md) is reached.

Define one or more emitters, each with its own dimensions and data specification.

Each emitter has this structure:

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `name` | The unique name for the emitter. | | Yes |
| [`dimensions`](#dimensions) | A list of attributes and measures, and, for each, the specification for how data will be generated. | | Yes |

### `dimensions`

When an event is emitted, it contains both an [event timestamp](#event-timestamp) and [attributes and measures](#attributes-and-measures) that you specify.

#### Event timestamp

A dimension called `time`, containing the synthetic event datetime stamp, is always emitted.

#### Attributes and measures

The `dimensions` list sets the name and type of every dimensions to be generated.

Every dimension must contain a `name` and a `type`.

Supported simple types are:

* [`timestamp`](./type-timestamp.md) generates a timestamp between a range.
* [`string`](./type-string.md) creates a synthetic string, optionally limited to a specific list of characters.
* [`int`](./type-int.md) generates whole numbers.
* [`float`](./type-float.md) generates floating point numbers.

More complex types are:

* [`ipaddress`](./type-ipaddress.md)
* [`enum`](#enum)
* [`counter`](#counter)
* [`object`](#object)
* [`list`](#list)
* [`variable`](#variable)

##### `enum`

Enum dimensions specify the set of all possible dimension values, as well as a distribution for selecting from the set.

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

##### `counter`

Counter dimensions are values that increment each time they occur in a record (counters are not incremented when they are missing or null).
Counters may be useful for dimensions simulating serial numbers, etc.
Counter dimension specification entries have the following format:

```
{
  "type": "counter",
  "name": "<dimension name>",
  "start": "<counter starting value (optional)>",
  "increment": "<counter increment value (optional)>",
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>start</i> is the initial value of the counter. (optional - the default is 0)
- <i>increment</i> is the amount to increment the value (optional - the default is 1)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)

In the following example, there is one emitter called "example_record_1" that has two dimensions, "dimension1" and "dimension2".

```
{
:
  "emitters": [
    {
      "name": "example_record_1",
      "dimensions": [
        {
          "type": "counter",
          "name": "dimension1"
        },
        {
          "type": "counter",
          "name": "dimension2",
          "start": 5
        }
      ]
    }
:
}
```

##### `object`

Object dimensions create nested data. Object dimension specification entries have the following format:

```
{
  "type": "object",
  "name": "<dimension name>",
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>,
  "dimensions": [<list of dimensions nested within the object>]
}
```

Where:
- <i>name</i> is the name of the object
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated objects (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)
- <i>dimensions</i> is a list of nested dimensions

##### `list`

list dimensions create lists of dimesions. List dimension specification entries have the following format:

```
{
  "type": "list",
  "name": "<dimension name>",
  "length_distribution": <distribution descriptor object>,
  "selection_distribution": <distribution descriptor object>,
  "elements": [<a list of dimension descriptions>],
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the object
- <i>length_distribution</i> describes the length of the resulting list as a distribution
- <i>selection_distribution</i> informs the generator which elements to select for the list from the elements list
- <i>elements</i> is a list of possible dimensions the generator may use in the generated list
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated lists (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)


List configuration can seem a bit confusing.
So to clarify, the generator will generate a list that is the length of a sample from the <i>length_distribution</i>.
The types of the elements of the list are selected from the <i>elements</i> list by using an index into the elements list that is determined by sampling from the <i>selection_distribution</i>.
The other field values (e.g., <i>cardinality</i>, <i>percent_nulls</i>, etc.) operate like the other types, but in this case apply to the entire list.

##### `variable`

Use `variable` when the value of the output field differs according to the [`state`](./config-states.md) that the data generator has reached.

```
{
  "type": "variable",
  "name": "<dimension name>"
  "variable": "<name of variable>"
}
```

Where:
- <i>name</i> is the name of the dimension.
- <i>variable</i> is the name of variable with a previously set value.