#!/usr/bin/env python3
# type: ignore
from absl import app
from absl import flags
from lxm3 import xm
from lxm3 import xm_cluster
from lxm3.contrib import ucl

_LAUNCH_ON_CLUSTER = flags.DEFINE_boolean(
    "launch_on_cluster", False, "Launch on cluster"
)
_USE_GPU = flags.DEFINE_boolean("use_gpu", False, "If set, use GPU")
_SINGULARITY_CONTAINER = flags.DEFINE_string(
    "container", None, "Path to singularity container"
)
_ENTRYPOINT = flags.DEFINE_string("entrypoint", None, "Entrypoint for experiment")
flags.mark_flags_as_required(["entrypoint"])


def main(_):
    with xm_cluster.create_experiment(experiment_title="basic") as experiment:
        if _USE_GPU.value:
            job_requirements = xm_cluster.JobRequirements(gpu=1, ram=8 * xm.GB)
        else:
            job_requirements = xm_cluster.JobRequirements(ram=8 * xm.GB)
        if _LAUNCH_ON_CLUSTER.value:
            # This is a special case for using SGE in UCL where we use generic
            # job requirements and translate to SGE specific requirements.
            # Non-UCL users, use `xm_cluster.GridEngine directly`.
            executor = ucl.UclGridEngine(
                job_requirements,
                walltime=10 * xm.Min,
            )
        else:
            executor = xm_cluster.Local(job_requirements)

        spec = xm_cluster.PythonPackage(
            # This is a relative path to the launcher that contains
            # your python package (i.e. the directory that contains pyproject.toml)
            path=".",
            # Entrypoint is the python module that you would like to
            # In the implementation, this is translated to
            #   python3 -m py_package.main
            entrypoint=xm_cluster.ModuleName(_ENTRYPOINT.value),
        )

        # Wrap the python_package to be executing in a singularity container.
        singularity_container = _SINGULARITY_CONTAINER.value

        # It's actually not necessary to use a container, without it, we
        # fallback to the current python environment for local executor and
        # whatever Python environment picked up by the cluster for GridEngine.
        # For remote execution, using the host environment is not recommended.
        # as you may spend quite some time figuring out dependency problems than
        # writing a simple Dockfiler/Singularity file.
        if singularity_container is not None:
            spec = xm_cluster.SingularityContainer(
                spec,
                image_path=singularity_container,
            )

        [executable] = experiment.package(
            [xm.Packageable(spec, executor_spec=executor.Spec())]
        )

        experiment.add(
            xm.Job(
                executable=executable,
                executor=executor,
                # You can pass additional arguments to your executable with args
                # This will be translated to `--seed 1`
                # Note for booleans we currently use the absl.flags convention
                # so {'gpu': False} will be translated to `--nogpu`
                # args={"seed": 1},
                # You can customize environment_variables as well.
                env_vars={"XLA_PYTHON_CLIENT_PREALLOCATE": "false"},
            )
        )


if __name__ == "__main__":
    app.run(main)
