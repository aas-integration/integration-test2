# integration-test2
2nd big integration test of all tools

Our new story is:
- TBD

# Dependencies and Requirements

- Java 8
  - JAVA_HOME environment variable must be set to the location of your JDK install.
- Python 2.7
  - packages: glob2 (required by `map2annotation.py`), subprocess32 (required by `fetch.py`)
  - install with `sudo pip install glob2 subprocess32` or, if you don't have sudo privileges, with `pip install --user glob2 subprocess32`)

# How to run
    
    python fetch.py

This downloads all the jars, compiles stuff, and downloads the corpus. Only needs to be run once unless you need to update tools or the corpus.

    python backend.py

Compiles the corpus projects, generates tests and dtrace files, computes dot files, runs petablox.

    python frontend.py

or

    python frontend.py imgscalr dyn4j

runs the main loop over the corpus, or the subset of corpus programs specified in the args.


Results of all tools running can be found on Travis:
[![Click here to see the Results of the experiments on TravisCI](https://travis-ci.org/aas-integration/integration-test.svg?branch=master)](https://travis-ci.org/aas-integration/integration-test)
