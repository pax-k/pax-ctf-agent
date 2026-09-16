ARG PYTHON_IMAGE=python@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
ARG KALI_IMAGE=kalilinux/kali-rolling@sha256:49d174981a2a211e76acdde22a2e4978ea19bc0433487292cd9ad865da24ee42
FROM ${PYTHON_IMAGE} AS python-runtime

FROM ${KALI_IMAGE}

ARG TARGETARCH
ARG HEXSTRIKE_REF=d689933ff579d839c676c82b231f8e98326c5f04
ARG LIBC_DATABASE_REF=b7e948f7324cde8ac5cdb26bc4d58fbeeb1fbb5c

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/ctf-adapter \
    PATH=/opt/dotnet:/opt/hexstrike-venv/bin:/usr/share/ghidra/support:${PATH} \
    HOME=/workbench/output/home \
    HEXSTRIKE_HOST=0.0.0.0 \
    HEXSTRIKE_PORT=8888 \
    PWNDBG_NO_AUTOUPDATE=1 \
    CTF_INPUT_ROOT=/workbench/input \
    CTF_OUTPUT_ROOT=/workbench/output \
    CTF_SCOPE_FILE=/workbench/input/scope.json

COPY container/hexstrike/packages/ /tmp/ctf-packages/

RUN find /tmp/ctf-packages -type f -name '*.txt' -print0 \
      | sort -z \
      | xargs -0 cat \
      | sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' \
      | sort -u > /tmp/ctf-apt-packages.txt \
    && apt-get update \
    && xargs -r apt-get install -y --no-install-recommends < /tmp/ctf-apt-packages.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/ctf-packages /tmp/ctf-apt-packages.txt

# HexStrike pins dependencies that do not support Kali's newest Python. Keep
# Kali's Python for packaged tools and use the pinned Python runtime for the
# HexStrike server and the local CTF adapter.
COPY --from=python-runtime /usr/local /usr/local
COPY requirements.hexstrike-core.txt /tmp/requirements.hexstrike-core.txt

RUN python3 -m venv /opt/hexstrike-venv \
    && /opt/hexstrike-venv/bin/python -m pip install --no-cache-dir --upgrade pip \
    && /opt/hexstrike-venv/bin/python -m pip install --no-cache-dir -r /tmp/requirements.hexstrike-core.txt \
    && rm -f /tmp/requirements.hexstrike-core.txt

RUN git init -q /opt/hexstrike \
    && git -C /opt/hexstrike remote add origin https://github.com/0x4m4/hexstrike-ai.git \
    && git -C /opt/hexstrike fetch -q --depth 1 origin "${HEXSTRIKE_REF}" \
    && git -C /opt/hexstrike checkout -q --detach FETCH_HEAD \
    && rm -rf /opt/hexstrike/.git \
    && git init -q /opt/libc-database \
    && git -C /opt/libc-database remote add origin https://github.com/niklasb/libc-database.git \
    && git -C /opt/libc-database fetch -q --depth 1 origin "${LIBC_DATABASE_REF}" \
    && git -C /opt/libc-database checkout -q --detach FETCH_HEAD \
    && rm -rf /opt/libc-database/.git

COPY container/hexstrike/requirements/ /opt/ctf-requirements/
COPY container/hexstrike/ctf_adapter/ /opt/ctf-adapter/ctf_adapter/
COPY container/hexstrike/tools.json /opt/ctf-adapter/tools.json
COPY container/hexstrike/profiles.json /opt/ctf-adapter/profiles.json
COPY container/hexstrike/hashpump_cli.py /opt/ctf-adapter/hashpump_cli.py
COPY container/hexstrike/install-source-tools.sh /usr/local/sbin/install-ctf-source-tools

RUN --mount=type=cache,target=/root/.cache/pip \
    chmod 0755 /usr/local/sbin/install-ctf-source-tools /opt/ctf-adapter/hashpump_cli.py \
    && /usr/local/sbin/install-ctf-source-tools python-tools
RUN --mount=type=cache,target=/opt/micromamba/pkgs \
    /usr/local/sbin/install-ctf-source-tools sage
RUN --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    --mount=type=cache,target=/tmp/pwninit-target \
    /usr/local/sbin/install-ctf-source-tools pwn-support
RUN --mount=type=cache,target=/root/.cache/pip \
    /usr/local/sbin/install-ctf-source-tools pwndbg
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/go/pkg/mod \
    /usr/local/sbin/install-ctf-source-tools research-tools
RUN /usr/local/sbin/install-ctf-source-tools native-tools
RUN /usr/local/sbin/install-ctf-source-tools blockchain-evm
RUN --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    --mount=type=cache,target=/tmp/agave-target \
    /usr/local/sbin/install-ctf-source-tools solana-core
RUN --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    --mount=type=cache,target=/tmp/anchor-target \
    /usr/local/sbin/install-ctf-source-tools solana-anchor
RUN --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    --mount=type=cache,target=/tmp/spl-target \
    /usr/local/sbin/install-ctf-source-tools solana-spl
RUN /usr/local/sbin/install-ctf-source-tools verify \
    && python3 -m ctf_adapter.capture_versions \
    && python3 -m compileall -q /opt/ctf-adapter

COPY container/hexstrike/entrypoint.sh /usr/local/bin/hexstrike-entrypoint
RUN chmod 0755 /usr/local/bin/hexstrike-entrypoint \
    && mkdir -p /workspace /workbench/input /workbench/output

WORKDIR /workspace

EXPOSE 8888

HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=12 \
  CMD curl --fail --silent --show-error http://127.0.0.1:8888/health >/dev/null || exit 1

ENTRYPOINT ["/usr/local/bin/hexstrike-entrypoint"]
CMD ["python3", "/opt/hexstrike/hexstrike_server.py", "--port", "8888"]
