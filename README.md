# integration-test2
2nd big integration test of all tools

## Dependencies and Requirements

- Java 8
  - JAVA_HOME environment variable must be set to the location of your JDK install.
- Python 2.7
  - install required packages with `sudo pip install glob2 networkx pydotplus subprocess32`
     - if you don't have sudo privileges, install with `pip install --user glob2 subprocess32`

## How to run
    
    python fetch.py

This downloads all the jars, compiles stuff, and downloads the corpus. Only needs to be run once unless you need to update tools or the corpus. After all dependencies and the corpus are ready, run the tools using one of the `run_*` scripts. For example

    ./run_restricted.sh
    
Which processes the projects `react` and `jreactphysics3d` from the corpus. Each of these `run_*.sh` scripts contains an example invokation of `experiments.py` which executes all tools. This includes the following tools:

  - Bixie: a bug finding tool that reports inconsistencies.
  - [Randoop](https://randoop.github.io/randoop/): A tool that automatically generates unit tests.
    See the [Randoop tutorial](https://github.com/randoop/tutorial-examples).
  - [Daikon](https://plse.cs.washington.edu/daikon/): A tool to infer likely invariants from recorded execution data.
    See the [Daikon tutorial](https://github.com/aas-integration/daikon-tutorial).
  - Clusterer: A tool to cluster classes and fields that are likely to be similiar based on their naming scheme.
  - Partitions: A tool to cluster projects that are likely to serve a similar purpose.
  - [Checker-Framework-Inference](https://github.com/typetools/checker-framework-inference): A tool to propagate and infer type annotations (provided by clusterer).
  - Simprog: A tool that computes method similarity across projects (uses input from clusterer).
  
  
  *TODO* will paste the description of the individual tools.
