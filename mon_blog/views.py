from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import activate


from mon_blog import settings
from mon_blog.blog_ai import BlogAI
from mon_blog.models import Post, Avis, MotDePasse

blog_ai = BlogAI.get_instance(Post.objects.all())


def get_post(post_id):
    try:
        return Post.objects.all().filter(pk=post_id).get()
    except ObjectDoesNotExist:
        return None


def check_pwd(pwd):
    try:
        expected_pwd = MotDePasse.objects.all().get().mdp_hache
        if pwd != expected_pwd:
            return False
        return True
    except ObjectDoesNotExist:
        return None


def go_to_index(request):
    foot_posts = Post.objects.all().filter(categorie="foot")[:5]
    game_posts = Post.objects.all().filter(categorie="jeu")[:5]
    anime_posts = Post.objects.all().filter(categorie="anime")[:5]
    return render(request, "index.html",
                  context={
                      "football_posts": foot_posts,
                      "jeu_posts": game_posts,
                      "anime_posts": anime_posts
                  })


def go_to_avis(request):
    avis = Avis.objects.all()
    return render(request, "avis.html",
                  context={
                      "avis": avis,
                  })


def go_to_loisirs(request):
    return render(request, "loisirs.html")


def go_to_contact(request):
    return render(request, "contact.html")


def go_to_foot_posts(request):
    foot_posts = Post.objects.all().filter(categorie="foot")
    return render(request, "posts.html",
                  context={
                      "categorie": "Football",
                      "posts": foot_posts
                  })


def go_to_game_posts(request):
    game_posts = Post.objects.all().filter(categorie="jeu")
    return render(request, "posts.html",
                  context={
                      "categorie": "Jeux-Vidéos",
                      "posts": game_posts
                  })


def go_to_anime_posts(request):
    anime_posts = Post.objects.all().filter(categorie="anime")
    return render(request, "posts.html",
                  context={
                      "categorie": "Animés",
                      "posts": anime_posts
                  })


def go_to_other_posts(request):
    other_posts = Post.objects.all().filter(categorie="autre")
    return render(request, "posts.html",
                  context={
                      "categorie": "Autres",
                      "posts": other_posts
                  })


def go_to_post(request, post_id):
    post = get_post(post_id)
    if post:
        return render(request, "post.html", context={"post": post})
    messages.error(request, "Post inexistant")
    return redirect("/")


def create_avis(request):
    if request.method == "POST":
        data = request.POST
        try:
            nom = data["nom"]
            prenom = data["prenom"]
            avis = data["avis"]
            note = int(data["note"])
        except ValueError:
            messages.error(request, "Erreur lors de l'enregistrement de l'avis")
            return redirect("/")
        avis = Avis(nom=nom, prenom=prenom, avis=avis, note=note)
        avis.save()
        messages.success(request, "Avis enregistré")
        return redirect("/")


def publish(request):
    if request.method == "GET":
        return render(request, "publier.html", context={"categories": Post.categories_choix})
    elif request.method == "POST":
        data = request.POST
        files = request.FILES
        mdp = data["mdp"]
        mdp = MotDePasse.algorithm(str(mdp).encode()).hexdigest()
        titre = data["titre"]
        contenu = data["contenu"]
        contenu = "</br>".join(contenu.split("\n"))
        categorie = data["categorie"]
        context = {
            "categories": Post.categories_choix,
            "titre": titre,
            "categorie": categorie,
            "contenu": contenu
        }
        if check_pwd(mdp):
            image = files.get("image", None)
            if image:
                post = Post(titre=titre, contenu=contenu, categorie=categorie, image=image)
            else:
                image_url = data["image_url"]
                if not image_url:
                    messages.error(request, "Aucune image fournie")
                    return render(request, "publier.html", context=context)
                post = Post(titre=titre, contenu=contenu, categorie=categorie, image_url=image_url)
            post.save()
            messages.success(request, "Post enregistré")
            return redirect(f"/post-{post.pk}/")
        messages.error(request, "Mot de passe incorrect")
        return render(request, "publier.html", context=context)


def change_language(request, lang_code):
    next_url = request.GET.get('next', '/')
    response = redirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    activate(lang_code)
    return response


def search(request):
    query = request.GET.get('q', '')
    if query:
        resultat = blog_ai.rechercher_plus_proche_voisin(query)
        return render(request, 'rechercher.html', {
            'posts': resultat[0],
            'recherche': query,
            'reponse': resultat[1]
        })
    return render(request, 'rechercher.html', {
        'recherche': query,
    })


def discuter(request):
    query = request.GET.get('q', '')
    if query:
        return render(request, 'discuter.html', {
            'question': query,
            'reponse': blog_ai.chatGPT(query)
        })
    return render(request, 'discuter.html', )
