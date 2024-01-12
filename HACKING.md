# Development

## Requirements
The following dependencies should be installed on your system:

1. [Python](https://www.python.org/)

A Python toolchain should be installed on your system. You can use [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions. The project template uses Python 3.10, but you
can use any Python version that is compatible with the dependencies.

2. [PDM](https://pdm-project.org/latest/)

PDM is used for building, testing and managing dependencies. You can install PDM via

```bash
curl -sSL https://pdm-project.org/install-pdm.py | python3 -
```

or refer to the [official documentation](https://pdm-project.org/latest/#installation)
for alternative installation methods.

3. [Singularity](https://docs.sylabs.io/guides/latest/user-guide/index.html) and [Docker](docker.com)

Singularity and Docker is needed for building the container image. The container is used
for building a runtime environment that allows you to run your application on the HPC cluster.
If you are not using the HPC cluster, you can skip this step.

## Local development
You can install the dependencies via

```bash
pdm install
```

You can run the application via

```bash
pdm run python <script>
```

Alternatively, activate the virtual environment via
```bash
eval $(pdm venv activate)
```
This allows you to drop the pdm prefix when running commands.

Run the tests via
```bash
pdm run test
```

Run linter and formatter via
```bash
pdm run lint
pdm run format
```

Install pre-commit hooks
```bash
pdm run pre-commit install
```

## Building the container images
Containers are used for running your application on the HPC cluster.
Unlike typical singularity tutorial, we recommend building the container image
via docker and converting that image to a singularity image. This way, we can leverage
docker's caching mechanism to speed up the build process.

Build a docker image with
```bash
docker build -t project_name .
```

You can test your application inside the docker container via
```bash
docker run \
    --mount=type=bind,source=$PWD,target=/workspace \
    --gpus all \
    --workdir=/workspace \
    --rm \
    -it \
    project_name bash
```
Note that pdm is not installed in the container as it is development dependency.
Also, if you docker with GPUs, you need to install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker).


You can then convert the docker image to singularity image via
```bash
singularity build project_name.sif docker-daemon://project_name:latest
```

Test that your singularity image works by opening a shell.
```bash
singularity shell --nv project_name.sif
```

## Launch the application on the HPC cluster
We use [LXM3](https://github.com/ethanluoyc/lxm3/tree/main) for automating the job
submission process. A basic launcher script has been provided. You can modify the
launcher script to suit your needs. If it is the first time you are using LXM3, you
should create a configuration file. Refer to the examples in
(https://github.com/ethanluoyc/lxm3/tree/main/examples/jax_gpu) for details on how to
set up a configuration file that you may use for interacting with the UCL HPC cluster.

You can test your LXM3 setup locally with
```bash
pdm run lxm3 launch lxm3_launcher.py \
    --entrypoint project_template.main \
    --container $PWD/project_name.sif
```

Once you are sure that your jobs can be launched locally, you can submit your job to
the HPC cluster by appending the `--launch_on_cluster` flag to the command above.

## Additional Useful Tools
1. [direnv](https://direnv.net/): direnv is an environment switcher for the shell. It knows how to hook into bash, zsh, tcsh, fish shell and elvish to load or unload environment variables depending on the current directory. This allows project-specific environment variables without cluttering the "~/.profile" file.
