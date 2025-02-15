## Generator states

When the generator reaches a state, the following happens:

1. [Variable](./config-states.md#state-variables) values are set
2. Based on a the [emitter description](./config-emitters), an event is emitted.
3. The generator waits for a period of time.
4. The next state is selected.

The selection of the next state is probabilistic, meaning it's possible for the output events to be stochastic (ie, they have a random probability distribution).

Each state employs a single emitter, but the same emitter may be used by many states.

List all possible states in the `states` object of the configuration file, with the first entry in the list setting the initial state.

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `name` | A unique, friendly name for this state. |  | Yes |
| [`variables`](#variables) | A list of dimension definitions for [`variable`-type dimensions](./config-emitters.md#variable) | | No |
| `emitter` | The [emitter](./config-emitters.md) to use. | The `name` of an emitter in the `emitter` list. | Yes |
| [`transitions`](#transitions) | A list of all possible states that could be entered after this state. | | Yes |
| `delay` | How long (in seconds) to remain in the state before transitioning, defined as a [`distribution`](./distributions.md). | | Yes |


```
{
:
	"states": [
		{
		  "name": <state>,
		  "variables": [variable 1, variable 2...],
		  "emitter": <emitter>,
		  "transitions": [state transition 1, state transition 2...],
		  "delay": <distribution descriptor>
		}
	]
:
}
```

### Variables

See the [variables](../config_file/examples/variable.json) example configuration file.

See [`variable`-type dimensions](./emitters.md#variable).

### Transitions

Transition objects describe potential state transitions from the current state to the next state.

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `next` | Either the name of the next state to enter _or_ `stop` |  | Yes |
| `probability` | The probability that this state will be entered. | A value greater than zero and less than or equal to one. The sum total of all probabilities must be 1. | Yes |

These objects have the following form:

```
{
  "next": <state name>,
  "probability": <probability value>
}
```

When the `next` field is set to `stop`, the state machine will terminate.

In the following example, the same state is applied after every transition. Apply this approach when state engine functionality is not required.

```
{
:
	"states": [
	    {
	      "name": "initial",
	      "emitter": "emitter-name",
	      "delay": {
	        "type": "constant",
	        "value": 1
	      },
	      "transitions": [
	        {
	          "next": "initial",
	          "probability": 1.0
	        }
	      ]
	    }
	  ]
:
}
```