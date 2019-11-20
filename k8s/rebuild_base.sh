#!/bin/bash

srcdir=`dirname $0`
. "${srcdir}/config"
. "${srcdir}/lib.sh"
check_config "IMAGE COMMON_IMAGE"

set -e
set -x

docker build -t ${COMMON_IMAGE} \
  -f ${srcdir}/Dockerfile.base ${srcdir}/..
docker push ${COMMON_IMAGE}
