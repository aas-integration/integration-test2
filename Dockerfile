FROM buildpack-deps:xenial-scm

RUN apt-get update && apt-get install -y \
    ant \
    gradle \
    graphviz \
    libgraphviz-dev \
    maven \
    openjdk-8-jdk \
    python2.7-dev \
    python-pip \
    wamerican \
    vim \
    ruby1.9

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV JAVA_TOOL_OPTIONS -Dfile.encoding=UTF8
ENV INTEGRATION_DIR /integration-test2/

RUN mkdir $INTEGRATION_DIR
WORKDIR $INTEGRATION_DIR

RUN mkdir corpus

ARG corpus=all

COPY fetch_corpus.py corpus.json ./
RUN python fetch_corpus.py $corpus

COPY fetch_dependencies.sh build_daikon.sh ./
RUN bash fetch_dependencies.sh 1

COPY *.py ./
COPY *.sh ./
COPY dyntrace dyntrace
COPY insert_jaif insert_jaif
COPY inv_check inv_check
COPY map2annotation map2annotation
COPY ontology_to_daikon ontology_to_daikon
COPY pa2checker pa2checker
COPY simprog simprog

CMD ["bash"]




