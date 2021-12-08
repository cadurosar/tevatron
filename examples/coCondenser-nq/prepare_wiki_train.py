import json
import os
from argparse import ArgumentParser

from transformers import AutoTokenizer, PreTrainedTokenizer
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--tokenizer', type=str, required=False, default='bert-base-uncased')
parser.add_argument('--minimum-negatives', type=int, required=False, default=8)
args = parser.parse_args()

tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)

data = json.load(open(args.input))

if not os.path.exists(args.output):
    os.makedirs(args.output)
with open(os.path.join(args.output, 'train_data.json'), 'w') as f:
    for idx, item in enumerate(tqdm(data)):
        if len(item['hard_negative_ctxs']) < args.minimum_negatives and len(item['positive_ctxs']) < 1:
            continue

        group = {}
        positives = [pos['title'] + tokenizer.pad_token + pos['text'] for pos in item['positive_ctxs']]
        negatives = [neg['title'] + tokenizer.pad_token + neg['text'] for neg in item['hard_negative_ctxs']]

        query = tokenizer.encode(item['question'], add_special_tokens=False, max_length=256, truncation=True)
        positives = tokenizer(
            positives, add_special_tokens=False, max_length=256, truncation=True, padding=False)['input_ids']
        negatives = tokenizer(
            negatives, add_special_tokens=False, max_length=256, truncation=True, padding=False)['input_ids']

        group['query'] = query
        group['positives'] = positives
        group['negatives'] = negatives

        f.write(json.dumps(group) + '\n')