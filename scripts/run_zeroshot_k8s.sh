#!/bin/bash
domains='hotel train restaurant attraction taxi'
for dom in $domains
do
./k8s/train.sh --experiment multiwoz --dataset baseline21 --model sumbt-except-$dom-1 -- \
                --do_train --do_eval --data_dir data --output_dir save --target_slot all --experiment multiwoz2.1 \
                --bert_model bert-base-uncased --task_name bert-gru-sumbt --nbt rnn \
                --num_train_epochs 300 --do_lower_case --task_name bert-gru-sumbt \
                --warmup_proportion 0.1 --learning_rate 1e-4 --train_batch_size 3 --distance_metric euclidean \
                --patience 15 --tf_dir tensorboard --hidden_dim 300 --max_label_length 32 --max_seq_length 64 \
                --max_turn_length 22 --except_domain $dom
done
