# mon-blog

## Présentation
Il s'agit d'un blog "personnel". On peut accéder à des articles sur différents sujets comme on peut ajouter des articles
(mot de passe: zarzis). Les lecteurs peuvent accéder à un post, rechercher un post en particulier ou publier un avis.

## Fonctionnalités
- Changer de langue: Le lecteur peut choisir une langue parmi les 3 proposées!![img_1.png](img_1.png)
- Toutes les pages sont responsives![img.png](img.png)
- Publier un avis![img_2.png](img_2.png)
- Publier un article (mdp: zarzis)![img_5.png](img_5.png)
- Rechercher un post et avoir une réponse généré à partir des résultats![img_3.png](img_3.png)
- Discuter avec chatGPT à propos des contenus des blogs![img_4.png](img_4.png)

## Utilisation de ChatGPT 
ChatGPT a été utilisé pour résoudre plusieurs problèmes, 
voici la liste des problèmes où j'ai fait appel à chatGPT:
- Afficher un aperçu d'une image dans le panel admin
- Peupler la BD (Générer des avis et des posts sur différents sujets)
- Rappeler les étapes pour traduire les éléments statiques et ignorer certains dossiers (dossier venv)
- Traduire ces éléments (je lui donne le fichier Django.po et je lui demande de compléter avec les traductions)
- Proposer une solution pour que l'utilisateur puisse changer de langue facilement. Il m'a proposé une solution qui ne me convenait pas, à savoir ajouter des préfixes (fr/, en/) ce qui ne fonctionnait pas très bien. En regardant la documentation, (https://docs.djangoproject.com/fr/4.2/topics/i18n/translation/#the-set-language-redirect-view), je constate que je peux modifier la langue en modifiant la valeur d'un cookie dont le nom peut être changé dans les paramètres (LANGUAGE_COOKIE_NAME)
- Implémenter une recherche RAG: Ne connaissant pas assez ce sujet, je lui ai demandé de me proposer un code pour générer une réponse basé sur un ensemble de documenets.

## Instructions sur la façon d'exécuter le projet et de tester la fonctionnalité multilingue.
Vous pouvez lancer (pour tester) avec la commande python manage.py runserver, après avoir installer toutes les dépendances dans requirements.txt.  
Pour changer la langue, il suffit d'aller dans le menu > langue et cliquer sur la langue souhaitée. La page rechargera et la version de la langue sélectionnée sera affichée.

## Démonstration de l'intégration du chatbot et/ou de la fonctionnalité RAG
J'ai crée une classe qui gère tout ce qui est IA. Cette classe met en place un singleton (on suppose que dans le code, on fait appel à la méthode statique get_instance()) pour éviter la création de plusieurs instances ce qui entrainerai une perte de temps car le chargement des modèles prend du temps. Ensuite, on enregistre les articles déjà existant et pour chaque nouveau article on l'ajoute simplement sans devoir réajouter les autres grâce à un trigger:
```python
@receiver(post_save, sender=Post)
def trigger_ajouter_article(sender, instance, created, **kwargs):
    if created:
        BlogAI.get_instance(Post.objects.all()).ajouter_article(instance)
```

Cette classe n'est pas complète car elle ne prend pas en compte les mise à jour d'articles ou la suppression d'articles. Bien évidement, ces problèmes n'ont pas été pris en compte à cause du temps. Ensuite, nous avons une méthode pour permettre de rechercher des articles grâce à la méthode du plus proche voisins et avoir une réponse généré en se basant sur un modèle.
```python
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
```
Enfin, nous avons une méthode qui renvoie la réponse à une question passée en paramètre grâce à chatGPT et un prompt qui lui demande de se baser sur les articles du blog:
```python
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
```

## Points négligés ou à améliorer
Il fallait rendre le projet avant une certaine date, ce qui entraîne la négligence de certains points. On pouvait bien sûr mieux structurer le projet en créant plusieurs applications (IA, client, admin...), améliorer la classe BlogAI (prendre en compte les anciens messages dans le prompt...), personnaliser le site et la partie /admin/, factoriser le code de certaines parties du projet ou encore mieux concevoir la base de données en créant par exemple une autre table Categories (et donc mettre une clé étrangère dans Post) afin de permettre à l'admin de créer d'autre catégorie.  