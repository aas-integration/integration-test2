#!/bin/bash

# Fail the whole script if any command fails
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd ${DIR} &> /dev/null

# Libraries
mkdir -p libs
pushd libs &> /dev/null

JARS=(
    "http://plse.cs.washington.edu/daikon/download/daikon.jar"
    "https://github.com/randoop/randoop/releases/download/v3.0.8/randoop-all-3.0.8.jar"
    "https://github.com/aas-integration/prog2dfg/releases/download/v0.1/prog2dfg.jar"
    "https://github.com/junit-team/junit/releases/download/r4.12/junit-4.12.jar"
    "http://search.maven.org/remotecontent?filepath=org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar"
    "https://github.com/aas-integration/clusterer/releases/download/v0.5/clusterer.jar"
    "https://github.com/SRI-CSL/bixie/releases/download/0.3/bixie.jar"
)

for jar in "${JARS[@]}"
do
    base=$(basename ${jar})
    echo Fetching ${base}
    curl -L -o ${base} ${jar} &> /dev/null

    # Rename randoop's release-specific-name to just randoop.jar
    if  [[ ${base} == randoop* ]] ;
    then
        echo Renaming ${base} to randoop.jar
        mv ${base} "randoop.jar"
    fi
done

popd &> /dev/null # Exit libs

# Tools
mkdir -p tools
pushd tools &> /dev/null

# Fetch do-like-javac
if [ -d do-like-javac ]; then
    rm -rf do-like-javac
fi
git clone https://github.com/SRI-CSL/do-like-javac.git

if [ ! -d daikon-src ]; then
    curl -L -o daikon-src.tgz http://plse.cs.washington.edu/daikon/download/daikon-5.4.6.tar.gz
    bash ../build_daikon.sh `pwd`/daikon-src.tgz
    cp daikon-src/daikon.jar ../libs/daikon.jar
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
