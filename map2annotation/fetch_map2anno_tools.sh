#!/bin/bash
MAP2ANNO_DIR=$(cd $(dirname "$0") && pwd)

##### fetch refactor front-end
if [ ! -d $MAP2ANNO_DIR/multiDeclRefactor ] ; then
    # rm -rf $MAP2ANNO_DIR/multiDeclRefactor
    (cd $MAP2ANNO_DIR && git clone --depth 1 https://github.com/CharlesZ-Chen/multiDeclRefactor.git)
fi
(cd $MAP2ANNO_DIR/multiDeclRefactor && git pull)
(cd $MAP2ANNO_DIR/multiDeclRefactor && ./fetch_dependency.sh)
