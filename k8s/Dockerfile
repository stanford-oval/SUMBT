ARG COMMON_IMAGE=
FROM ${COMMON_IMAGE}

MAINTAINER Thingpedia Admins <thingpedia-admins@lists.stanford.edu>

# copy source and install
RUN mkdir -p /home/SUMBT/SUMBT
COPY --chown=SUMBT:SUMBT k8s /home/SUMBT/SUMBT/k8s
COPY --chown=SUMBT:SUMBT code /home/SUMBT/SUMBT/code
COPY --chown=SUMBT:SUMBT *.py *sh README.md requirements.txt /home/SUMBT/SUMBT/
WORKDIR /home/SUMBT/SUMBT
RUN pip3 install --user -r requirements.txt
