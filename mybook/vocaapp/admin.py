from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Post, Category


# 管理サイトでmodels.pyで定義したものを操作できるようにする
#admin.site.register(Post)
#admin.site.register(Category)

admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(Category, MarkdownxModelAdmin)
