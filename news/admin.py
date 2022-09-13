# Time
from datetime import datetime
from datetime import timedelta

#Models
from django.contrib import admin
from news.models import Category
from news.models import Article
from news.models import Comment
from news.models import TempImage


class OldTempImageFilter(admin.SimpleListFilter):
    title = ('Old temp image')
    parameter_name = 'Older_than_24_hours.'

    def lookups(self,  request, model_admin):
        return (('1', ('Older than 24 hours.')),)

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(time_created__lt=(datetime.now()-timedelta(days=1)))


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'autor', 'time_created', 'time_modified')
    list_display_links = ['name']
    list_filter = ['autor_id', 'category_id']

    def delete_queryset(self,  request , queryset):
        for obj in queryset:
            obj.delete()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ['name']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'autor', 'article', 'time_created','time_modified', 'comment')
    list_filter = ['autor_id']


@admin.register(TempImage)
class TempImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'time_created')
    list_filter = (OldTempImageFilter,)

    def delete_queryset(self,  request , queryset):
        for obj in queryset:
            obj.delete()
