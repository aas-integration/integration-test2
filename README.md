# integration-test2
2nd big integration test of all tools

Our new story is:
- TBD

How to run:

    ./fetch_dependencies.sh

This downloads all the jars, compiles stuff, etc. Only needs to be run once.

    python fetch_corpus.py

This fetches all of the projects in the corpus, specified in corpus.json.

    python backend.py

Compiles the corpus projects, generates tests and dtrace files, computes dot files, runs petablox.

    python frontend.py

or

    python frontend.py imgscalr dyn4j

runs the main loop over the corpus, or the subset of corpus programs specified in the args.


Results of all tools running can be found on Travis:
[![Click here to see the Results of the experiments on TravisCI](https://travis-ci.org/aas-integration/integration-test.svg?branch=master)](https://travis-ci.org/aas-integration/integration-test)
