#
# DruidDataDriver - generates JSON records as a workload for Apache Druid.
#

import argparse
import dateutil.parser
from datetime import datetime, timedelta
import json
from kafka import KafkaProducer
import numpy as np
import random
from sortedcontainers import SortedList
import string
import sys
import threading
import time

############################################################################
#
# DruidDataDriver simulates Druid workloads by producing JSON records.
# Use a JSON config file to describe the characteristics of the workload
# you want to simulate.
#
# Run the program as follows:
# python DruidDataDriver.py <config file name> <options>
# Options include:
# -n <total number of records to generate>
# -t <duration for generating records>
#
# See the associated documentation for the format of the config file.
#
############################################################################


#
# Parse the command line
#

parser = argparse.ArgumentParser(description='Generates JSON records as a workload for Apache Druid.')
#parser.add_argument('config_file', metavar='<config file name>', help='the workload config file name')
parser.add_argument('-f', dest='config_file', nargs='?', help='the workload config file name')
parser.add_argument('-t', dest='time', nargs='?', help='the script runtime (may not be used with -n)')
parser.add_argument('-n', dest='n_recs', nargs='?', help='the number of records to generate (may not be used with -t)')
parser.add_argument('-s', dest='time_type', nargs='?', const='SIM', default='REAL', help='simulate time (default is real, not simulated)')

args = parser.parse_args()

config_file_name = args.config_file
runtime = args.time
total_recs = None
if args.n_recs is not None:
    total_recs = int(args.n_recs)
time_type = args.time_type

if (runtime is not None) and (total_recs is not None):
    print("Use either -t or -n, but not both")
    parser.print_help()
    exit()


if config_file_name:
    with open(config_file_name, 'r') as f:
        config = json.load(f)
else:
    config = json.load(sys.stdin)

class FutureEvent:
    def __init__(self, t):
        self.t = t
        self.name = threading.current_thread().name
        self.event = threading.Event()
    def get_time(self):
        return self.t
    def get_name(self):
        return self.name
    def __lt__(self, other):
        return self.t < other.t
    def __eq__(self, other):
        return self.t == other.t
    def __str__(self):
        return 'FutureEvent('+self.name+', '+str(self.t)+')'
    def pause(self):
        #print(self.name+" pausing")
        self.event.clear()
        self.event.wait()
    def resume(self):
        #print(self.name+" resuming")
        self.event.set()

class Clock:
    sim_time = datetime.now()
    future_events = SortedList()
    active_threads = 0
    lock = threading.Lock()
    sleep_lock = threading.Lock()

    def __init__(self, time_type):
        self.time_type = time_type

    def __str__(self):
        s = 'Clock(time='+str(self.sim_time)
        for e in self.future_events:
            s += ', '+str(e)
        s += ')'
        return s

    def activate_thread(self):
        if self.time_type == 'SIM':
            self.lock.acquire()
            self.active_threads += 1
            self.lock.release()

    def deactivate_thread(self):
        if self.time_type == 'SIM':
            self.lock.acquire()
            self.active_threads -= 1
            self.lock.release()

    def end_thread(self):
        if self.time_type == 'SIM':
            self.lock.acquire()
            self.active_threads -= 1
            if len(self.future_events) > 0:
                self.remove_event().resume()
            self.lock.release()

    def release_all(self):
        if self.time_type == 'SIM':
            self.lock.acquire()
            #print('release_all - active_threads = '+str(self.active_threads))
            for e in self.future_events:
                e.resume()
            self.lock.release()

    def add_event(self, future_t):
        this_event = FutureEvent(future_t)
        self.future_events.add(this_event)
        #print('add_event (after) '+threading.current_thread().name+' - '+str(self))
        return this_event

    def remove_event(self):
        #print('remove_event (before) '+threading.current_thread().name+' - '+str(self))
        next_event = self.future_events[0]
        self.future_events.remove(next_event)
        return next_event

    def pause(self, event):
        self.active_threads -= 1
        self.lock.release()
        event.pause()
        self.lock.acquire()
        self.active_threads += 1

    def resume(self, event):
        event.resume()

    def now(self):
        if time_type == 'SIM':
            t = self.sim_time
        else:
            t = datetime.now()
        return t

    def sleep(self, delta):
        if self.time_type == 'SIM': # Simulated time
            self.lock.acquire()
            #print(threading.current_thread().name+" begin sleep "+str(self.sim_time)+" + "+str(delta))
            this_event = self.add_event(self.sim_time + timedelta(seconds=delta))
            #print(threading.current_thread().name+" active threads "+str(self.active_threads))
            if self.active_threads == 1:
                next_event = self.remove_event()
                if str(this_event) != str(next_event):
                    self.resume(next_event)
                    #print(threading.current_thread().name+" start pause if")
                    self.pause(this_event)
                    #print(threading.current_thread().name+" end pause if")
            else:
                #print(threading.current_thread().name+" start pause else")
                self.pause(this_event)
                #print(threading.current_thread().name+" end pause else")
            self.sim_time = this_event.get_time()
            #print(threading.current_thread().name+" end sleep "+str(self.sim_time))
            self.lock.release()

        else: # Real time
            time.sleep(delta)

global_clock = Clock(time_type)

#
# Set up the target
#

class PrintStdout:
    lock = threading.Lock()
    def print(self, record):
        with self.lock:
            print(str(record))
            sys.stdout.flush()
    def __str__(self):
        return '#printStdout()'

class PrintFile:
    f = None
    def __init__(self, file_name):
        self.file_name = file_name
        self.f = open(file_name, 'w')
    def __str__(self):
        return 'PrintFile(file_name='+self.file_name+')'
    def print(self, record):
        self.f.write(str(record)+'\n')
        self.f.flush()

class PrintKafka:
    producer = None
    topic = None
    def __init__(self, endpoint, topic):
        self.endpoint = endpoint
        self.producer = KafkaProducer(bootstrap_servers=endpoint, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = topic
    def __str__(self):
        return 'PrintKafka(endpoint='+self.endpoint+', topic='+self.topic+')'
    def print(self, record):
        self.producer.send(self.topic, json.loads(str(record)))

target = config['target']

if target['type'].lower() == 'stdout':
    target_printer = PrintStdout()
elif target['type'].lower() == 'file':
    path = target['path']
    if path is None:
        print('Error: File target requires a path item')
        exit()
    target_printer = PrintFile(path)
elif target['type'].lower() == 'kafka':
    endpoint = target['endpoint']
    topic = target['topic']
    if endpoint is None:
        print('Error: Kafka target requires an endpoint item')
        exit()
    if topic is None:
        print('Error: Kafka target requires a topic item')
        exit()
    target_printer = PrintKafka(endpoint, topic)
else:
    print('Error: Unknown target type "'+target['type']+'"')
    exit()

#sys.stderr.write('target='+str(target_printer)+'\n')

#
# Handle distributions
#

class DistConstant:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'DistConstant(value='+str(self.value)+')'
    def get_sample(self):
        return self.value

class DistUniform:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
    def __str__(self):
        return 'DistUniform(min_value='+str(self.min_value)+', max_value='+str(self.max_value)+')'
    def get_sample(self):
        n = np.random.uniform(self.min_value, self.max_value)
        return np.random.uniform(self.min_value, self.max_value+1)

class DistExponential:
    def __init__(self, mean):
        self.mean = mean
    def __str__(self):
        return 'DistExponential(mean='+str(self.mean)+')'
    def get_sample(self):
        return np.random.exponential(scale = self.mean)

class DistNormal:
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev
    def __str__(self):
        return 'DistNormal(mean='+str(self.mean )+', stddev='+str(self.stddev)+')'
    def get_sample(self):
        return np.random.normal(self.mean, self.stddev)

def parse_distribution(desc):
    dist_type = desc['type'].lower()
    dist_gen = None
    if dist_type == 'constant':
        value = desc['value']
        dist_gen = DistConstant(value)
    elif dist_type == 'uniform':
        min_value = desc['min']
        max_value = desc['max']
        dist_gen = DistUniform(min_value, max_value)
    elif dist_type == 'exponential':
        mean = desc['mean']
        dist_gen = DistExponential(mean)
    elif dist_type == 'normal':
        mean = desc['mean']
        stddev = desc['stddev']
        dist_gen = DistNormal(mean, stddev)
    else:
        print('Error: Unknown distribution "'+dist_type+'"')
        exit()
    return dist_gen

def parse_timestamp_distribution(desc):
    dist_type = desc['type'].lower()
    dist_gen = None
    if dist_type == 'constant':
        value = dateutil.parser.isoparse(desc['value']).timestamp()
        dist_gen = DistConstant(value)
    elif dist_type == 'uniform':
        min_value = dateutil.parser.isoparse(desc['min']).timestamp()
        max_value = dateutil.parser.isoparse(desc['max']).timestamp()
        dist_gen = DistUniform(min_value, max_value)
    elif dist_type == 'exponential':
        mean = dateutil.parser.isoparse(desc['mean']).timestamp()
        dist_gen = DistExponential(mean)
    elif dist_type == 'normal':
        mean = desc[dateutil.parser.isoparse(desc['mean']).timestamp()]
        stddev = desc['stddev']
        dist_gen = DistNormal(mean, stddev)
    else:
        print('Error: Unknown distribution "'+dist_type+'"')
        exit()
    return dist_gen

#
# Set up the interarrival rate
#

rate = config['interarrival']
rate_delay = parse_distribution(rate)

#sys.stderr.write('rate_delay='+str(rate_delay)+'\n')

#
# Set up the dimensions for the emitters (see below)
# There is one element class for each dimension type. This code creates a list of
# elements and then runs through the list to create a single record.
# Notice that the get_json_field_string() method produces the JSON dimension
# field object based on the dimension configuration.
# The get_stochastic_value() method is like a private method used to get a random
# idividual value.
#

class ElementNow: # The __time dimension
    def __str__(self):
        return 'ElementNow()'
    def get_json_field_string(self):
        now = global_clock.now().isoformat()
        return '"__time":"'+now+'"'

class ElementEnum: # enumeration dimensions
    def __init__(self, desc):
        self.name = desc['name']
        if 'percent_nulls' in desc.keys():
            self.percent_nulls = desc['percent_nulls'] / 100.0
        else:
            self.percent_nulls = 0.0
        if 'percent_missing' in desc.keys():
            self.percent_missing = desc['percent_missing'] / 100.0
        else:
            self.percent_missing = 0.0
        self.cardinality = desc['values']
        if 'cardinality_distribution' not in desc.keys():
            print('Element '+self.name+' specifies a cardinality without a cardinality distribution')
            exit()
        self.cardinality_distribution = parse_distribution(desc['cardinality_distribution'])

    def __str__(self):
        return 'ElementEnum(name='+self.name+', cardinality='+str(self.cardinality)+', cardinality_distribution='+str(self.cardinality_distribution)+')'

    def get_stochastic_value(self):
        index = int(self.cardinality_distribution.get_sample())
        if index < 0:
            index = 0
        if index >= len(self.cardinality):
            index = len(self.cardinality)-1
        return self.cardinality[index]

    def get_json_field_string(self):
        if random.random() < self.percent_nulls:
            s = '"'+self.name+'": null'
        else:
            s = '"'+self.name+'":"'+str(self.get_stochastic_value())+'"'
        return s

    def is_missing(self):
        return random.random() < self.percent_missing

class ElementVariable: # Variable dimensions
    def __init__(self, desc):
        self.name = desc['name']
        self.variable_name = desc['variable']

    def __str__(self):
        return 'ElementVariable(name='+self.name+', value='+self.variable_name+')'

    def get_json_field_string(self, variables): # NOTE: because of timing, this method has a different signature than the other elements
        value = variables[self.variable_name]
        return '"'+self.name+'":"'+str(value)+'"'


class ElementBase: # Base class for the remainder of the dimensions
    def __init__(self, desc):
        self.name = desc['name']
        if 'percent_nulls' in desc.keys():
            self.percent_nulls = desc['percent_nulls'] / 100.0
        else:
            self.percent_nulls = 0.0
        if 'percent_missing' in desc.keys():
            self.percent_missing = desc['percent_missing'] / 100.0
        else:
            self.percent_missing = 0.0
        cardinality = desc['cardinality']
        if cardinality == 0:
            self.cardinality = None
            self.cardinality_distribution = None
        else:
            self.cardinality = []
            if 'cardinality_distribution' not in desc.keys():
                print('Element '+self.name+' specifies a cardinality without a cardinality distribution')
                exit()
            self.cardinality_distribution = parse_distribution(desc['cardinality_distribution'])
            for i in range(cardinality):
                Value = None
                while True:
                    value = self.get_stochastic_value()
                    if value not in self.cardinality:
                        break
                self.cardinality.append(value)


    def get_stochastic_value(self):
        pass

    def get_json_field_string(self):
        if random.random() < self.percent_nulls:
            s = '"'+self.name+'": null'
        else:
            if self.cardinality is None:
                value = self.get_stochastic_value()
            else:
                index = int(self.cardinality_distribution.get_sample())
                if index < 0:
                    index = 0
                if index >= len(self.cardinality):
                    index = len(self.cardinality)-1
                value = self.cardinality[index]
            s = '"'+self.name+'":'+str(value)
        return s

    def is_missing(self):
        return random.random() < self.percent_missing


class ElementString(ElementBase):
    def __init__(self, desc):
        self.length_distribution = parse_distribution(desc['length_distribution'])
        if 'chars' in desc:
            self.chars = desc['chars']
        else:
            self.chars = string.printable
        super().__init__(desc)

    def __str__(self):
        return 'ElementString(name='+self.name+', cardinality='+str(self.cardinality)+', cardinality_distribution='+str(self.cardinality_distribution)+', chars='+self.chars+')'

    def get_stochastic_value(self):
        length = int(self.length_distribution.get_sample())
        return ''.join(random.choices(list(self.chars), k=length))

    def get_json_field_string(self):
        if random.random() < self.percent_nulls:
            s = '"'+self.name+'": null'
        else:
            if self.cardinality is None:
                value = self.get_stochastic_value()
            else:
                index = int(self.cardinality_distribution.get_sample())
                if index < 0:
                    index = 0
                if index >= len(self.cardinality):
                    index = len(self.cardinality)-1
                value = self.cardinality[index]
            s = '"'+self.name+'":"'+str(value)+'"'
        return s

class ElementInt(ElementBase):
    def __init__(self, desc):
        self.value_distribution = parse_distribution(desc['distribution'])
        super().__init__(desc)

    def __str__(self):
        return 'ElementInt(name='+self.name+', value_distribution='+str(self.value_distribution)+', cardinality='+str(self.cardinality)+', cardinality_distribution='+str(self.cardinality_distribution)+')'

    def get_stochastic_value(self):
        return int(self.value_distribution.get_sample())

class ElementFloat(ElementBase):
    def __init__(self, desc):
        self.value_distribution = parse_distribution(desc['distribution'])
        super().__init__(desc)

    def __str__(self):
        return 'ElementFloat(name='+self.name+', value_distribution='+str(self.value_distribution)+', cardinality='+str(self.cardinality)+', cardinality_distribution='+str(self.cardinality_distribution)+')'

    def get_stochastic_value(self):
        return float(self.value_distribution.get_sample())

class ElementTimestamp(ElementBase):
    def __init__(self, desc):
        self.name = desc['name']
        self.value_distribution = parse_timestamp_distribution(desc['distribution'])
        if 'percent_nulls' in desc.keys():
            self.percent_nulls = desc['percent_nulls'] / 100.0
        else:
            self.percent_nulls = 0.0
        if 'percent_missing' in desc.keys():
            self.percent_missing = desc['percent_missing'] / 100.0
        else:
            self.percent_missing = 0.0
        cardinality = desc['cardinality']
        if cardinality == 0:
            self.cardinality = None
            self.cardinality_distribution = None
        else:
            if 'cardinality_distribution' not in desc.keys():
                print('Element '+self.name+' specifies a cardinality without a cardinality distribution')
                exit()
            self.cardinality = []
            self.cardinality_distribution = parse_distribution(desc['cardinality_distribution'])
            for i in range(cardinality):
                Value = None
                while True:
                    value = self.get_stochastic_value()
                    if value not in self.cardinality:
                        break
                self.cardinality.append(value)

    def __str__(self):
        return 'ElementTimestamp(name='+self.name+', value_distribution='+str(self.value_distribution)+', cardinality='+str(self.cardinality)+', cardinality_distribution='+str(self.cardinality_distribution)+')'

    def get_stochastic_value(self):
        return datetime.fromtimestamp(self.value_distribution.get_sample()).isoformat()

    def get_json_field_string(self):
        if random.random() < self.percent_nulls:
            s = '"'+self.name+'": null'
        else:
            if self.cardinality is None:
                value = self.get_stochastic_value()
            else:
                index = int(self.cardinality_distribution.get_sample())
                if index < 0:
                    index = 0
                if index >= len(self.cardinality):
                    index = len(self.cardinality)-1
                value = self.cardinality[index]
            s = '"'+self.name+'":"'+str(value)+'"'
        return s

    def is_missing(self):
        return random.random() < self.percent_missing

class ElementIPAddress(ElementBase):
    def __init__(self, desc):
        self.value_distribution = parse_distribution(desc['distribution'])
        super().__init__(desc)

    def __str__(self):
        return 'ElementIPAddress(name='+self.name+', value_distribution='+str(self.value_distribution)+', cardinality='+str(self.cardinality)+', cardinality_distribution='+str(self.cardinality_distribution)+')'

    def get_stochastic_value(self):
        value = int(self.value_distribution.get_sample())
        return str((value & 0xFF000000) >> 24)+'.'+str((value & 0x00FF0000) >> 16)+'.'+str((value & 0x0000FF00) >> 8)+'.'+str(value & 0x000000FF)

    def get_json_field_string(self):
        if random.random() < self.percent_nulls:
            s = '"'+self.name+'": null'
        else:
            if self.cardinality is None:
                value = self.get_stochastic_value()
            else:
                index = int(self.cardinality_distribution.get_sample())
                if index < 0:
                    index = 0
                if index >= len(self.cardinality):
                    index = len(self.cardinality)-1
                value = self.cardinality[index]
            s = '"'+self.name+'":"'+str(value)+'"'
        return s

def parse_element(desc):
    if desc['type'].lower() == 'enum':
        el = ElementEnum(desc)
    elif desc['type'].lower() == 'string':
        el = ElementString(desc)
    elif desc['type'].lower() == 'int':
        el = ElementInt(desc)
    elif desc['type'].lower() == 'float':
        el = ElementFloat(desc)
    elif desc['type'].lower() == 'timestamp':
        el = ElementTimestamp(desc)
    elif desc['type'].lower() == 'ipaddress':
        el = ElementIPAddress(desc)
    elif desc['type'].lower() == 'variable':
        el = ElementVariable(desc)
    else:
        print('Error: Unknown dimension type "'+desc['type']+'"')
        exit()
    return el


def get_variables(desc):
    elements = []
    for element in desc:
        el = parse_element(element)
        elements.append(el)
    return elements

def get_dimensions(desc):
    global time_gen
    elements = get_variables(desc)
    elements.insert(0, ElementNow())
    return elements

#
# Set up emitters list
#

emitters = {}
for emitter in config['emitters']:
    name = emitter['name']
    dimensions = get_dimensions(emitter['dimensions'])
    emitters[name] = dimensions

#sys.stderr.write('emitters='+str(['(name='+str(key)+', dimensions='+str([str(e) for e in emitters[key]])+')' for key in emitters])+'\n')

#
# Set up the state machine
#

class Transition:
    def __init__(self, next_state, probability):
        self.next_state = next_state
        self.probability = probability

    def __str__(self):
        return 'Transition(next_state='+str(self.next_state)+', probability='+str(self.probability)+')'

def parse_transitions(desc):
    transitions = []
    for trans in desc:
        next_state = trans['next']
        probability = float(trans['probability'])
        transitions.append(Transition(next_state, probability))
    return transitions

class State:
    def __init__(self, name, dimensions, delay, transistions, variables):
        self.name = name
        self.dimensions = dimensions
        self.delay = delay
        self.transistion_states = [t.next_state for t in transitions]
        self.transistion_probabilities = [t.probability for t in transitions]
        self.variables = variables

    def __str__(self):
        return 'State(name='+self.name+', dimensions='+str([str(d) for d in self.dimensions])+', delay='+str(self.delay)+', transistion_states='+str(self.transistion_states)+', transistion_probabilities='+str(self.transistion_probabilities)+'variables='+str([str(v) for v in self.variables])+')'

    def get_next_state_name(self):
        return random.choices(self.transistion_states, weights=self.transistion_probabilities, k=1)[0]


state_desc = config['states']
initial_state = None
states = {}
for state in state_desc:
    name = state['name']
    emitter_name = state['emitter']
    if 'variables' not in state.keys():
        variables = []
    else:
        variables = get_variables(state['variables'])
    dimensions = emitters[emitter_name]
    delay = parse_distribution(state['delay'])
    transitions = parse_transitions(state['transitions'])
    this_state = State(name, dimensions, delay, transitions, variables)
    states[name] = this_state
    if initial_state == None:
        initial_state = this_state

#sys.stderr.write('states='+str(['('+str(key)+':'+str(states[key])+')' for key in states])+'\n')

#
# Run the driver
#

record_count = 0

def create_record(dimensions, variables):
    json_string = '{'
    for element in dimensions:
        if isinstance(element, ElementVariable):
            json_string += element.get_json_field_string(variables) + ','
        else:
            if isinstance(element, ElementNow) or not element.is_missing():
                json_string += element.get_json_field_string() + ','
    json_string = json_string[:-1] + '}'
    return json_string

thread_end_event = threading.Event()

def set_variable_values(variables, dimensions):
    for d in dimensions:
        variables[d.name] = d.get_stochastic_value()

def worker_thread(target_printer, states, initial_state):
    # Process the state machine using worker threads
    global record_count
    global total_recs
    global global_clock
    #print('Thread '+threading.current_thread().name+' starting...')
    global_clock.activate_thread()
    current_state = initial_state
    variables = {}
    while True:
        set_variable_values(variables, current_state.variables)
        record = create_record(current_state.dimensions, variables)
        target_printer.print(record)
        record_count += 1
        if total_recs is not None and record_count >= total_recs:
            thread_end_event.set()
            break
        delta = float(current_state.delay.get_sample())
        global_clock.sleep(delta)
        if total_recs is not None and record_count >= total_recs:
            thread_end_event.set()
            break
        next_state_name = current_state.get_next_state_name()
        if next_state_name.lower() == 'stop':
            break
        current_state = states[next_state_name]

    #print('Thread '+threading.current_thread().name+' done!')
    global_clock.end_thread()

def spawning_thread(target_printer, rate_delay, states, initial_state):
    global thread_end_event
    global global_clock
    #print('Thread '+threading.current_thread().name+' starting...')
    global_clock.activate_thread()
    # Spawn the workers in a separate thread so we can stop the whole thing in the middle of spawning if necessary
    count = 0
    while not thread_end_event.is_set():
        thread_name = 'W'+str(count)

        count += 1
        t = threading.Thread(target=worker_thread, args=(target_printer, states, initial_state, ), name=thread_name, daemon=True)
        t.start()
        global_clock.sleep(float(rate_delay.get_sample()))
    global_clock.end_thread()
    #print('Thread '+threading.current_thread().name+' done!')

thrd = threading.Thread(target=spawning_thread, args=(target_printer, rate_delay, states, initial_state, ), name='Spawning', daemon=True)
thrd.start()

if runtime is not None:
    if runtime[-1].lower() == 's':
        t = int(runtime[:-1])
    elif runtime[-1].lower() == 'm':
        t = int(runtime[:-1]) * 60
    elif runtime[-1].lower() == 'h':
        t = int(runtime[:-1]) * 60 * 60
    else:
        print('Error: Unknown runtime value"'+runtime+'"')
        exit()
    global_clock.activate_thread()
    global_clock.sleep(t)
    global_clock.deactivate_thread()
elif total_recs is not None:
    thread_end_event.wait()
    global_clock.release_all()
else:
    while True:
        time.sleep(60)
