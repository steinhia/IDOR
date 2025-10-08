import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import pdb

# --------------------------
# 1. Charger un corpus léger en français
# --------------------------
# Exemple : Tatoeba (phrases françaises)
# Tu peux télécharger depuis https://tatoeba.org/en/downloads
# Ici on suppose que tu as un CSV "sentences.csv" avec colonnes: id, lang, sentence


import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

def calcultate_embeddings():
    # Exemple : Tatoeba français
    df = pd.read_csv("csv/fra_sentences.tsv", sep='\t', header=None, names=['id','lang','sentence'])
    print("csv read")
    df_fr = df[df['lang'] == 'fra'].reset_index(drop=True)
    model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    model = SentenceTransformer(model_name)
    print("model loaded!")
    corpus_sentences = df_fr['sentence'].tolist()
    corpus_embeddings = model.encode(corpus_sentences, convert_to_tensor=True,show_progress_bar=True)
    print("sentences encoded!")
    torch.save(corpus_embeddings, "corpus_embeddings.pt")
    df_fr.to_csv("corpus_fr.csv", index=False)
    print("Embeddings pré-calculés et sauvegardés !")
#calcultate_embeddings()


def select_sentences():
    df_fr = pd.read_csv("corpus_fr.csv")
    corpus_embeddings = torch.load("corpus_embeddings.pt")
    model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    model = SentenceTransformer(model_name)
    target_word = "pomme"
    word_embedding = model.encode([target_word], convert_to_tensor=True)
    subset_df = df_fr[df_fr['sentence'].str.contains(target_word)].reset_index()
    if subset_df.empty:
        print(f"Aucune phrase ne contient '{target_word}'")
    else:
        subset_embeddings = corpus_embeddings[subset_df['index'].values]
    cos_scores = util.cos_sim(word_embedding, subset_embeddings)[0]
    top_k = min(10, len(subset_df))
    top_results = torch.topk(cos_scores, k=top_k)

    print(f"Phrases les plus proches de '{target_word}':\n")
    for score, idx in zip(top_results.values, top_results.indices):
        print(f"{subset_df.iloc[idx]['sentence']}  (score={score:.4f})")
#select_sentences()

def generate_prediction():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    model_name = "mistralai/Mistral-7B-v0.1"  # accessible sans gated repo
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

    prompt = "Elle a acheté un"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=20,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Texte généré :", generated_text)
generate_prediction()

