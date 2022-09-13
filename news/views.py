# Base
import os
import shutil
import json
import base64
import io

# Django settings
from django.conf import settings

# Django shortcuts
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.shortcuts import Http404

# Auth
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

# Exceptions
from django.core.exceptions import ObjectDoesNotExist

# Django messages
from django.contrib import messages

# Models
from news.models import Article
from news.models import Category
from news.models import Comment
from news.models import TempImage
from django.contrib.auth.models import User

# Forms
from news.form import CommentForm
from news.form import UpdateCommentForm
from news.form import DeleteItemForm
from news.form import ArticleDataTextForm
from news.form import ArticleImageForm
from news.form import LogInForm
from news.form import DataUserForm

# Paginator
from django.core.paginator import Paginator

# Views
from django.views import View

# Pilow
from PIL import Image

# My code
from news.code.my_code import resize_image
from news.code.my_code import DeleteSession


def index(request, page_number=None):
    if request.user.is_authenticated:
        delete_session = DeleteSession(request)
        delete_session.temp_image(TempImage)
        delete_session.delete_session_all()

    article = Article.objects.all().order_by('-pk')

    quantity_page = 10
    pagination = Paginator(article, quantity_page)

    if page_number is None:
        page_obj = pagination.get_page(1)
    else:
        page_number = int(page_number)
        page_obj = pagination.get_page(page_number)

    menu = Category.objects.all().order_by('name')

    return render(request, 'news/index.html',
                  context={'menu': menu, 'page_obj': page_obj})


def article(request, category_name, page_number=None):
    if request.user.is_authenticated:
        delete_session = DeleteSession(request)
        delete_session.temp_image(TempImage)
        delete_session.delete_session_all()

    menu = Category.objects.all().order_by('name')
    article = Article.objects.filter(category_id__name=category_name).order_by('-pk')

    quantity_page = 10
    pagination = Paginator(article, quantity_page)

    if page_number is None:
        page_obj = pagination.get_page(1)
    else:
        page_number = int(page_number)
        page_obj = pagination.get_page(page_number)

    return render(request, 'news/articles.html',
                  context={'menu': menu, 'page_obj': page_obj, 'category_name': category_name})


def article_details(request, article_id, page_number=None):
    if request.user.is_authenticated:
        delete_session = DeleteSession(request)
        delete_session.temp_image(TempImage)
        delete_session.delete_session_all()



    menu = Category.objects.all().order_by('name')
    article = get_object_or_404(Article.objects.select_related('category_id', 'autor_id'), pk=article_id)
    comment_list = Comment.objects.select_related('autor_id').filter(article_id=article_id).order_by('-pk')

    quantity_page = 10
    pagination = Paginator(comment_list, quantity_page)
    if page_number is None:
        page_obj = pagination.get_page(1)
    else:
        page_number = int(page_number)
        page_obj = pagination.get_page(page_number)

    return render(request, 'news/article_details.html',
                  context={'menu': menu, 'article': article, 'page_obj': page_obj})


def article_comment_add(request, article_id):
    menu = Category.objects.all().order_by('name')

    article = get_object_or_404(Article.objects.select_related('category_id', 'autor_id'), pk=article_id)
    if request.user.is_authenticated:
        form = CommentForm({'article_id': article_id})
    else:
        raise Http404()
    form.errors.clear()

    return render(request, 'news/article_comment_add.html',
                  context={'menu': menu, 'article': article, 'form': form})


def comment_edit(request, comment_id):
    if not request.user.is_superuser:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    comment = get_object_or_404(Comment.objects.select_related('article_id'), pk=comment_id)

    update_comment_form = UpdateCommentForm({
        'comment': comment.comment,
        'comment_id': comment.id,
    })

    del_item_form = DeleteItemForm({'item_id': comment.id})

    return render(request, 'news/article_comment_edit.html',
                  context={
                      'menu': menu,
                      'comment': comment,
                      'update_comment_form': update_comment_form,
                      'del_item_form': del_item_form
                  })


def article_add_text_data(request):
    if not request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    if request.session.get('data_article'):
        data_article = json.loads(request.session.get('data_article'))

        form = ArticleDataTextForm({
            'name': data_article.get('name'),
            'article': data_article.get('article'),
            'choice_category': data_article.get('choice_category')
        })

    else:
        form = ArticleDataTextForm()

    return render(request, 'news/article_text_data_add.html',
                  context={'menu': menu, 'form': form})


def article_add_image(request):
    if not request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')

    if request.session.get('data_article'):
        form = ArticleImageForm()

        if request.session.get('temp_img_id_list'):
            temp_img_id_list = json.loads(request.session.get('temp_img_id_list'))
            temp_image = TempImage.objects.get(pk=temp_img_id_list[-1])

            return render(request, 'news/article_image_add.html',
                          context={'menu': menu, 'form': form, 'temp_image': temp_image})

    return render(request, 'news/article_image_add.html',
                  context={'menu': menu, 'form': form})


def article_preview(request):
    if not request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')

    if not request.session.get('data_article'):
        raise Http404()

    if not request.session.get('temp_img_id_list'):
        raise Http404()

    data_session_dict = json.loads(request.session.get('data_article'))
    last_iamge_temp_id = json.loads(request.session.get('temp_img_id_list'))

    img = get_object_or_404(TempImage, pk=last_iamge_temp_id[-1])
    image = Image.open(img.img.path)
    image = resize_image(image, 2000, 5 / 1.5)
    buffered = io.BytesIO()
    image.save(buffered, format='JPEG')
    img_string = base64.b64encode(buffered.getvalue())
    img_string = img_string.decode(encoding='utf-8')

    return render(request, 'news/article_preview.html',
                  context={'menu': menu, 'article': data_session_dict, 'img': img_string})


def article_preview_text_update(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()
    article_id = request.session.get('article_id')
    menu = Category.objects.all().order_by('name')
    if request.session.get('data_article_update'):
        data_session_dict = json.loads(request.session.get('data_article_update'))
        img = get_object_or_404(Article, pk=article_id)
    else:
        raise Http404()

    return render(request, 'news/article_preview_text_update.html',
                  context={
                      'menu': menu,
                      'article': data_session_dict,
                      'article_id': article_id,
                      'img': img
                  })


def article_preview_image_update(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()

    article_id = request.session.get('article_id')
    menu = Category.objects.all().order_by('name')

    if request.session.get('temp_img_id_list_update'):
        last_iamge_temp_id = json.loads(request.session.get('temp_img_id_list_update'))
        img = get_object_or_404(TempImage, pk=last_iamge_temp_id[-1])
        article = get_object_or_404(Article, pk=article_id)
    else:
        raise Http404()

    return render(request, 'news/article_preview_image_update.html',
                  context={'menu': menu, 'article': article, 'img': img})


def article_edit_menu(request, article_id):
    delete_session = DeleteSession(request)
    delete_session.temp_image(TempImage)
    delete_session.delete_data_article_update()
    delete_session.delete_temp_img_id_list_update()

    article = get_object_or_404(Article.objects.select_related('autor_id'), pk=article_id)

    if not request.user.id == article.autor_id.id and not request.user.is_superuser:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    request.session['article_id'] = article.id
    del_item_form = DeleteItemForm({'item_id': article.id})

    return render(request, 'news/article_edit_menu.html',
                  context={'menu': menu, 'article': article, 'del_item_form': del_item_form})


def article_edit_text(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()

    menu = Category.objects.all().order_by('name')
    article_id = request.session.get('article_id')
    article = get_object_or_404(Article.objects.select_related('category_id'), pk=article_id)

    if request.session.get('data_article_update'):
        data_article_update = json.loads(request.session.get('data_article_update'))

        if article.id == article_id:
            form = ArticleDataTextForm({
                'name': data_article_update.get('name'),
                'article': data_article_update.get('article'),
                'choice_category': data_article_update.get('choice_category')
            })

            return render(request, 'news/article_edit_text_data.html',
                          context={'menu': menu, 'form': form, 'article': article})

    form = ArticleDataTextForm({
        'name': article.name,
        'article': article.article,
        'choice_category': article.category_id.id
    })

    return render(request, 'news/article_edit_text_data.html',
                  context={'menu': menu, 'form': form, 'article': article})


def article_change_image(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()

    menu = Category.objects.all().order_by('name')
    article_id = request.session.get('article_id')
    form = ArticleImageForm()

    if request.session.get('temp_img_id_list_update'):
        iamge_temp_id_list = json.loads(request.session.get('temp_img_id_list_update'))
        temp_image = get_object_or_404(TempImage, pk=iamge_temp_id_list[-1])

        return render(request, 'news/article_image_update.html',
                      context={
                          'menu': menu,
                          'form': form,
                          'temp_image': temp_image,
                          'article_id': article_id
                      })

    article = get_object_or_404(Article, pk=article_id)
    image = article.img

    return render(request, 'news/article_image_update.html',
                  context={
                      'menu': menu,
                      'form': form,
                      'image': image,
                      'article_id': article_id
                  })


def log_in(request):
    if request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    form = LogInForm()

    return render(request, 'news/log_in.html', context={'menu': menu, 'form': form})


def register(request):
    if request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    form = UserCreationForm()

    return render(request, 'news/register.html', context={'menu': menu, 'form': form})


def user_profile_menu(request):
    if not request.user.is_authenticated:
        raise Http404()

    delete_session = DeleteSession(request)
    delete_session.temp_image(TempImage)
    delete_session.delete_session_all()

    menu = Category.objects.all().order_by('name')

    return render(request, 'news/user_profile_menu.html', context={'menu': menu})


def user_profil_data(request):
    if not request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')

    first_name = request.user.first_name
    last_name = request.user.last_name
    email = request.user.email
    form = DataUserForm({
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    })

    return render(request, 'news/user_profile_data.html', context={'menu': menu, 'form': form})


def user_change_password(request):
    if not request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    form = PasswordChangeForm(User)

    return render(request, 'news/user_change_password.html', context={'menu': menu, 'form': form})


def user_my_article(request, page_number=None):
    if not request.user.is_authenticated:
        raise Http404()

    menu = Category.objects.all().order_by('name')
    user_id = request.user.id

    quantity_page = 10
    list_articles = Article.objects.select_related('autor_id').filter(autor_id__id=user_id).order_by('-pk')
    pagination = Paginator(list_articles, quantity_page)
    if page_number is None:
        page_obj = pagination.get_page(1)
    else:
        page_number = int(page_number)
        page_obj = pagination.get_page(page_number)

    return render(request, 'news/user_my_article.html', context={'menu': menu, 'page_obj': page_obj})


# Create - Update - Delete ---------------------------------------------------CUD----------------------------------------------------------Create - Update - Delete


class CudArticleAddToSession(View):
    update = False

    def post(self, request):

        if not request.user.is_authenticated:
            raise Http404()

        if request.method == 'POST':
            form = ArticleDataTextForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                data_session_dict = {
                    'name': data.get('name'),
                    'article': data.get('article'),
                    'choice_category': data.get('choice_category').id
                }
                data_session_json = json.dumps(data_session_dict)

                if self.update:
                    request.session['data_article_update'] = data_session_json
                    return redirect('news:article_preview_text_update')
                request.session['data_article'] = data_session_json
                return redirect('news:article_add_image')
            raise Http404()


class CudArticleAddImageToTemp(View):
    update = False
    session_temp_image_list = 'temp_img_id_list'

    def session_update(self):
        if self.update:
            self.session_temp_image_list = 'temp_img_id_list_update'

    def session_article_id_is_exists(self, request):
        if self.update:
            if not request.session.get('article_id'):
                raise Http404()

    def post(self, request):
        if not request.user.is_authenticated:
            raise Http404()

        self.session_article_id_is_exists(request)
        form = ArticleImageForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            self.session_update()
            if not request.session.get(self.session_temp_image_list):
                request.session[self.session_temp_image_list] = json.dumps([])

            temp_image = TempImage(
                img=data.get('img')
            )
            temp_image.save()
            temp_img_id_list = json.loads(request.session[self.session_temp_image_list])
            temp_img_id_list.append(temp_image.pk)
            request.session[self.session_temp_image_list] = json.dumps(temp_img_id_list)

            if self.update:
                return redirect('news:article_change_image')
            return redirect('news:article_add_image')
        raise Http404()


def cud_comment_add(request):
    if not request.user.is_authenticated:
        raise Http404()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            article = Article.objects.get(pk=data.get('article_id'))
            if request.user.is_authenticated:
                Comment.objects.create(
                    comment=data.get('comment'),
                    article_id=article,
                    autor_id=get_object_or_404(User, pk=request.user.id)
                )
            messages.success(request, 'Twój komentarz został dodany')

            return redirect('news:article_details', article.pk)
        else:
            raise Http404()


def cud_comment_edit(request):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'POST':
        form = UpdateCommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            comment = get_object_or_404(Comment.objects.select_related('article_id'), pk=data.get('comment_id'))
            comment.comment = data.get('comment')
            comment.save()
            messages.success(request, 'Komentarz został Zmodyfiowany')

            return redirect('news:article_details', comment.article_id.id)
        else:
            raise Http404()


def cud_comment_del(request):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'POST':
        form = DeleteItemForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            comment_to_del = get_object_or_404(Comment.objects.select_related('article_id'), pk=data.get('item_id'))
            article_id_to_redirect = comment_to_del.article_id.id
            comment_to_del.delete()
            messages.success(request, 'Komentarz został usunęty')

            return redirect('news:article_details', article_id_to_redirect)
        else:
            raise Http404()


def cud_article_save(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('data_article'):
        raise Http404()

    if not request.session.get('temp_img_id_list'):
        raise Http404()

    article_data_dict = json.loads(request.session.get('data_article'))
    temp_img_id_list = json.loads(request.session.get('temp_img_id_list'))

    try:
        temp_image = TempImage.objects.get(pk=temp_img_id_list[-1])
    except ObjectDoesNotExist:
        messages.warning(request, 'Proszę wybierz ponownie swój obrazek')
        return redirect('news:article_add_image')

    choice_category = get_object_or_404(Category, pk=article_data_dict['choice_category'])
    autor = get_object_or_404(User, pk=request.user.id)

    new_relative_path_article_images = f'{Article.img.field.upload_to}{str(temp_image.img).split("/")[1]}'
    new_absolute_path_article_image = f'{settings.MEDIA_ROOT}/{Article.img.field.upload_to}'

    if os.path.exists(temp_image.img.path):

        if not os.path.exists(new_absolute_path_article_image):
            os.mkdir(new_absolute_path_article_image)

        shutil.copy(temp_image.img.path, new_absolute_path_article_image)

        new_article = Article(
            name=article_data_dict['name'],
            article=article_data_dict['article'],
            category_id=choice_category,
            img=new_relative_path_article_images,
            autor_id=autor
        )
        new_article.save()

        messages.success(request, 'Dodano nowy artykuł')
    else:
        messages.error(request, 'Coś poszło nie tak')

    delete_session = DeleteSession(request)
    delete_session.temp_image(TempImage)
    delete_session.delete_data_article()
    delete_session.delete_temp_img_id_list()

    return redirect('news:index')


def cud_article_update_text_save(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()

    if not request.session.get('data_article_update'):
        raise Http404()

    article_id = request.session.get('article_id')
    article_data_dict = json.loads(request.session.get('data_article_update'))
    choice_category = get_object_or_404(Category, pk=article_data_dict.get('choice_category'))

    article = get_object_or_404(Article, pk=article_id)
    article.name = article_data_dict.get('name')
    article.article = article_data_dict.get('article')
    article.category_id = choice_category
    article.save()

    delete_session = DeleteSession(request)
    delete_session.delete_article_id()
    delete_session.delete_data_article_update()

    messages.success(request, 'Zmodyfikowano artykuł')

    return redirect('news:article_details', article.id)


def cud_article_update_image_save(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()

    if not request.session.get('temp_img_id_list_update'):
        raise Http404()

    article_id = request.session.get('article_id')
    article = get_object_or_404(Article, pk=article_id)
    temp_img_id_list_update = json.loads(request.session.get('temp_img_id_list_update'))

    try:
        temp_image = TempImage.objects.get(pk=temp_img_id_list_update[-1])
    except ObjectDoesNotExist:
        messages.warning(request, 'Proszę wybierz ponownie swój obrazek')
        return redirect('news:article_change_image')

    new_relative_path_article_images = f'{Article.img.field.upload_to}{str(temp_image.img).split("/")[1]}'
    new_absolute_path_article_image = f'{settings.MEDIA_ROOT}/{Article.img.field.upload_to}'

    if os.path.exists(temp_image.img.path):
        article.delete_file_image()
        shutil.copy(temp_image.img.path, new_absolute_path_article_image)

        article.img = new_relative_path_article_images
        article.save()
        messages.success(request, 'Zmieniono obrazek')
    else:
        messages.error(request, 'Coś poszło nie tak')

    delete_session = DeleteSession(request)
    delete_session.temp_image(TempImage)
    delete_session.delete_temp_img_id_list_update()

    return redirect('news:article_details', article.id)


def cud_article_delete(request):
    if not request.user.is_authenticated:
        raise Http404()

    if not request.session.get('article_id'):
        raise Http404()

    if request.method == 'POST':

        form = DeleteItemForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            article_to_delete = get_object_or_404(Article, pk=data.get('item_id'))
            article_to_delete.delete()
            messages.success(request, 'Artykuł został usunięty')
            return redirect('news:index')
        raise Http404()


def cud_data_user_update(request):
    if not request.user.is_authenticated:
        raise Http404()

    if request.method == 'POST':
        form = DataUserForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user_id = request.user.id
            user = get_object_or_404(User, pk=user_id)
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.email = data.get('email')
            user.save()
            messages.success(request, 'Uaktualniono profil')

        form_error = dict(form.errors.as_data())

        if form_error.get('first_name'):
            messages.error(request, list(form_error.get('first_name')[0])[0])

        if form_error.get('last_name'):
            messages.error(request, list(form_error.get('last_name')[0])[0])

        if form_error.get('email'):
            messages.error(request, list(form_error.get('email')[0])[0])

        return redirect('news:user_profile_data')


# Auth---------------------------------------------------------------------------------------------------------------------------------------------------------------


def auth_log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            if not User.objects.filter(username=data.get('user')):
                messages.error(request, 'Nie ma takiego użytkownika')
                return redirect('news:log_in')

            user = authenticate(
                username=data.get('user'),
                password=data.get('password')
            )

            if user:
                login(request, user=user)
                return redirect('news:index')
            messages.error(request, 'Nieprawidłowe hasło')
            return redirect('news:log_in')


def auth_log_out(request):
    if request.method == 'POST':
        delete_session = DeleteSession(request)
        delete_session.temp_image(TempImage)
        delete_session.delete_session_all()
        logout(request)

        return redirect('news:index')


def auth_register(request):
    form = UserCreationForm(request.POST)

    if form.is_valid():
        form.save()
        return redirect('news:log_in')

    form_error = json.loads(form.errors.as_json())

    for error in list(form_error.values())[0]:
        messages.error(request, error.get('message'))

    return redirect('news:register')


def auth_change_password(request):
    if not request.user.is_authenticated:
        raise Http404()

    form = PasswordChangeForm(user=request.user, data=request.POST)

    if form.is_valid():
        form.save()
        messages.success(request, 'Zmieniono chasło')
        return redirect('news:log_in')

    form_error = json.loads(form.errors.as_json())

    for error in list(form_error.values())[0]:
        messages.error(request, error.get('message'))

    return redirect('news:user_change_password')
