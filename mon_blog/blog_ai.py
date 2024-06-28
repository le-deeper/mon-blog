from transformers import AutoTokenizer, AutoModel, pipeline
import faiss
import torch
import numpy as np
import os
from openai import OpenAI


class BlogAI:
    NOM_MODELE = "sentence-transformers/all-MiniLM-L6-v2"
    CLE_API = os.getenv('CHATGPT_CLE_API')
    tokenizer = AutoTokenizer.from_pretrained(NOM_MODELE)
    modele = AutoModel.from_pretrained(NOM_MODELE)
    qr_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
    k = 3

    instance = None

    def __init__(self, articles=None):
        os.environ['KMP_DUPLICATE_LIB_OK'] = "True"
        self.client = OpenAI(
            api_key=BlogAI.CLE_API,
        )
        self.index = faiss.IndexFlatL2(384)
        self.text_articles = ""
        self.articles = []
        if articles:
            for article in articles:
                self.ajouter_article(article)

    @staticmethod
    def get_instance(articles=None):
        if not BlogAI.instance:
            BlogAI.instance = BlogAI(list(articles))
        return BlogAI.instance

    @staticmethod
    def embed_text(text):
        inputs = BlogAI.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            embeddings = BlogAI.modele(**inputs).last_hidden_state[:, 0, :]
        return embeddings.squeeze().numpy()

    def ajouter_article(self, article):
        self.articles.append(article)
        self.text_articles += f"\n\ntitre: {article.titre}\n contenu: {article.contenu}"
        a_embedding = BlogAI.embed_text(article.contenu)
        self.index.add(np.expand_dims(a_embedding, axis=0))


    def rechercher_plus_proche_voisin(self, recherche):
        # On transforme la recherche en vecteur
        query_embedding = BlogAI.embed_text(recherche).reshape(1, -1)
        # Et on recherche les plus proches voisins
        distances, indices = self.index.search(query_embedding, BlogAI.k)
        resultat = [self.articles[int(i)] for i in indices[0]]
        # On génére une réponse à l'aide du modèle de langage
        context = " ".join([article.contenu for article in resultat])
        reponse = BlogAI.qr_pipeline(question=recherche, context=context)

        return resultat, reponse["answer"]

    def chatGPT(self, question):
        prompt = (f"En te basant sur les articles suivants, réponds à la question:"
                  f"\n\n{self.text_articles}\n\nQuestion de l'utilisateur: {question}\nChatbot:")
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-3.5-turbo",
            )
            chatbot_response = chat_completion.choices[0].message.content
        except Exception as e:
            print(e)
            chatbot_response = "Erreur lors de la génération de la réponse"
        return chatbot_response
