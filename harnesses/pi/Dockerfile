# syntax=docker/dockerfile:1
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# scion-base already ships node/npm (core-base is node:24-trixie-slim).
# pi needs node >= 20.6; fail the build early on an older base.
RUN node -e 'const [a,b]=process.versions.node.split(".").map(Number); if (a<20||(a===20&&b<6)) { console.error("pi needs node >= 20.6, found "+process.versions.node); process.exit(1) }'

# Install pi (pinned). Credentials are never baked in: provision.py writes
# ~/.pi/agent/{settings,models}.json at pre-start and the key comes from
# DEEPSEEK_API_KEY (or a scion-staged auth-file) at runtime.
ARG PI_VERSION=0.73.1
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc,required=false \
    npm install -g @mariozechner/pi-coding-agent@${PI_VERSION} \
  && npm cache clean --force \
  && pi --version

# Desk tooling for the SLDB_1 desks, so an executor does not build a venv in
# /tmp: pytest/pytest-xdist pinned to the SLDB_1 venv, dagster pinned to
# mepu's requirements.txt. scion-base has no pip, so it comes from apt.
# --ignore-installed: apt's python3-pip pulls dpkg-managed packages without a
# pip RECORD file (see harnesses/hermes/Dockerfile); the pip-installed set
# lands in /usr/local/lib/python3.X/dist-packages and shadows them.
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN --mount=type=secret,id=pipconf,target=/etc/pip.conf,required=false \
    pip install --no-cache-dir --break-system-packages --ignore-installed \
      pytest==9.2.0 pytest-xdist==3.8.0 dagster==1.13.24 \
  && python3 -c 'import pytest, xdist, dagster; print(pytest.__version__, dagster.__version__)'

RUN mkdir -p /home/scion/.pi/agent && \
  chown -R scion:scion /home/scion/.pi

CMD ["pi"]
