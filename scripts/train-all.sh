#!/bin/bash
set -e
#set -x

do_train() {
  dataset="$1"
  model="$2"
  shift
  shift
  ./k8s/train.sh --experiment multiwoz --dataset "$dataset" --model "$model" -- \
                --target_slot all --experiment multiwoz2.1 \
                --bert_model bert-base-uncased --task_name bert-gru-sumbt --nbt rnn \
                --num_train_epochs 300 --do_lower_case --task_name bert-gru-sumbt \
                --warmup_proportion 0.1 --learning_rate 1e-4 --train_batch_size 3 --distance_metric euclidean \
                --patience 15 --tf_dir tensorboard --hidden_dim 300 --max_label_length 32 --max_seq_length 64 \
                --max_turn_length 22 "$@"
  sleep 30
}

domains='hotel train restaurant attraction taxi'
percents='0 1 5 10'

do_train baseline21 sumbt-baseline
do_train aug16 sumbt-augmented

augmentations='restaurant2hotel hotel2restaurant restaurant2attraction train2taxi taxi2train'
for aug in $augmentations ; do
  to_domain=$(echo "${aug}" | cut -f2 -d'2')
  for pct in $percents ; do
    do_train ${aug}-pct${pct} sumbt-except-${to_domain}-pct${pct}
  done
done

augmentations='restaurant2hotel hotel2restaurant restaurant2attraction train2taxi taxi2train'
for aug in $augmentations ; do
  to_domain=$(echo "${aug}" | cut -f2 -d'2')
  for pct in $percents ; do
    do_train ${aug}-pct${pct}-tr16 sumbt-except-${to_domain}-pct${pct}-augmented
  done
done