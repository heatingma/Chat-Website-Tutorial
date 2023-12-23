import os
import uuid
import mimetypes
from django.db import models
from users.models import User
from django.contrib.auth import get_user_model
from chat.utils import validate_file_size, convert_size
    

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


#################################################################
#                         CHATROOM                              #
#################################################################

def room_media_path(instance, filename):
    room_name = instance.name
    upload_path = os.path.join('chatrooms', room_name)
    file_path = os.path.join(upload_path, filename)
    media_upload_path = os.path.join('media', upload_path)
    if not os.path.exists(media_upload_path):
        os.makedirs(media_upload_path)
    return file_path
 
class Room(models.Model):
    """
    A flexible and freely accessible space
    """
    name = models.CharField(max_length=128, unique=True)
    show_name = models.CharField(max_length=100, default="Showname")
    owner_name = models.CharField(max_length=128)
    about_room = models.CharField(max_length=128, default="welcome to my chatroom")
    online = models.ManyToManyField(to=get_user_model(), blank=True)
    image = models.ImageField(upload_to=room_media_path, null=True, blank=True)
    
    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    @property
    def initial(self):
        return self.name[0].upper()
    
    @property
    def image_url(self):
        if self.image == "":
            return "/media/static_default/{}.png".format(self.initial)
        else:
            return self.image.url
    
    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'
    

#################################################################
#                             TAG                               #
#################################################################

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


#################################################################
#                             POST                              #
#################################################################

def post_media_path(instance, filename):
    room_name = instance.belong_room.name
    post_name = instance.title
    upload_path = os.path.join('chatrooms', room_name, 'posts', post_name)
    file_path = os.path.join(upload_path, filename)
    media_upload_path = os.path.join('media', upload_path)
    if not os.path.exists(media_upload_path):
        os.makedirs(media_upload_path)
    return file_path

class Post(models.Model):
    """
    A flexible and freely accessible space
    """
    title = models.CharField(max_length=128)
    show_name = models.CharField(max_length=128,default="Post_Showname")
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    author_profile = models.ForeignKey(to=Profile, on_delete=models.CASCADE)
    about_post = models.CharField(max_length=1000, default="The author did not set an introduction to the topic")
    image = models.ImageField(upload_to=post_media_path, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now= True)
    belong_room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def initial(self):
        return self.title[0].upper()
    
    class Meta:
        ordering = ['-created_on']
        
    @property
    def image_url(self):
        if self.title.startswith('chatting_'):
            return self.belong_room.image_url
        if self.image == "" or self.image is None:
            return "/media/static_default/{}.png".format(self.initial)
        else:
            return self.image.url

    @property
    def all_tags(self):
        if self.tags.all() == "" or self.tags.all() is None:
            return None
        else:
            return self.tags.all()
          
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        

#################################################################
#                       CHATROOM MESSAGE                        #
#################################################################

def room_message_media_path(instance, filename):
    room_name = instance.room.name
    post_name = instance.belong_post.title
    upload_path = os.path.join('chatrooms', room_name, 'posts', post_name)
    file_path = os.path.join(upload_path, filename)
    media_upload_path = os.path.join('media', upload_path)
    if not os.path.exists(media_upload_path):
        os.makedirs(media_upload_path)
    return file_path

class RoomMessage(models.Model):
    """
    Message for Room
    """
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    belong_post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=room_message_media_path, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.content} [{self.timestamp}]'
    
    def save(self, *args, **kwargs):
        if self.attachment.name:
            validate_file_size(self.attachment)
        super().save(*args, **kwargs)
        
    @property
    def image_url(self):
        profile = Profile.objects.get(user=self.user)
        return profile.image_url

    @property
    def attachment_url(self):
        if self.attachment.name == "" or self.attachment.name is None:
            return ""
        return self.attachment.url
    
    @property
    def attachment_type(self):
        file_type, _ = mimetypes.guess_type(self.attachment.name)
        if file_type.startswith("image"):
            file_type = "image"
        return file_type
    
    @property
    def attachment_name(self):
        if self.attachment.name == "" or self.attachment.name is None:
            return None
        return os.path.basename(self.attachment.name)
        
    @property
    def attachment_size(self):
        try:
            size = os.path.getsize(self.attachment.path)
            return convert_size(size)
        except:
            return 'Unknown Size'
