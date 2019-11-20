#!/bin/bash

srcdir=`dirname $0`
. "${srcdir}/lib.sh"

parse_args "$0" "owner dataset_owner experiment dataset model" "$@"
shift $n

set -e
set -x

id
pwd
ls -al .
aws s3 sync s3://almond-research/${dataset_owner}/dataset/${experiment}/${dataset}/ data/

mkdir -p data-sumbt
python3 code/transform_augmented_data.py --input_dir data --output_dir data-sumbt
cp data/multi-woz/MULTIWOZ2.1/ontology.json data-sumbt/ontology.json
python3 code/main-multislot.py --do_train --do_eval --data_dir data-sumbt --output_dir save "$@"

aws s3 sync save/ s3://almond-research/${owner}/models/${experiment}/${model}/
aws s3 sync tensorboard/ s3://almond-research/${owner}/models/${experiment}/${model}_tensorboard/
