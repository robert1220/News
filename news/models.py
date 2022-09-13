# os
import os

# Django
from django.db import models
from django.conf import settings
from django.contrib import admin

# Pilow
from PIL import Image

# My code
from news.code.my_code import resize_image


class Category(models.Model):
    name = models.CharField(max_length=150, null=False)

    def __str__(self):
        return f"{self.name}"


class Article(models.Model):
    name = models.CharField(max_length=120, null=False)
    article = models.TextField(max_length=25000, null=False)
    img = models.ImageField(upload_to='images/')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    autor_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def delete_file_image(self):
        if os.path.exists(self.img.path):
            os.remove(self.img.path)

    def save(self):
        super().save()
        if self.img:
            image = Image.open(self.img.path)
            im = resize_image(image, 2000, 5 / 1.5)
            im.save(self.img.path)

    def delete(self):
        super().delete()
        self.delete_file_image()

    @admin.display
    def autor(self):
        return self.autor_id

    @admin.display
    def category(self):
        return self.category_id

    def __str__(self):
        return f"{self.name}"


class Comment(models.Model):
    comment = models.TextField(max_length=5000, null=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)
    autor_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display
    def autor(self):
        return self.autor_id

    @admin.display
    def article(self):
        return self.article_id

    def __str__(self):
        return f"{self.comment}"


class TempImage(models.Model):
    img = models.ImageField(upload_to='temp-images/')
    time_created = models.DateTimeField(auto_now_add=True)

    def rename_image_name(self):
        path = settings.MEDIA_ROOT
        name_img = str(self.img)
        dot_position = name_img.rfind('.')
        name_img = f'{name_img[0:dot_position]}-{self.pk}{name_img[dot_position:]}'
        list_name_img = name_img.split('/')
        os.rename(self.img.path, f'{path}\\{list_name_img[0]}\\{list_name_img[1]}')
        self.img = f'{list_name_img[0]}/{list_name_img[1]}'

    def save(self):
        super().save()
        self.rename_image_name()
        super().save()

    def delete(self):
        super().delete()
        if os.path.exists(self.img.path):
            os.remove(self.img.path)
