#!/bin/bash
MAP2ANNO_DIR=$(cd $(dirname "$0") && pwd)

##### build hacked checkstyle
if [ ! -d $MAP2ANNO_DIR/checkstyle ] ; then
    # rm -rf $MAP2ANNO_DIR/checkstyle
    (cd $MAP2ANNO_DIR && git clone --depth 1 --branch multiDeclJson https://github.com/CharlesZ-Chen/checkstyle.git)
    (cd $MAP2ANNO_DIR/checkstyle && mvn clean package -Passembly)
fi
(cd $MAP2ANNO_DIR/checkstyle && git pull)

##### fetch refactor front-end
if [ ! -d $MAP2ANNO_DIR/multiDeclRefactor ] ; then
    # rm -rf $MAP2ANNO_DIR/multiDeclRefactor
    (cd $MAP2ANNO_DIR && git clone --depth 1 https://github.com/CharlesZ-Chen/multiDeclRefactor.git)
fi
(cd $MAP2ANNO_DIR/multiDeclRefactor && git pull)
