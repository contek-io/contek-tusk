# Tusk Clickhouse Metric Writer

```contek-tusk``` is a metric writer built upon Clickhouse.

### 1. Connection Initialization

```python
import contek_tusk as tusk

tusk.init(host='localhost', user='tester', password='P@assw0rd')
```

### 2. Generic Metric

```python
from contek_tusk import metric

cpu_usage = metric(table='system.cpu')

cpu_usage.write({
    'region': 'Tokyo',
    'instance_id': 'ABC',
    'usage': 0.43
})

cpu_usage.write({
    'region': 'Seoul',
    'instance_id': 'XYZ',
    'usage': 0.22
})
```

```sql
SELECT * FROM system.cpu
```

| region | instance_id |                datetime | usage |
| ------ | ----------- | ----------------------- | ----- |
| Tokyo  | ABC         | 2022-03-10 06:42:42.746 |  0.43 |
| Seoul  | XYZ         | 2022-03-10 06:42:42.746 |  0.22 |

Note: the client will automatically use the first ```DateTime``` column to record current timestamp. Alternatively, it
can be explicitly specified:

```python
from contek_tusk import metric
from contek_tusk.table import Table

table = Table(database='system', table_name='cpu', time_column='datetime')
cpu_usage = metric(table)
```

### 3. Summing Counter

```python
from contek_tusk.counter import counter

counter = counter(table='download.quota_usage')

counter.count({
    'resource_id': 'ABC111',
    'requester_ip': '1.2.3.4'
})  # default count is 1

counter.count({
    'resource_id': 'ABC122',
    'requester_ip': '2.2.2.4'
}, 3)

counter.count({
    'resource_id': 'ABC111',
    'requester_ip': '1.2.3.4'
}, 4)  # the new count is 1 + 4 = 5

counter.count({
    'resource_id': 'ABC122',
    'requester_ip': '1.2.3.4'
}, 2)
```

```sql
SELECT * FROM download.quota_usage
```

| resource_id | requester_ip |                datetime | count |
| ----------- | ------------ | ----------------------- | ----- |
| ABC111      | 1.2.3.4      | 2022-03-10 06:42:48.411 |     5 |
| ABC122      | 1.2.3.4      | 2022-03-10 06:42:48.411 |     2 |
| ABC122      | 2.2.2.4      | 2022-03-10 06:42:48.411 |     3 |

Note: the client will automatically use the first ```Int``` or ```UInt``` column to record the count. Alternatively, it
can be explicitly specified:

```python
from contek_tusk.counter import counter

counter = counter(table='download.quota_usage', count_column='count')
```

### 4. Heartbeat Recorder

```python
from contek_tusk.heartbeat import init

init(table='maintenance.heartbeats', app_name='my_app')
```

After initialization, a recurring task starts in the background and sends a heartbeat to the database every 30 seconds.
The heartbeat cycle can be explicitly specified:

```python
from contek_tusk.heartbeat import init

init(table='maintenance.heartbeats', app_name='my_app', heartbeat_period=15)
```

If the application is running multiple recurring tasks. Their heartbeats can also be registered:

```python
from contek_tusk.heartbeat import beat

beat(task='scan_disk', heartbeat_period=60)
```

```sql
SELECT * FROM maintenance.heartbeats
```

|    app |      task |                datetime | sequence |
| -------| --------- | ----------------------- | -------- |
| my_app | main      | 2022-03-10 06:51:01.178 |        0 |
| my_app | main      | 2022-03-10 06:51:31.178 |        1 |
| my_app | main      | 2022-03-10 06:52:01.178 |        2 |
| my_app | scan_disk | 2022-03-10 06:52:04.215 |        0 |
| my_app | main      | 2022-03-10 06:52:31.178 |        3 |
| my_app | main      | 2022-03-10 06:53:01.178 |        4 |
| my_app | scan_disk | 2022-03-10 06:53:04.215 |        1 |

### 5.Logging

```python
import logging
from contek_tusk.logging import init

logger = logging.getLogger(__name__)
init(table='maintenance.logs', app_name='my_app')

logger.info('Hello world!')
logger.warning('Fire drill test.')
logger.error('This is real fire.')
try:
    raise ValueError('Guess what?')
except ValueError:
    logger.exception('Oh no!')
logger.critical('I give up.')
```

```sql
SELECT * FROM maintenance.logs
```

|    app |                datetime | level |     logger | line |      error |            message |  stacktrace |
| -------| ----------------------- | ----- | ---------- | ---- | ---------- | ------------------ | ----------- |
| my_app | 2022-03-10 08:53:03.558 |     4 | example.py |    7 |            |       Hello world! |             |
| my_app | 2022-03-10 08:53:03.558 |     3 | example.py |    8 |            |   Fire drill test. |             |
| my_app | 2022-03-10 08:53:03.558 |     2 | example.py |    9 |            | This is real fire. |             |
| my_app | 2022-03-10 08:53:03.558 |     2 | example.py |   13 | ValueError |             Oh no! | (traceback) |
| my_app | 2022-03-10 08:53:03.558 |     1 | example.py |   14 |            |         I give up. |             |

### 6. Full Initialization

#### Standard

```python
import contek_tusk as tusk
import contek_tusk.heartbeat as heartbeat
import contek_tusk.logging as logging

tusk.init(host='localhost', user='tester', password='P@assw0rd')
tusk.set_app_name('my_app')
heartbeat.init(table='maintenance.heartbeats')
logging.init(table='maintenance.logs')
```

#### YAML

```yaml
app: 'my_app'
host: 'localhost'
user: 'tester'
password: 'P@assw0rd'
heartbeat:
  database: 'maintenance'
  table: 'heartbeats'
logging:
  database: 'maintenance'
  table: 'logs'
```

```python
import contek_tusk.yaml as tusk_yaml

tusk_yaml.for_yaml_file('example.yml')
```

### 7. Example Table Schema

#### maintenance.heartbeats

```sql
CREATE TABLE IF NOT EXISTS maintenance.heartbeats
(
    `app` String, 
    `datetime` DateTime64(3),
    `task` String,
    `sequence` UInt32,
    `expiry` DateTime64
)
ENGINE = MergeTree()
ORDER BY
(
    `app`,
    `datetime`,
    `task`,
    `sequence`
)
TTL toDateTime(datetime) + INTERVAL 28 DAY DELETE;
```

#### maintenance.logs

```sql
CREATE TABLE IF NOT EXISTS maintenance.logs
(
    `app` String,
    `datetime` DateTime64(3),
    `level` Int8,
    `logger` String,
    `line` UInt32,
    `error` String,
    `message` String,
    `stacktrace` String
)
ENGINE = MergeTree()
ORDER BY
(
    `category`,
    `host`,
    `app`,
    `datetime`,
    `level`,
    `logger`,
    `line`,
    `error`
)
TTL toDateTime(datetime) + INTERVAL 7 DAY DELETE;
```

### 8. Customization

To write to tables with different schemas. Specify the column names in ``TuskHeartbeatConfig`` and
``TuskLoggingConfig``.