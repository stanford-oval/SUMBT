import json
import os
import random

def get_path(dir, file_name):
    return os.path.join(dir, file_name)

def save_domains(fp_in):
    a_dict = dict()
    for key, dial in fp_in.items():
        #a_dict[dial["dialogue_idx"]] = dial['domains']
        a_dict[key] = []
        for dom in ['attraction', 'hotel', 'restaurant', 'taxi', 'train']:
            if dial['goal'][dom] != {}:
                a_dict[key].append(dom)
    with open(get_path(data_dir, 'all_domains.json'), 'w') as outfile:
        json.dump(a_dict, outfile)
    return a_dict

def convos_per_dom(fp_in):
    a_dict = {'attraction': [], 'hotel': [], 'restaurant': [], 'taxi': [], 'train': []}
    for key, dial in fp_in.items():
        for dom in ['attraction', 'hotel', 'restaurant', 'taxi', 'train']:
            if dial['goal'][dom] != {}:
                a_dict[dom].append(key)
    with open(get_path(data_dir, 'convos-to-domains.json'), 'w') as outfile:
        json.dump(a_dict, outfile)
    return a_dict

def gen_few_shot(dom, percent, conv_dict, save=False):
    dom_lines = []
    to_select_idx = random.sample(range(len(conv_dict[dom])),k=int(len(conv_dict[dom])*percent))
    to_select = [el for idx, el in enumerate(conv_dict[dom]) if idx in to_select_idx]
    i = 0
    for line in lines[1:]:
        if dom not in dom_dict[line[0]]:
            dom_lines.append(line)
        elif line[0] in to_select:
            dom_lines.append(line)
            i+=1

    #print(dom, percent, "num_lines", len(dom_lines))
    if save:
        with open(get_path(data_dir, 'train-no'+dom+'-'+str(percent*10)+'per.tsv'), 'w') as outfile:
            outfile.write('\t'.join(lines[0]))
            outfile.write('\n')
            for line in dom_lines:
                outfile.write('\t'.join(line))
                outfile.write('\n')

    return dom_lines

def gen_zero_shot(dom, dom_dict, save=False):
    dom_lines = []
    for line in lines[1:]:
        if dom not in dom_dict[line[0]]:
            dom_lines.append(line)
    #print(len(dom_lines))
    if save:
        with open(get_path(data_dir, 'train-no'+dom+'.tsv'), 'w') as outfile:
            outfile.write('\t'.join(lines[0]))
            outfile.write('\n')
            for line in dom_lines:
                outfile.write('\t'.join(line))
                outfile.write('\n')
    return dom_lines

data_dir = "../data/multiwoz2.1"

train_file = get_path(data_dir, "train_dials.json")
test_file = get_path(data_dir, "test_dials.json")
dev_file = get_path(data_dir, "dev_dials.json")

with open(get_path(data_dir, "train.tsv"), 'r') as f:
    lines = [el.strip().split('\t') for el in f.readlines()]

with open('../data/multiwoz2.1/original/data.json', 'r') as f:
    data = json.load(f)

dom_dict = save_domains(data)
conv_dict = convos_per_dom(data)

dom_len = {'attraction':0, 'hotel':0, 'restaurant':0, 'taxi':0, 'train':0}
for dom in ['attraction', 'hotel', 'restaurant', 'taxi', 'train']:
    dom_lines = []
    for line in lines[1:]:
        if dom in dom_dict[line[0]]:
            dom_len[dom] +=1

for dom in ['attraction', 'hotel', 'restaurant', 'taxi', 'train']:
    zero_shot = gen_zero_shot(dom, dom_dict, save=True)
    for percent in [0.01, 0.05, 0.10]:
        few_shot = gen_few_shot(dom, percent, conv_dict, save=True)


