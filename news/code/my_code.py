import json

from django.core.exceptions import ObjectDoesNotExist


class DeleteSession:
    def __init__(self, request):
        self._req = request
        self._TempImage = None

    def _delete_session(self, session_name):
        if self._req.session.get(session_name):
            del self._req.session[session_name]

    def _delete_temp_images(self, session_name):
        if self._req.session.get(session_name):
            temp_image_id_list = json.loads(self._req.session.get(session_name))

            for temp_id_image_to_delete in temp_image_id_list:
                try:
                    delete_image = self._TempImage.objects.get(pk=temp_id_image_to_delete)
                    delete_image.delete()
                except ObjectDoesNotExist:
                    pass

    def _temp_image_exist(self):
        if self._TempImage is None:
            raise ValueError

    def temp_image(self, temp_image):
        self._TempImage = temp_image

    def delete_data_article(self):
        self._delete_session('data_article')

    def delete_data_article_update(self):
        self._delete_session('data_article_update')

    def delete_temp_img_id_list(self):
        self._temp_image_exist()
        self._delete_temp_images('temp_img_id_list')
        self._delete_session('temp_img_id_list')

    def delete_temp_img_id_list_update(self):
        self._temp_image_exist()
        self._delete_temp_images('temp_img_id_list_update')
        self._delete_session('temp_img_id_list_update')

    def delete_article_id(self):
        self._delete_session('article_id')

    def delete_session_all(self):
        self.delete_data_article()
        self.delete_data_article_update()
        self.delete_temp_img_id_list()
        self.delete_temp_img_id_list_update()
        self.delete_article_id()


def resize_image(image_pilow: object, max_width: int, proporcion: float):
    max_height = int(round(max_width / proporcion, 0))

    if not image_pilow.width / image_pilow.height == proporcion:
        new_height = int(round(image_pilow.width / proporcion, 0))
        image_pilow = image_pilow.resize((image_pilow.width, new_height))

    image_pilow.thumbnail((max_width, max_height))

    return image_pilow
