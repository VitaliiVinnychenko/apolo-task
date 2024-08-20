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

## 4.2 Local start up message

You should see `INFO: Application startup complete` in the terminal

# 5.0 Configuration

We use the `pydantic` [baseconfig](https://pydantic-docs.helpmanual.io/usage/settings) system for managing configuration. Here, configuration can
be derived from a few places, in the following order.

1. ENV vars
2. the defaults stored in [config.py](backend/app/config.py)

# 6.0 Development / Debugging

## 6.1 Tests

**Run tests**

```bash
coverage run -m pytest  -v -s
```
