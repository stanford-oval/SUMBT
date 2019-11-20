import json
import os
import argparse
import git
#repo = git.Repo('.', search_parent_directories=True)
repo = os.path.dirname(os.path.abspath(__file__))
work_repo = '/'.join(repo.split('/')[:-1])
os.chdir(work_repo)

parser = argparse.ArgumentParser()

## Required parameters
parser.add_argument("--data_src", default="data/multiwoz2.1/original")
parser.add_argument("--data_store", default="data/multiwoz2.1")
args = parser.parse_args()
data_dir = os.path.join(work_repo, args.data_src)
data_store = os.path.join(work_repo, args.data_store)

GENERAL_TYPO = {
    # type
    "guesthouse": "guest house", "guesthouses": "guest house", "guest": "guest house",
    "mutiple sports": "multiple sports",
    "sports": "multiple sports", "mutliple sports": "multiple sports", "swimmingpool": "swimming pool",
    "concerthall": "concert hall",
    "concert": "concert hall", "pool": "swimming pool", "night club": "nightclub", "mus": "museum",
    "ol": "architecture",
    "colleges": "college", "coll": "college", "architectural": "architecture", "musuem": "museum", "churches": "church",
    # area
    "center": "centre", "center of town": "centre", "near city center": "centre", "in the north": "north",
    "cen": "centre", "east side": "east",
    "east area": "east", "west part of town": "west", "ce": "centre", "town center": "centre",
    "centre of cambridge": "centre",
    "city center": "centre", "the south": "south", "scentre": "centre", "town centre": "centre", "in town": "centre",
    "north part of town": "north",
    "centre of town": "centre", "cb30aq": "none",
    # price
    "mode": "moderate", "moderate -ly": "moderate", "mo": "moderate",
    # day
    "next friday": "friday", "monda": "monday",
    # parking
    "free parking": "free",
    # internet
    "free internet": "yes",
    # star
    "4 star": "4", "4 stars": "4", "0 star rarting": "none",
    # others
    "y": "yes", "any": "do not care", "n": "no", "does not care": "do not care", "not men": "none", "not": "none",
    "not mentioned": "none",
    '': "none", "not mendtioned": "none", "3 .": "3", "does not": "no", "fun": "none", "art": "none",
}

def get_path(dir, file_name):
    return os.path.join(dir, file_name)

data_file = get_path(data_dir, "data.json")

val_list_file = get_path(data_dir, "valListFile.json")
test_list_file = get_path(data_dir, "testListFile.json")
train_target_file = get_path(data_store, "train.tsv")
dev_target_file = get_path(data_store, "dev.tsv")
test_target_file = get_path(data_store, "test.tsv")

target_files = [train_target_file, dev_target_file, test_target_file]
ontology_file = get_path(data_dir, "ontology.json")

### Read ontology file
fp_ont = open(ontology_file, "r")
data_ont = json.load(fp_ont)
ontology = {}
for domain_slot in data_ont:
    domain, slot = domain_slot.split('-')
    if domain in ["bus", "hospital"]:
        continue
    if domain not in ontology:
        ontology[domain] = {}
    ontology[domain][slot] = {}
    for value in data_ont[domain_slot]:
        ontology[domain][slot][value] = 1
fp_ont.close()

### Read file list (dev and test sets are defined)
dev_file_list = {}
fp_dev_list = open(val_list_file)
for line in fp_dev_list:
    dev_file_list[line.strip()] = 1

test_file_list = {}
fp_test_list = open(test_list_file)
for line in fp_test_list:
    test_file_list[line.strip()] = 1

### Read woz logs and write to tsv files

fp_train = open(train_target_file, "w")
fp_dev = open(dev_target_file, "w")
fp_test = open(test_target_file, "w")

fp_train.write('# Dialogue ID\tTurn Index\tUser Utterance\tSystem Response\t')
fp_dev.write('# Dialogue ID\tTurn Index\tUser Utterance\tSystem Response\t')
fp_test.write('# Dialogue ID\tTurn Index\tUser Utterance\tSystem Response\t')

for domain in sorted(ontology.keys()):
    if domain in ["bus", "hospital"]:
        continue
    for slot in sorted(ontology[domain].keys()):
        fp_train.write(str(domain) + '-' + str(slot) + '\t')
        fp_dev.write(str(domain) + '-' + str(slot) + '\t')
        fp_test.write(str(domain) + '-' + str(slot) + '\t')

fp_train.write('\n')
fp_dev.write('\n')
fp_test.write('\n')

fp_data = open(data_file, "r")

data = json.load(fp_data)

n_skipped = 0
n_turns = 0
for file_id in data:
    if file_id in dev_file_list:
        fp_out = fp_dev
    elif file_id in test_file_list:
        fp_out = fp_test
    else:
        fp_out = fp_train

    user_utterance = ''
    system_response = ''
    turn_idx = 0


    for idx, turn in enumerate(data[file_id]['log']):
        skipped = False
        n_turns += 1

        if idx % 2 == 0:        # user turn
            user_utterance = data[file_id]['log'][idx]['text']
        else:                   # system turn
            user_utterance = user_utterance.replace('\t', ' ')
            user_utterance = user_utterance.replace('\n', ' ')
            user_utterance = user_utterance.replace('  ', ' ')

            system_response = system_response.replace('\t', ' ')
            system_response = system_response.replace('\n', ' ')
            system_response = system_response.replace('  ', ' ')

            fp_out.write(str(file_id))                   # 0: dialogue ID
            fp_out.write('\t' + str(turn_idx))           # 1: turn index
            fp_out.write('\t' + str(user_utterance))     # 2: user utterance
            fp_out.write('\t' + str(system_response))    # 3: system response

            belief = {}
            for domain in data[file_id]['log'][idx]['metadata'].keys():
                if domain in ["bus", "hospital"]:
                    continue
                for slot in data[file_id]['log'][idx]['metadata'][domain]['semi'].keys():

                    value = data[file_id]['log'][idx]['metadata'][domain]['semi'][slot].strip()
                    value = value.lower()
                    if value == '' or value == 'not mentioned' or value == 'not given':
                        value = 'none'

                    if slot == "leaveAt":
                        slot = "leave at"
                    elif slot == "arriveBy":
                        slot = "arrive by"
                    elif slot == "pricerange":
                        slot = "price range"
                    if value == "doesn't care" or value == "don't care" or value == "dont care" or value == "does not care" or value == "dontcare":
                        value = "do not care"

                    if value in GENERAL_TYPO.keys():
                        value = GENERAL_TYPO[value]

                    if domain not in ontology:
                        print("domain (%s) is not defined" % domain)
                        skipped = True
                        continue


                    if slot not in ontology[domain]:
                        print("slot (%s) in domain (%s) is not defined" % (slot, domain))   # bus-arriveBy not defined
                        skipped = True
                        continue


                    if value not in ontology[domain][slot] and value != 'none' and value != "do not care":
                        #print("%s: value (%s) in domain (%s) slot (%s) is not defined in ontology" %
                        #      (file_id, value, domain, slot))
                        value = 'none'
                        skipped = True
                        #print("value set to none")

                    belief[str(domain) + '-' + str(slot)] = value

                for slot in data[file_id]['log'][idx]['metadata'][domain]['book'].keys():
                    if slot == 'booked':
                        continue
                    if domain == 'bus' and slot == 'people':
                        continue    # not defined in ontology

                    value = data[file_id]['log'][idx]['metadata'][domain]['book'][slot].strip()
                    value = value.lower()

                    if value == '' or value == 'not mentioned' or value == 'not given':
                        value = 'none'
                    elif value == "doesn't care" or value == "don't care" or value == "dont care" or value == "does not care" or value == "dontcare":
                        value = "do not care"
                    if str('book ' + slot) not in ontology[domain]:
                        print("book %s is not defined in domain %s" % (slot, domain))
                        continue

                    if value not in ontology[domain]['book ' + slot] and value != 'none' and value != "do not care":
                        print("%s: value (%s) in domain (%s) slot (book %s) is not defined in ontology" %
                              (file_id, value, domain, slot))
                        skipped = True
                        value = 'none'

                    belief[str(domain) + '-book ' + str(slot)] = value

            for domain in sorted(ontology.keys()):
                for slot in sorted(ontology[domain].keys()):
                    key = str(domain) + '-' + str(slot)
                    if key in belief:
                        fp_out.write('\t' + belief[key])
                    else:
                        fp_out.write('\tnone')

            fp_out.write('\n')
            fp_out.flush()

            system_response = data[file_id]['log'][idx]['text']
            turn_idx += 1
    if skipped:
        n_skipped += 1

print("Number skipped", n_skipped)
print("% skipped", n_skipped/n_turns)

fp_train.close()
fp_dev.close()
fp_test.close()
