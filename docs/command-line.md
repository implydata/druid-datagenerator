## Run from the command line

The Druid Data Driver is a python script that simulates a workload that generates data for Druid ingestion.
You can use a JSON config file to describe the characteristics of the workload you want the Druid Data Driver to simulate.
The script uses this config file to generate JSON records.

```
python generator/DruidDataDriver.py
		-o <JSON target definition>
		[-f <JSON configuration>]
		[-s <timestamp>]
		[{-n <int> | -t <timestamp>}]
```

## Prerequities

The data generator requires Python 3.

```
apt-get install python3
apt-get update
apt-get install -y python3-pip
```

The data generator has dependencies on a number of modules. Run the following commands to prepare your Python environment.

```
pip install confluent-kafka
pip install python-dateutil
pip install kafka-python
pip install numpy
pip install sortedcontainers
```

## Command line options

| Argument | Description | Required? |
|---|---|---|
| [`-f`](#select-the-config-file) | The name of the [configuration](config.md) to use. All configuration files are stored in the `config_file` folder. | No |
| [`-o`](#select-the-target-definition-file) | The name of the file that contains the [target definition](#target.md). | Yes |
| [`-s`](#set-a-start-time) | Simulate the start time for `__time`. | No |
| [`-n`](#set-generation-limit) | The number of records to generate. Must not be used in combinaton with `-t`. | No |
| [`-t`](#set-generation-limit) | The length of time to create records for. Must not be used in combination with `-n`. | No |

### Select the config file

Every data generator run requires a [configuration file](#config.md).

When the `-f` option is used, a configuration file will be read from `./config_files`.

When the `-f` option is not used, the configuration will be read from `stdin`.

### Select the target definition file

Set the output of the data generator by setting the `target` object.

Use the _-o_ option to designate a target definition file name. The [target](./target.md) defines where the generated messages are sent.

### Set a start time

The _-s_ option tells the driver to use simulated time instead of wall clock time (the default).

The simulated clock starts at the time specified by the argument (or the current time if no argument is specified) and advances the simulated clock based on the generated events (i.e., records).

When used with the _-t_ option, the simulated clock simulates the duration. This option is useful for generating batch data as quickly as possible.

### Set generation limit

Use either `-n` or `-t` to limit how long generation executes for. If neither option is present, the script will run indefinitely.

#### Limit generation to a length of time

Time durations may be specified in terms of seconds, minutes or hours.

For example, specify 30 seconds as follows:

```
python generator/DruidDataDriver.py -c generator_config.json -o generator_output.json -t 30S
```

Specify 10 minutes as follows:

```
python generator/DruidDataDriver.py -c generator_config.json -o generator_output.json -t 10M
```

Or, specify 1 hour as follows:

```
python generator/DruidDataDriver.py -c generator_config.json -o generator_output.json -t 1H
```

#### Limit generation to a number of records

Use `-n` to limit generation to a number of records.

```
python generator/DruidDataDriver.py -c generator_config.json -o generator_output.json -n 1000
```