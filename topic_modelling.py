from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
import pandas as pd
from datasets import load_dataset

print('Downloading dataset...')
dataset = load_dataset('Swithord/hong-kong-legco-transcripts', split='train')
df = pd.DataFrame(dataset)
df['text'] = df['text'].astype(str)
df['year'] = pd.to_datetime(df['date']).dt.year
df['year'] = df['year'].astype(int)
mask = df['text'].str.len() > 100
mask &= df['year'] >= 1995
df = df[mask]
print(f'Filtered dataset contains {len(df)} entries.')

candidate_topics = ['freedom', 'healthcare', 'education', 'economy', 'environment', 'culture', 'industry', 'security', 'justice', 'housing', 'abuse']
topic_model = BERTopic(
    representation_model=KeyBERTInspired(),
    zeroshot_topic_list=candidate_topics,
    zeroshot_min_similarity=.75,
    language='english',
    n_gram_range=(1, 2),
    min_topic_size=250,
)

print('Fitting BERTopic model...')
topics, probs = topic_model.fit_transform(df['text'])
topic_model.save('topic_model', serialization='safetensors')
