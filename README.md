# 1.0. Setup for local development

This project uses Poetry (& pyenv to some degree) to ensure that python environments are compartmentalised to one project at a time.

## 1.1 pyenv

We strongly recommend you install [pyenv](https://github.com/pyenv/pyenv). This will let you have multiple versions of python on your system easily.

```bash
pyenv version 3.12.1
```

### 1.1.1 pyenv install MacOS

```
brew update
brew install pyenv
```

### 1.1.2 pyenv - Linux

```
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc
```

## 1.2 Installing on MacOS

```shell
brew update
brew install pyenv openssl
pyenv install 3.12.1
curl -sSL https://install.python-poetry.org | python3 -
poetry shell
poetry install
```

hint: _As much as possible, please try to keep the service running locally. This makes it easier for folks on other platforms (ie. ARM64) to get it running locally._

## 1.3 Installing on Linux

### 1.3.1 Install Linux common libraries

```
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
sudo apt install -y git openssl
```

### 1.3.2 Python + pip + Poetry versions

```
pyenv install 3.12.1
curl -sSL https://install.python-poetry.org | python3 -
cd apolo-task
poetry shell
poetry install
```

# 2.0 Installing docker

Based on [docker documentation](https://docs.docker.com/desktop/install/mac-install/) which also requires downloading the `Docker.dmg` installer

## 2.1 Docker on MacOS

```
softwareupdate --install-rosetta
sudo hdiutil attach ~/Desktop/Docker.dmg # or whatever directory it is downloaded in
sudo /Volumes/Docker/Docker.app/Contents/MacOS/install --accept-license
sudo hdiutil detach /Volumes/Docker
# run Docker Desktop manually to go through permissions settings and enable `docker` command line usage
docker version
```

## 2.2 Docker on Linux

**reference:** [Docker in Linux](https://docs.docker.com/engine/install/ubuntu/)

```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

note: be slightly wary of the update to your apt sources.list.d, I had to used the previous release name, e.g. `jammy` instead of `vera` for my linux install

# 3.0 Installing pre-commit

We use commit hooks to run a bunch of checks (typing, lint etc) which can be done locally to save debug time when the branch hits git.

## 3.1 MacOS pre-commit

```
brew install pre-commit
cd apolo-task
pre-commit install
```

## 3.2 Linux pre-commit

```
pip install pre-commit
cd apolo-task
pre-commit install
```

note: before issuing `pre-commit install`, make sure you are in the GIT repo directory, e.g. `cd apolo-task`

# 4.0 Run locally

Assuming you have all installations above configured

## 4.1 Run locally

```
docker-compose up -d --build
```

API should available here - http://localhost:3000/docs

The resource based (vCPU and memory) job scheduler is enabled by default.
To disable go to the `config.py` and update `DISABLE_RESOURCES_CHECKS` value or do the same in `.env` file.

## 4.2 Local start up message

You should see `INFO: Application startup complete` in the terminal

# 5.0 Configuration

We use the `pydantic` [baseconfig](https://pydantic-docs.helpmanual.io/usage/settings) system for managing configuration. Here, configuration can
be derived from a few places, in the following order.

1. ENV vars
2. the defaults stored in [config.py](app/config.py)

# 6.0 Development / Debugging

## 6.1 Tests

**Run tests**

```bash
coverage run -m pytest  -v -s
```

## 6.2 Test cases

### Create nodes:
```shell
curl -X 'POST' \
  'http://localhost:3000/api/v1/nodes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "max_concurrent_jobs": 1,
    "max_total_jobs": 2,
    "vcpu_units": 50,
    "memory": 100000
  },
  {
    "max_concurrent_jobs": 3,
    "max_total_jobs": 10,
    "vcpu_units": 50,
    "memory": 100000
  }
]'
```

### Submit batch of jobs:
```shell
curl -X 'POST' \
  'http://localhost:3000/api/v1/jobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "total_run_time": 600000,
    "vcpu_units": 1,
    "memory": 1000
  },
  {
    "total_run_time": 50000,
    "vcpu_units": 1,
    "memory": 1000
  },
  {
    "total_run_time": 50000,
    "vcpu_units": 1,
    "memory": 1000
  },
  {
    "total_run_time": 50000,
    "vcpu_units": 1,
    "memory": 1000
  },
  {
    "total_run_time": 50000,
    "vcpu_units": 1,
    "memory": 1000
  },
  {
    "total_run_time": 50000,
    "vcpu_units": 1,
    "memory": 1000
  },
  {
    "total_run_time": 50000,
    "vcpu_units": 1,
    "memory": 1000
  }
]'
```

Expected output:
```shell
[
    {
        "max_concurrent_jobs": 1,
        "max_total_jobs": 2,
        "vcpu_units": 50,
        "memory": 100000,
        "id": "d2f9313c-f158-4e9a-ae3e-68adf64a6c7a",
        "jobs": [
            {
                "total_run_time": 600000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "9e35b5a6-fa1b-403c-852e-61e465b1b494",
                "node_id": "d2f9313c-f158-4e9a-ae3e-68adf64a6c7a",
                "node_thread_id": 0,
                "expected_to_start_at": "2024-08-21T14:21:40.285151",
                "expected_to_finish_at": "2024-08-21T14:31:40.285151",
                "status": "running"
            }
        ]
    },
    {
        "max_concurrent_jobs": 3,
        "max_total_jobs": 10,
        "vcpu_units": 50,
        "memory": 100000,
        "id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
        "jobs": [
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "73143bdd-b341-43e6-8808-dba9bd380597",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 0,
                "expected_to_start_at": "2024-08-21T14:21:40.285448",
                "expected_to_finish_at": "2024-08-21T14:22:30.285448",
                "status": "running"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "c6647ba9-3bc5-411e-9601-629ce860e356",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 1,
                "expected_to_start_at": "2024-08-21T14:21:40.288606",
                "expected_to_finish_at": "2024-08-21T14:22:30.288606",
                "status": "running"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "019fbd23-a0df-4ecc-b259-1bef23b257db",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 2,
                "expected_to_start_at": "2024-08-21T14:21:40.288795",
                "expected_to_finish_at": "2024-08-21T14:22:30.288795",
                "status": "running"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "7d49d68c-c9ca-48f5-9178-ab1373d3d007",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 0,
                "expected_to_start_at": "2024-08-21T14:22:30.285448",
                "expected_to_finish_at": "2024-08-21T14:23:20.285448",
                "status": "scheduled"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "92f03dd3-655c-4284-9c0d-ccab61fd0e2e",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 1,
                "expected_to_start_at": "2024-08-21T14:22:30.288606",
                "expected_to_finish_at": "2024-08-21T14:23:20.288606",
                "status": "scheduled"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "91831e2f-e7be-44e0-8f42-dc51d1d9fa0e",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 2,
                "expected_to_start_at": "2024-08-21T14:22:30.288795",
                "expected_to_finish_at": "2024-08-21T14:23:20.288795",
                "status": "scheduled"
            }
        ]
    }
]
```

### Remove node:

```shell
curl -X 'DELETE' \
  'http://localhost:3000/api/v1/nodes/<id of the node with single job>' \
  -H 'accept: */*'
```

Expected output:
```shell
[
    {
        "max_concurrent_jobs": 3,
        "max_total_jobs": 10,
        "vcpu_units": 50,
        "memory": 100000,
        "id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
        "jobs": [
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "73143bdd-b341-43e6-8808-dba9bd380597",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 0,
                "expected_to_start_at": "2024-08-21T14:21:40.285448",
                "expected_to_finish_at": "2024-08-21T14:22:30.285448",
                "status": "done"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "c6647ba9-3bc5-411e-9601-629ce860e356",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 1,
                "expected_to_start_at": "2024-08-21T14:21:40.288606",
                "expected_to_finish_at": "2024-08-21T14:22:30.288606",
                "status": "done"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "019fbd23-a0df-4ecc-b259-1bef23b257db",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 2,
                "expected_to_start_at": "2024-08-21T14:21:40.288795",
                "expected_to_finish_at": "2024-08-21T14:22:30.288795",
                "status": "done"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "7d49d68c-c9ca-48f5-9178-ab1373d3d007",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 0,
                "expected_to_start_at": "2024-08-21T14:22:30.285448",
                "expected_to_finish_at": "2024-08-21T14:23:20.285448",
                "status": "running"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "92f03dd3-655c-4284-9c0d-ccab61fd0e2e",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 1,
                "expected_to_start_at": "2024-08-21T14:22:30.288606",
                "expected_to_finish_at": "2024-08-21T14:23:20.288606",
                "status": "running"
            },
            {
                "total_run_time": 50000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "91831e2f-e7be-44e0-8f42-dc51d1d9fa0e",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 2,
                "expected_to_start_at": "2024-08-21T14:22:30.288795",
                "expected_to_finish_at": "2024-08-21T14:23:20.288795",
                "status": "running"
            },
            {
                "total_run_time": 600000,
                "vcpu_units": 1,
                "memory": 1000,
                "id": "9e35b5a6-fa1b-403c-852e-61e465b1b494",
                "node_id": "21869df5-f78b-4a8f-8d5b-d1785121127a",
                "node_thread_id": 0,
                "expected_to_start_at": "2024-08-21T14:23:20.285448",
                "expected_to_finish_at": "2024-08-21T14:33:20.285448",
                "status": "scheduled"
            }
        ]
    }
]
```
