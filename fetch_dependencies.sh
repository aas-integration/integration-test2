#!/bin/bash

# Fail the whole script if any command fails
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd ${DIR} &> /dev/null

# Libraries
mkdir -p libs
pushd libs &> /dev/null

JARS=(
    "https://github.com/randoop/randoop/releases/download/v3.1.5/randoop-all-3.1.5.jar"
    "https://github.com/aas-integration/prog2dfg/releases/download/v0.1/prog2dfg.jar"
    "https://github.com/junit-team/junit/releases/download/r4.12/junit-4.12.jar"
    "http://search.maven.org/remotecontent?filepath=org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar"
    "https://github.com/aas-integration/clusterer/releases/download/v0.6/clusterer.jar"
    "https://github.com/SRI-CSL/bixie/releases/download/0.3/bixie.jar"
)

for jar in "${JARS[@]}"
do
    base=$(basename ${jar})
    echo Fetching ${base}

    if curl -fLo ${base} ${jar} &> /dev/null; then
      # Rename randoop's release-specific-name to just randoop.jar
      if  [[ ${base} == randoop* ]] ;
      then
          echo Renaming ${base} to randoop.jar
          mv ${base} "randoop.jar"
      fi
    else
      echo Fetching ${base} failed.
      exit 1;
    fi
done

popd &> /dev/null # Exit libs

# Tools
mkdir -p tools
pushd tools &> /dev/null

# Fetch do-like-javac if not using external
if [[ -z "${DLJCDIR}" ]]; then
    if [ -d do-like-javac ]; then
    rm -rf do-like-javac
    fi
    git clone https://github.com/SRI-CSL/do-like-javac.git
fi

# Fetch Daikon if not using external
if [[ -z "${DAIKONDIR}" ]]; then
    DAIKON_SRC="http://plse.cs.washington.edu/daikon/download/daikon-5.5.4.tar.gz"
    DAIKON_SRC_FILE=$(basename ${DAIKON_SRC})

    if [ ! -e $DAIKON_SRC_FILE ]; then
    rm -rf daikon-src

    if curl -fLo $DAIKON_SRC_FILE $DAIKON_SRC; then
        bash ../build_daikon.sh `pwd`/$DAIKON_SRC_FILE
        cp daikon-src/daikon.jar ../libs/daikon.jar
    else
        echo "Fetching $DAIKON_SRC failed."
        exit 1;
    fi

    else
        echo "Daikon already up to date."
    fi
fi

if [ -d "ontology" ]; then
    rm -rf ontology
fi
git clone https://github.com/pascaliUWat/ontology.git

pushd ontology &> /dev/null
export TRAVIS_BUILD_DIR=`pwd`
./pascali-setup.sh
popd &> /dev/null # Exit ontology

popd &> /dev/null # Exit tools

popd &> /dev/null # Exit integration-test
