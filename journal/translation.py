from modeltranslation.translator import register, TranslationOptions

from .models import Article, Post, About, Editorial, SendingArticle


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(About)
class AboutTranslationOptions(TranslationOptions):
    fields = ('journal_name', 'content', 'author_description')


@register(Editorial)
class EditorialTranslationOptions(TranslationOptions):
    fields = ('position',)


@register(SendingArticle)
class SendingArticleTranslationOptions(TranslationOptions):
    fields = ('content',)





