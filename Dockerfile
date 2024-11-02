FROM python:3.10-bookworm
LABEL maintainer="Rosen Vladimirov <vladimirv.rosen@gmail.com>"

ENV PIPX_BIN_DIR=/usr/local/bin
ENV PIPX_DEFAULT_PYTHON=python3
ENV PIPX_GLOBAL_MAN_DIR=/usr/local/share/man
ENV PIPX_GLOBAL_HOME=/opt/odoo/pipx
ENV PYTHONPATH=/opt/python3

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y \
        python3 \
        python3-pip \
        libcups2-dev

RUN mkdir -p /opt/odoo_import_rpc && \
    mkdir -p /etc/odoo

COPY --chown=root:root ./import_model_odoorpc_steps_v_2_12.py /opt/odoo_import_rpc/import_model_odoorpc_steps_v_2_12.py
COPY --chown=root:root ./requirements.txt /opt/odoo_import_rpc/requirements.txt
COPY --chown=root:root ./conf /etc/odoo

RUN pip3 install --upgrade pip && \
    pip3 install -r /opt/odoo_import_rpc/requirements.txt

ENTRYPOINT ["python3"]
CMD ["/opt/odoo_import_rpc/import_model_odoorpc_steps_v_2_12.py", "/etc/odoo/main-dev2-11-17.ini"]