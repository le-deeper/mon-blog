from django.utils.html import format_html
from django.contrib import admin
from mon_blog.models import Post, Avis, MotDePasse


class PostAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'date_publication', 'image_tag')

    def image_tag(self, obj):
        img = '<img src="{}" width="auto" height="50" />'
        if obj.image:
            return format_html(img.format(obj.image.url))
        elif obj.image_url:
            return format_html(img.format(obj.image_url))
        return 'No Image'
    image_tag.short_description = 'Image'


admin.site.register(Post, PostAdmin)
admin.site.register(Avis)
admin.site.register(MotDePasse)
