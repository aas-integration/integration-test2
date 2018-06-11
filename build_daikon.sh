#!/usr/bin/env bash

DAIKON_TARBALL=$1
DAIKON_PARENT_DIR=`dirname $1`

echo JAVA_HOME: ${JAVA_HOME:?"Building Daikon requires the JAVA_HOME environment variable to be set."}

pushd $DAIKON_PARENT_DIR
    DAIKON_SRC_DIR=`tar -tzf ${DAIKON_TARBALL} | head -1 | cut -f1 -d"/"`
    tar xzf $DAIKON_TARBALL
    mv $DAIKON_SRC_DIR daikon-src
    pushd daikon-src
        export DAIKONDIR=`pwd`
        source scripts/daikon.bashrc
        make -C java dcomp_rt.jar
    popd
popd
