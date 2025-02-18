## Worker states

When the worker reaches a state, the following happens:

1. [Variable](#variables) values are set.
2. Based on a the [emitter description](./genspec-emitters.md), an event is emitted.
3. The generator delays for a period of time.
4. The next state is selected.

The selection of the next state is probabilistic, meaning it's possible for the output events to be stochastic (ie, they have a random probability distribution).

Each state employs a single emitter, but the same emitter may be used by many states.

List all possible states in the `states` object of the configuration file, with the first entry in the list setting the initial state.

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `name` | A unique, friendly name for this state. |  | Yes |
| `emitter` | The [emitter](./genspec-emitters.md) to use. | The `name` of an emitter in the `emitter` list. | Yes |
| [`variables`](#variables) | A list of [field generators](./fieldgen.md). | | No |
| `delay` | How long (in seconds) to remain in the state before transitioning, defined as a [`distribution`](./distributions.md). | | Yes |
| [`transitions`](#transitions) | A list of all possible states that could be entered after this state. | | Yes |

### Variables

The optional `variables` list contains [field generators](./fieldgen.md). When a worker enters this state, it generates fields that are then stored for later re-use.

Address the variable values in `emitters` by using a `variable`-type dimension, and using the `name` of the variable in the `variable` field.

For more information, see [`variable`-type dimensions](./type-variable.md).

### Transitions

For a given state, this part of the configuration lists all the potential states that can be entered, and the probabilities for each state.

This allows for very simple (single state) through to very complex (multiple branching) state machines.

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `next` | Either the name of the next state to enter _or_ `stop` |  | Yes |
| `probability` | The probability that this state will be entered. | A value greater than zero and less than or equal to one. The sum total of all probabilities must be 1. | Yes |

When the `next` field is set to `stop`, the state machine will terminate.

In this example, there are two states, `state_1` and `state_2`.

`state_1` uses the `example_record_1` emitter, while `state_2` uses the `example_record_2` emitter.

The initial state is the first in the list, `state_1`. When `state_1` emits a record, a `delay` of 1 second occurs before a selection is made from `transitions`: there is a 50% probability that the next state will be `state_2`, and a 50% probability that the next state will be `state_1`.

If `state_2` is selected, this emits an `example_record_2`, a `delay` of 1 second occurs, and another selection is made from `transitions`: there is a 75% chance that the next state will be `state_1`, and a 25% chance that it will be `state_2`.

```json
{
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
          "probability": 0.5
        },
        {
          "next": "state_2",
          "probability": 0.5
        }
      ]
    },
    {
      "name": "state_2",
      "emitter": "example_record_2",
      "delay": {
        "type": "constant",
        "value": 1
      },
      "transitions": [
        {
          "next": "state_1",
          "probability": 0.75
        },
        {
          "next": "state_2",
          "probability": 0.25
        }
      ]
    }
  ],
  "emitters": [
    {
      "name": "example_record_1",
      "dimensions": [
        {
          "type": "counter",
          "name": "default_counter1"
        },
        {
          "type": "counter",
          "name": "start_counter1",
          "start": 5
        },
        {
          "type": "counter",
          "name": "increment_counter1",
          "increment": 5
        },
        {
          "type": "counter",
          "name": "both_counter1",
          "start": 5,
          "increment": 5
        }
      ]
    },
    {
      "name": "example_record_2",
      "dimensions": [
        {
          "type": "counter",
          "name": "default_counter2"
        },
        {
          "type": "counter",
          "name": "start_counter2",
          "start": 5
        },
        {
          "type": "counter",
          "name": "increment_counter2",
          "increment": 5
        },
        {
          "type": "counter",
          "name": "both_counter2",
          "start": 5,
          "increment": 5
        }
      ]
    }
  ],
  "interarrival": {
    "type": "constant",
    "value": 1
  }
}
```
