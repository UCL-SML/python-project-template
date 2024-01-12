# syntax=docker/dockerfile:1
FROM python:3.10-bookworm as base

# RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
# RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
#     --mount=type=cache,target=/var/lib/apt,sharing=locked \
#     export DEBIAN_FRONTEND=noninteractive \
#     && apt-get update \
#     && apt-get install -q -y --no-install-recommends \
#     curl git ffmpeg

RUN pip install -U pip setuptools wheel
RUN pip install pdm
COPY pyproject.toml pdm.lock /project/

WORKDIR /project
RUN pdm export -o /requirements.txt

FROM python:3.10-bookworm as prod

COPY --from=base /requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

RUN groupadd --gid 1000 app && useradd --uid 1000 --gid 1000 -m app

USER app
