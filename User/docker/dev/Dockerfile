FROM ubuntu:20.04

ENV PYTHONPATH=/workspace/app:${PATH}

RUN echo $PYTHONPATH

RUN apt-get -qq update && apt-get install -y python3-pip

WORKDIR /workspace

COPY . /workspace/

RUN pip3 install -r ./requirements/requirements.dev.txt

WORKDIR /workspace/app

ENTRYPOINT ["python3", "main.py"]
