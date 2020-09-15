from django.db import models
from django.utils import timezone
from markdownx.models import MarkdownxField


class Category(models.Model):
    """問題カテゴリ"""
    name = models.CharField('カテゴリ名', max_length=255)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        """テキストの値を返す"""
        return self.name


class Post(models.Model):
    """問題本文と答え"""
    #question = models.TextField('問題文')
    question = MarkdownxField('問題文', help_text='Markdown形式で書いてください')
    #answer = models.TextField('答え')
    answer = MarkdownxField('答え', help_text='MarkDown形式で書いてください')
    created_at = models.DateTimeField('作成日', default=timezone.now)
    category = models.ForeignKey(Category, verbose_name='カテゴリ', on_delete=models.PROTECT)

    def __str__(self):
        """テキストの値を返す"""
        return self.question
