# servboard
A mini dashboard for showing a computer stats and services running on it.

## Installation

```
git clone https://github.com/vladcalin/servboard.git
python servboard/setup.py install
```

## Run

```
servboard --services_file=services.json
```

Where the ``services.json`` file conains a structure like this

```json
{
    "service_name": "http://localhost:8000",
    "service_2": "http://someotherlocaiton:9000",
    ...
}
```
