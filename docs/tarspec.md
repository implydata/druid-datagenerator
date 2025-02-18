## Generation targets

Targets are the output locations for your data generation jobs.

| Field | Description | Possible values | Required? |
|---|---|---|---|
| [`type`](#target-types) | The type of target. | [`stdout`](#stdout) [`file`](#file) [`kafka`](#kafka) [`confluent`](#confluent) | Yes |
| Options | Additional fields that configure the target for the data, depending on the `type` selected. | | Dependent on `type`. |

From the command line, use the `-o` flag to set what target configuration file to use.

When using the API, wrap the target configuration inside an object called `target`.

### Target types

Each target type has fields that specify the behavior required.

#### `stdout`

Print events to standard out.

```
{
  "type": "stdout"
}
```

#### `file`

Write events to the specified file.

```
{
  "type": "file",
  "path": "<filename goes here>"
}
```

Where:
- <i>path</i> is the path and file name

#### `kafka`

Write events to an Apache Kafka topic.

```
{
  "type": "kafka",
  "endpoint": "<ip address and optional port>",
  "topic": "<topic name>",
  "topic_key": [<list of key fields>],
  "security_protocol": "<protocol designation>",
  "compression_type": "<compression type designation>"
}
```

Where:
- <i>endpoint</i> is the IP address and optional port number (e.g., "127.0.0.1:9092") - if the port is omitted, 9092 is used
- <i>topic</i> is the topic name as a string
- <i>topic_key</i> (optional) is the list of generated fields used to build the key for each message
- <i>security_protocol</i> (optional) a protocol specifier ("PLAINTEXT" (default if omitted), "SSL", "SASL_PLAINTEXT", "SASL_SSL")
- <i>compression_type</i> (optional) a compression specifier ("gzip", "snappy", "lz4") - if omitted, no compression is used

#### `confluent`

Write events to a Confluent Cloud topic.

```
{
  "type": "confluent",
  "servers": "<bootstrap servers>",
  "topic": "<topic name>",
  "topic_key": [<list of key fields>],
  "username": "<username>",
  "password": "<password>"
}
```

Where:
- <i>servers</i> is the confluent servers (e.g., "pkc-lzvrd.us-west4.gcp.confluent.cloud:9092")
- <i>topic</i> is the topic name as a string
- <i>topic_key</i> (optional) is the list of generated fields used to build the key for each message
- <i>username</i> cluster API key
- <i>password</i> cluster API secret

