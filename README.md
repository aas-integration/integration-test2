# integration-test2
2nd big integration test of all tools

## Dependencies and Requirements (Docker)

- Docker

## Dependencies and Requirements (manual)

Tested on Ubuntu 14.04.

- Programs to download tool dependencies and build corpus projects
  - `sudo apt-get install ant git gradle maven mercurial python2.7-dev python-pip graphviz libgraphviz-dev curl`
- Java 8 JDK
  - JAVA_HOME environment variable must be set to the location of your JDK install.
- Python 2.7 and some packages
  - install required packages with `sudo pip install -r requirements.txt`
     - if you don't have sudo privileges, install with `pip install --user -r requirements.txt`

## Setup (Docker)

To prepare the environment, run:

    docker build -t pascali_integration .
    docker run -it pascali_integration

After the Docker image finishes building, you will be dropped into a bash shell in a fully prepared environment.

If you're running on a Linux system, you may need to run the above commands with `sudo`.

## Setup (manual)

    python fetch.py

This downloads all the jars, compiles stuff, and downloads the corpus. Only needs to be run once unless you need to update tools or the corpus.

## Running

After you've setup your environment, run the tools using one of the `run_*` scripts. For example

    ./run_restricted.sh

Which processes the projects `react` and `jreactphysics3d` from the corpus. Each of these `run_*.sh` scripts contains an example invokation of `experiments.py` which executes all tools. This includes the following tools:

  - [Bixie](http://sri-csl.github.io/bixie/): a bug finding tool that reports inconsistencies.
  - [Randoop](https://randoop.github.io/randoop/): A tool that automatically generates unit tests.
    See the [Randoop tutorial](https://github.com/randoop/tutorial-examples).
  - [Daikon](https://plse.cs.washington.edu/daikon/): A tool to infer likely invariants from recorded execution data.
    See the [Daikon tutorial](https://github.com/aas-integration/daikon-tutorial).
  - [Clusterer](https://github.com/aas-integration/clusterer): A tool to cluster classes and fields that are likely to be similiar based on their naming scheme.
  - [Partitions](https://github.com/aas-integration/partitions): A tool to cluster projects that are likely to serve a similar purpose.
  - [Checker-Framework-Inference](https://github.com/typetools/checker-framework-inference): A tool to propagate and infer type annotations (provided by clusterer).
  - Simprog: A tool that computes method similarity across projects (uses input from clusterer).

  ## Which outputs to look for:

  Project specific outputs are stored in the `./corpus/[PROJECT]/dljc-out/` folders. Outputs that are relevant across projects are stored in the root folder. Project specific outputs include:

### Per-project outputs:

    - `bixie_report`: a human readable report of inconsistencies.
    - `javac.json`, `jars.json`, `stats.json`: various information about the build process.
    - `dot`: flow-graphs for each public method including a `methods.txt` file that maps dot file name to fully qualified method name, and `sourcelines.txt` that maps method names to source code
   locations.
    - `dot/*/kernel.txt`: pre-computed Weisfeiler-Lehman graph kernels for all computed graphs (this includes global relabeling information).
    - `test-classes*/`: generated unit tests.
    - `test-classes*/RegressionTestDriver.dtrace.gz`: recorded execution data for the generated unit tests.
    - `test-classes*/invariants.gz`: Likely invariants per method.

### Cross-project outputs:

    - `clusters.json`: clustering of all classes in the corpus based on name similarity.
    - `class_field_map.json`: clustering of class-fields based on their type.
    - `word_based_field_clusters.json`: sub-clustering of each cluster in `class_field_map.json` based on name similarity. This is used, for example, to distinguish `Integers` that store `height` or `weight` from integers that store `socialSecurityNamber`.

Further, each of the `run_X.sh` scripts creates a folder `X` which contains json files per project that stores the k most similar methods to each method in that project together with their similarity score.


**Find more details on the tools in the [Wiki](https://github.com/aas-integration/integration-test2/wiki)**
