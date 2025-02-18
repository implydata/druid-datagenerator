## Worker variables

When a worker encounters an [emitter dimension](./genspec-emitters.md#dimensions) with a `type` of `variable`, the worker variable is used, rather than a new value value being created.

| Field | Description | Possible values | Required? | Default |
|---|---|---|---|---|
| `type` | The data type for the dimension. | `float` | Yes ||
| `name` | The unique name for the dimension. | String | Yes ||
| `variable` | The name of a [state variable](./genspec.md#variables). | String | Yes ||

In the following example, there are two states, `state_1` and `state_2`. In `state_1`, two variables are created, `var_client_ip` and `var_account_code`. Notice that these conform to the normal specification for [dimensions in emitters](./genspec-emitters.md) - [`ipaddress`](./type-ipaddress.md) and [`string`](./type-string.md) respectively.

Both states use the `click` emitter, which contains:

* An `enum` dimension to randomly output a request URL.
* The value of the `var_client_ip` variable, output as the `client_ip` field.
* The value of the `var_account_code` variable, output as the `account_code` field.

```json
{
  "states": [
    {
      "name": "state_1",
      "emitter": "click",
      "variables": [
        {
          "type": "ipaddress",
          "name": "var_client_ip",
          "cardinality": 5,
          "cardinality_distribution": { "type": "uniform", "min": 0, "max": 5 },
          "distribution": {
            "type": "uniform",
            "min": 184549376,
            "max": 2127008767
          }
        },
        {
          "type": "string",
          "name": "var_account_code",
          "length_distribution": { "type": "constant", "value": 5 },
          "cardinality": 0,
          "chars": "ABC123"
        }
      ],
      "delay": { "type": "constant", "value": 0.5 },
      "transitions": [ { "next": "state_2", "probability": 1.0 } ]
    },
    {
      "name": "state_2",
      "emitter": "click",
      "delay": { "type": "constant", "value": 1 },
      "transitions": [
        { "next": "state_2", "probability": 0.7 },
        { "next": "stop", "probability": 0.3 }
      ]
    }
  ],
  "emitters": [
    {
      "name": "click",
      "dimensions": [
        { "type": "variable", "name": "client_ip", "variable": "var_client_ip" },
        { "type": "variable", "name": "account_code", "variable": "var_account_code" },
        {
          "type": "enum",
          "name": "request",
          "values": [
            "GET /api/articles",
            "GET /api/articles/42",
            "GET /api/articles/102/history",
            "GET /api/articles/56/contributors",
            "GET /api/categories",
            "GET /api/categories/7/articles",
            "GET /api/search?q=quantum-mechanics",
            "GET /api/users/18",
            "GET /api/users/73/contributions",
            "GET /api/recent-changes"
          ],
          "cardinality_distribution": { "type": "uniform", "min": 0, "max": 9 }
        }
      ]
    }
  ],
  "target": { "type": "stdout"},
  "interarrival": { "type": "constant", "value": 0.2 }
}
```

Since the JSON above contains an inline `target`, you can save the JSON above as `example.json` in the `config_file` folder and run it with the following command.

```bash
python3 generator/DruidDataDriver.py -f example.json -n 15 -m 2 -s "2009-05-21:08:00:10"
```

* `-n 15` specifies a maximum of 15 records.
* `-m 2` sets a maximum of 2 workers.
* `-s` instructs the data generator to use a simulated clock.

Here is an example of the output:

```json
{"time":"2009-05-21T08:00","client_ip":"57.222.36.183","account_code":"A3332","request":"GET /api/articles/56/contributors"}
{"time":"2009-05-21T08:00:10.200","client_ip":"96.8.91.108","account_code":"BA113","request":"GET /api/users/18"}
{"time":"2009-05-21T08:00:10.500","client_ip":"57.222.36.183","account_code":"A3332","request":"GET /api/categories/7/articles"}
{"time":"2009-05-21T08:00:10.700","client_ip":"96.8.91.108","account_code":"BA113","request":"GET /api/articles/42"}
{"time":"2009-05-21T08:00:11.500","client_ip":"57.222.36.183","account_code":"A3332","request":"GET /api/articles/102/history"}
{"time":"2009-05-21T08:00:11.700","client_ip":"96.8.91.108","account_code":"BA113","request":"GET /api/users/73/contributions"}
{"time":"2009-05-21T08:00:12.500","client_ip":"57.222.36.183","account_code":"A3332","request":"GET /api/categories/7/articles"}
{"time":"2009-05-21T08:00:15.400","client_ip":"121.93.131.111","account_code":"2A2AC","request":"GET /api/search?q=quantum-mechanics"}
{"time":"2009-05-21T08:00:15.600","client_ip":"58.116.85.49","account_code":"BA221","request":"GET /api/users/73/contributions"}
{"time":"2009-05-21T08:00:15.900","client_ip":"121.93.131.111","account_code":"2A2AC","request":"GET /api/users/18"}
{"time":"2009-05-21T08:00:16.100","client_ip":"58.116.85.49","account_code":"BA221","request":"GET /api/categories"}
{"time":"2009-05-21T08:00:17.100","client_ip":"58.116.85.49","account_code":"BA221","request":"GET /api/articles"}
{"time":"2009-05-21T08:00:20.800","client_ip":"50.142.218.94","account_code":"1B3B3","request":"GET /api/categories"}
{"time":"2009-05-21T08:00","client_ip":"83.237.12.225","account_code":"1BB3B","request":"GET /api/articles/56/contributors"}
{"time":"2009-05-21T08:00:21.300","client_ip":"50.142.218.94","account_code":"1B3B3","request":"GET /api/articles/42"}
```