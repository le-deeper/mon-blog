from django.db import models
from django.core.exceptions import ValidationError
import hashlib

from django.db.models.signals import post_save
from django.dispatch import receiver

from mon_blog.blog_ai import BlogAI


class Post(models.Model):
    id_post = models.AutoField(primary_key=True)  # COUNTER equivalent
    titre = models.CharField(max_length=50)
    image = models.ImageField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    categories_choix = [
        ("foot", "Football"),
        ("jeu", "Jeux-video"),
        ("anime", "Animes"),
        ("autre", "Autres")
    ]
    categorie = models.CharField(choices=categories_choix, max_length=50, default="Autres")
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.image and not self.image_url:
            raise ValidationError("Vous devez soit saisir un lien soit importer une image")

    def __str__(self):
        return self.titre


class MotDePasse(models.Model):
    mdp_hache = models.CharField(max_length=256, verbose_name="Mot de Passe")
    algorithm = hashlib.sha256

    def save(self, *args, **kwargs):
        self.mdp_hache = MotDePasse.algorithm(str(self.mdp_hache).encode()).hexdigest()
        super(MotDePasse, self).save(*args, **kwargs)

    def clean(self):
        if len(MotDePasse.objects.all()) == 1:
            raise ValidationError("Un mot de passe est déjà enregistré, modifiez le directement ou supprimez le.")

    def __str__(self):
        return f"Mot de passe haché: {self.mdp_hache}"


class Avis(models.Model):
    id_avis = models.AutoField(primary_key=True)  # COUNTER equivalent
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    avis = models.TextField()
    note = models.IntegerField()

    def __str__(self):
        return f"{self.nom} {self.prenom} - Note: {self.note}"


# Ajouter tous les nouveaux articles à blogai
@receiver(post_save, sender=Post)
def trigger_ajouter_article(sender, instance, created, **kwargs):
    if created:
        BlogAI.get_instance(Post.objects.all()).ajouter_article(instance)
