FROM continuumio/miniconda3:latest

ARG DEBIAN_FRONTEND=noninteractivez
ARG username=arturo
ARG condaenv=env


RUN useradd --create-home --shell /bin/bash ${username}
RUN chown -R ${username} /opt/conda/

USER ${username}

RUN conda create -y --name ${condaenv}
RUN echo "source activate ${condaenv}" > ~/.bashrc
ENV TZ=Europe/Oslo



RUN pip3 install --upgrade pip

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
