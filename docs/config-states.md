## Event states

The data generator uses a probabilistic state machine to emit events.

List all possible states for a given emitter in the `states` object of the configuration file, with the first entry in the list setting the initial state.

| Field | Description | Possible values | Required? |
|---|---|---|---|
| `name` | A unique, friendly name for this state. |  | Yes |
| `emitter` | A [emitter](./config-emitters.md) from the list of `emitters` that this state belongs to. | The `name` of an emitter in the `emitter` list. | Yes |
| `delay` | How long (in seconds) to remain in the state before transitioning, defined as a [`distribution`](./distributions.md). | | Yes |
| [`transitions`](#state-transitions) | A list of all possible states that could be entered after this state. | | Yes |
| [`variables`](#variables) | A list of dimension definitions for [`variable`-type dimensions](./config-emitters.md#variable) | | No |


```
{
:
	"states": [
		{
		  "emitter": <emitter name>,
		  "name": <state name>,
		  "delay": <distribution descriptor object>,
		  "transitions": [...],
		  "variables": [...]
		}
	]
:
}
```

### State transitions

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

### State variables

See the [variables](../config_file/examples/variable.json) example configuration file.

See [`variable`-type dimensions](./emitters.md#variable).