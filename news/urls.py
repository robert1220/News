from django.urls import path
from news import views

app_name = 'news'

urlpatterns = [
    path('', views.index, name='index'),
    path('page/<int:page_number>/', views.index, name='index_pagination'),
    path('category/<slug:category_name>/', views.article, name='articles'),
    path('category/<slug:category_name>/peage/<int:page_number>/', views.article, name='articles_pagination'),
    path('article/<int:article_id>/', views.article_details, name='article_details'),
    path('article/<int:article_id>/peage/<int:page_number>/', views.article_details, name='article_details_pagination'),
    path('article/<int:article_id>/comment-add/', views.article_comment_add, name='article_comment_add'),
    path('comennt-edit/<int:comment_id>/', views.comment_edit, name='comment_edit'),
    path('article-add/', views.article_add_text_data, name='article_add_text_data'),
    path('article-add/image/', views.article_add_image, name='article_add_image'),
    path('article-preview/', views.article_preview, name='article_preview'),
    path('article-update/preview/', views.article_preview_text_update, name='article_preview_text_update'),
    path('article-update/preview/image', views.article_preview_image_update, name='article_preview_image_update'),
    path('article-edit/<int:article_id>/', views.article_edit_menu, name='article_edit_menu'),
    path('article-edit/text/', views.article_edit_text, name='article_edit_text_data'),
    path('article-edit/image/', views.article_change_image, name='article_change_image'),
    path('log-in/', views.log_in, name='log_in'),
    path('register/', views.register, name='register'),
    path('profil/', views.user_profile_menu, name='user_profile_menu'),
    path('profil/data/', views.user_profil_data, name='user_profile_data'),
    path('profil/change-password/', views.user_change_password, name='user_change_password'),
    path('article-list/', views.user_my_article, name='user_my_article'),
    path('article-list/<int:page_number>/', views.user_my_article, name='user_my_article_pagination'),

    #Create---Update---Delete----------------------------------------CUD-------------------------------------------------------------- CUD

    path('cud/comment/add/', views.cud_comment_add, name='cud_comment_add'),
    path('cud/comment/edit/', views.cud_comment_edit, name='cud_comment_edit'),
    path('cud/comment/del/', views.cud_comment_del, name='cud_comment_del'),
    path('cud/article/add/', views.CudArticleAddToSession.as_view(), name='cud_article_add'),
    path('cud/article/add/image/', views.CudArticleAddImageToTemp.as_view(), name='cud_article_add_image'),
    path('cud/article/add/save/', views.cud_article_save, name='cud_article_add_save'),
    path('cud/article/update/text/', views.CudArticleAddToSession.as_view(update=True), name='cud_article_text_update'),
    path('cud/article/update/text/save/', views.cud_article_update_text_save, name='cud_article_update_text_save'),
    path('cud/article/update/image/save/', views.cud_article_update_image_save, name='cud_article_update_image_save'),
    path('cud/article/update/image/', views.CudArticleAddImageToTemp.as_view(update=True), name='cud_article_update_image'),
    path('cud/article/delete/', views.cud_article_delete, name='cud_article_delete'),
    path('cud/profile/update/', views.cud_data_user_update, name='cud_data_user_update'),

    #LOGIN----------------------------------------------------------------
    path('auth/login/', views.auth_log_in, name='auth_log_in'),
    path('auth/logout/', views.auth_log_out, name='auth_log_out'),
    path('auth/register/', views.auth_register, name='auth_register'),
    path('auth/change-password/', views.auth_change_password, name='auth_change_password'),

]