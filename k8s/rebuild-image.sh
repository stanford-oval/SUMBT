#!/bin/bash

srcdir=`dirname $0`
. "${srcdir}/config"
. "${srcdir}/lib.sh"
check_config "IMAGE COMMON_IMAGE"

set -e
set -x

#docker build -t ${COMMON_IMAGE} \
#  -f ${srcdir}/Dockerfile.base ${srcdir}/..
#docker push ${COMMON_IMAGE}


docker pull ${COMMON_IMAGE}

docker build -t ${IMAGE} -f ${srcdir}/Dockerfile --build-arg COMMON_IMAGE=${COMMON_IMAGE} ${srcdir}/..
docker push ${IMAGE}

#docker build -t 373474209952.dkr.ecr.us-west-2.amazonaws.com/SUMBT:latest-agataf -f /home/agataf/SUMBT/k8s/Dockerfile.base
#docker push
