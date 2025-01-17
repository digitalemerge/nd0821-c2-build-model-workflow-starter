FROM continuumio/miniconda3:latest

ARG DEBIAN_FRONTEND=noninteractivez
ARG username=arturo
ARG condaenv=nyc_airbnb_dev


RUN useradd --create-home --shell /bin/bash ${username}
RUN chown -R ${username} /opt/conda/

USER ${username}

RUN conda update -n base -c defaults conda
COPY ./environment.yml ./environment.yml
RUN conda env create --file ./environment.yml
RUN echo "source activate ${condaenv}" > ~/.bashrc
ENV TZ=Europe/Oslo




