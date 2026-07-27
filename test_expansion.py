import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from benchmark.benchmark_longmemeval import simulate_llm_query_expansion
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import re

def simulate_llm_query_expansion(query):
    try:
        tokens = word_tokenize(query)
        tagged = pos_tag(tokens)
        
        expanded_words = set(w.lower() for w in re.findall(r'\w+', query) if len(w) > 2)
        
        for word, tag in tagged:
            if tag.startswith('NN') or tag.startswith('VB') or tag.startswith('JJ'):
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        syn_word = lemma.name().replace('_', ' ')
                        if len(syn_word) > 2:
                            expanded_words.add(syn_word.lower())
                            
        return " OR ".join(list(expanded_words)[:15])
    except Exception as e:
        print(f"Error: {e}")
        return query

print(simulate_llm_query_expansion("What degree did I graduate with?"))
