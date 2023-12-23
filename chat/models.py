import os
from django.db import models
from users.models import User


#################################################################
#                            PROFILE                            #
#################################################################

def profile_media_path(instance, filename):
    user_name = instance.user.username
    upload_path = os.path.join('users', user_name)
    file_path = os.path.join(upload_path, filename)
    media_upload_path = os.path.join('media', upload_path)
    if not os.path.exists(media_upload_path):
        os.makedirs(media_upload_path)
    return file_path

class Profile(models.Model):
    """
    Personal Profile
    """
    about_me = models.TextField(default='There is no Personal Signature here yet. You can add it through settings')
    image = models.ImageField(upload_to=profile_media_path, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=50, default="Unkown")
    
    @property
    def image_url(self):
        if self.image == "":
            return "/media/static_default/{}.png".format(self.user_initial)
        else:
            return self.image.url
        
    @property
    def user_initial(self):
        return self.user.username[0].upper()
    
    def __str__(self):
        return self.user.username
