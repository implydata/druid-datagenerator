## Event emitters

Emitters define the data that will be created by the data generator when a particular [state](./genspec-states.md) is reached.

Define one or more emitters, each with its own dimensions and data specification.

Each emitter has this structure:

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `name` | The unique name for the emitter. | | Yes |
| `dimensions` | A list of attributes and measures, and, for each, the specification for how data will be generated. | | Yes |

When an event is emitted by a worker, it is made up of:

* An [event timestamp](#event-timestamps) with the name `time`, generated automatically by the worker.
* [Attributes and measures](#event-dimensions) set by `dimensions`.

### Event timestamps

A dimension called `time`, containing the synthetic event datetime stamp, is always emitted in ISO format.

Every worker has a different start time depending on when the worker is created by the data generator.

The very first worker starts either at the current date time, or by using the `-s` argument at the [command line](./command-line.md), at a simulated clock start time.

The next output event for that worker is emitted based on the `delay` between `states`. For more information, see [`states`](./genspec-states.md).

The data generator spawns additional workers up to a configurable maximum, e.g. using the `-m` argument at the [command line](./command-line.md). The interval between workers being spawned is controlled by the `interarrival` time, set in the [generator specification](./genspec.md).

### Event dimensions

The `dimensions` list prescribes the attributes and measures to be added to the event that is emitted.

The list is made up of [field generators](./fieldgen.md) and, optionally, [worker variables](./type-variable.md).

To understand how to create worker variables, see [states](./genspec-states.md).