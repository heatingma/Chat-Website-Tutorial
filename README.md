# <center>聊天程序实验报告</center>

#### ps: 本实验报告以教程的形式呈现，所有实现细节都会进行详细说明

## 一、实验环境

#### Platform: Windows 11
#### Language: Python
#### Framework: Django


## 二、基础学习

#### 2.1 django

* django学习网址：https://developer.mozilla.org/zh-CN/docs/Learn/Server-side/Django

#### 2.2 Redis

* redis学习网址：https://www.zhihu.com/tardis/bd/art/487583440?source_id=1001

#### 2.3 websocket

* websocket学习网址：https://blog.csdn.net/weixin_45172107/article/details/126590769

## 三 安装实验环境

### 3.1 打开管理员界面依次输入

```bash
conda create --name chat_env python=3.8
conda activate chat_env
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install django==4.2.5
pip install channels==3.0.5
pip install channels-redis==4.1.0
pip install pillow==10.0.1
pip install pypinyin
```

### 3.2 管理员界面构建django项目

``` bash
django-admin startproject Chat_Website_Tutorial
```

### 3.3 创建聊天和用户两个模块

``` bash
cd Chat_Website_Tutorial
python manage.py startapp users
python manage.py startapp chat
```

### 3.4 在Chat_Website_Tutorial下的settings.py中注册模块
![](https://notes.sjtu.edu.cn/uploads/upload_f3aefa1933397134fd38a9a7e585fbbe.png)


### 3.5 下载Redis(windows)

* 下载链接：https://github.com/tporadowski/redis/releases
* 选择最新版本（Redis for Windows 5.0.14.1）
* 解压到Chat_Website_Tutorial文件夹，重命名为redis

### 3.6 创建三个文件夹

* 在Chat_Website_Tutorial文件夹下创建templates、media、static文件夹
* 在settings.py中将以下代码进行修改

```python
ALLOWED_HOSTS = []

TIME_ZONE = "UTC"

STATIC_URL = "static/"
```
修改为：

```python
ALLOWED_HOSTS = ['*']

TIME_ZONE = "Asia/Shanghai"

import os
STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static/css'),
    os.path.join(BASE_DIR, 'static/js'),
]
```

* 在TEMPLATES的DIRS中添加'./templates'
```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': ['./templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

* 添加以下代码
```python
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
ASGI_APPLICATION = 'Chat_Website_Tutorial.asgi.application'
```

### 3.7 目录结构

![](https://notes.sjtu.edu.cn/uploads/upload_77b3b99b1319b037e804847894205f5f.png)



## 四、用户登录界面

### 4.1 前端页面制作

* 在templates中新建users目录，在里面创建log.html并设计登录界面
* 在static文件夹下创建css、js、images三个文件夹，分别放css文件、javascript文件和静态图片

### 4.2 修改settings.py文件

* 在Chat_Website_Tutorial/settings.py中添加

### 4.3 创建User类
* 在users/models.py中添加用户类，以下是一个样例

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField('email address', primary_key=True, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]
```

### 4.4 注册User类
* users/admin.py中注册User类

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User, UserAdmin)
```

### 4.5 创建User相关的表单
* 由于用户注册和登录涉及到表单的填写与提交，因此需要在Users中创建forms.py文件，并在其中创建相关表单
```python
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.CharField()
    email_code = forms.CharField()
    class Meta:
        model = User
        fields = ("username", "email", "email_code", "password1", "password2")
        
class LoginForm(forms.Form):
    login_email = forms.CharField()
    login_password = forms.CharField()
```

### 4.6 添加请求处理函数
* django在处理Http请求时是通过自定义的视图函数进行处理的，需要在views.py中添加处理登录或者注册请求的函数
```python
from django.shortcuts import render, redirect
from django.http import HttpRequest
from .forms import LoginForm, RegisterForm
from django.contrib.auth import login, authenticate
from django.contrib import messages


def log(request: HttpRequest):
    # action when request method is GET
    if request.method == 'GET':
        register_form = RegisterForm()
        login_form = LoginForm()
        # context to render
        context = {
            "register_form": register_form,
            "login_form": login_form,
        }
    # action when request method is POST
    elif request.method == 'POST':
        # transform the request post to Forms 
        register_form = RegisterForm(request.POST)
        login_form = LoginForm(request.POST)
        # check whether login success
        if login_form.is_valid():
            email = login_form.cleaned_data["login_email"]
            password = login_form.cleaned_data["login_password"]
            # We check if the data is correct
            user = authenticate(email=email, password=password)
            if user:  # If the returned object is not None
                login(request, user)  # we connect the user
                return redirect('chat:my')
            else:  # otherwise an error will be displayed
                context = {
                    "register_form": register_form,
                    "login_form": login_form,
                    "login_error": "Error email or Error password!"
                }
        # check whether regist success
        elif register_form.is_valid():
            user = register_form.save()
            login(request, user)
            messages.success(request, "Congratulations, you are now a registered user!")
            return redirect('chat:my')
        # collect errors
        else:
            # return errors for user
            username_errors = register_form.errors.get('username')
            email_errors = register_form.errors.get('email')
            password_errors = register_form.errors.get('password2')
            context = {
                "register_form": register_form,
                "login_form": login_form,
                "username_errors": username_errors,
                "email_errors": email_errors,
                "password_errors":  password_errors,
            }            

    return render(
        request=request, 
        template_name='users/log.html', 
        context = context
    )
```
* log函数的输入是一个Http请求，函数首先判断请求的方式是GRT还是POST，然后分别进行处理，最后调用我们在4.1中制作完成的users/log.html模板，并将模板中需要的参数以字典的形式传入


### 4.7 添加访问路径(url)
* 在users中建立url.py文件
```python
from django.urls import path
from users import views

urlpatterns = [
    path('', views.log, name='log'),
]
```
* 修改Chat_Website_Tutorial/urls.py如下
```python
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(('users.urls', 'users'), namespace='users'), name='users'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

```
* 添加url之后，当在浏览器访问根目录（对应''）时，就会到log界面，调用log函数处理http请求


### 4.8 更新数据库
* 在根目录下创建update.py文件，内容如下
```python
import os

os.system("python manage.py makemigrations")
os.system("python manage.py migrate")
os.system("python manage.py runserver")
```

### 4.9页面展示
* 在浏览器中输入 http://127.0.0.1:8000/， 可以看到如下界面
![](https://notes.sjtu.edu.cn/uploads/upload_a4e5ca5521b7850e09d161843a8f0863.png)


### 4.10创建超级用户
* 在根目录下创建superuser.py文件
```python
import os
os.system("python manage.py createsuperuser")
```

### 4.11注册两个测试账号

* 根据注册要求注册test001和test002两个账号

![](https://notes.sjtu.edu.cn/uploads/upload_06902894e35d6cc975a676cb569e7208.png)
* 正常注册的时候应该看到如下界面
![](https://notes.sjtu.edu.cn/uploads/upload_d9d35ba53e3b2926f7629d087b4979ee.png)
* 这是因为我们在log函数中写了以下代码
```python
# check whether regist success
elif register_form.is_valid():
    user = register_form.save()
    login(request, user)
    messages.success(request, "Congratulations, you are now a registered user!")
    return redirect('chat:my')
```
* 当注册成功时会重定向到chat模块的my页面，但是由于我们暂时还没有写这一部分，因此会报错
* 当我们用4.10中创建的超级用户登录管理员界面 http://127.0.0.1:8000/admin， 可以看到两个账户已经被创建成功了

![](https://notes.sjtu.edu.cn/uploads/upload_bcba73537cb0282958ceeb54fc35f822.png)


## 五、用户主页设计

### 5.1 用户主页模板设计

* 将一个页面分成4个part部分
    * side_menus：侧边栏
    * leftsidebar：左侧部分
    * body：主体部分
    * rightsidebar：右侧部分
* 利用django特有的block机制，首先设计一个base.html，所有的页面都继承base.html，然后每一个html页面根据需求按照上述四个部分（不一定全部需要）分别设计
* 例如my页面设计如下：

```htmlmixed=
{% extends 'chat/base.html' %}

<!-- side_menu -->
{% block side_menu %}
    {% include "chat/side_menus/side_menu_my.html" %}
{% endblock %}
<!-- side_menu -->

<!-- leftsidebar -->
{% block leftsidebar %}
    {% include "chat/leftsidebar/leftsidebar_my.html" %}
{% endblock %}
<!-- leftsidebar -->

<!-- body -->
{% block chat_conversation %}
    {% include "chat/body/body_my.html" %}
{% endblock %}
<!-- body -->
```

* 编写好相关的html模板，如下所示

![](https://notes.sjtu.edu.cn/uploads/upload_4757528bdfb5d58f91d28839a51e61d6.png)

### 5.2 用户主页相关类的实现

* 与第四章介绍的一样，我们需要创建一些类、表单、路径、视图函数等，具体代码由于过长就不在这里一一列出，详细请直接参考代码文件包，以下是需要创建的相关内容。
* Profile类：用户的个人画像类
* EditProfileForm表单：修改Profile
* PasswordChangeForm表单：修改密码
* my函数，用户主页视图函数
* settings函数，用户设置页面视图函数
* chatroom函数，用户聊天界面视图函数（在第六章实现，这里需要放一个空函数）
* innerroom函数，用户聊天界面内部视图函数（在第六章实现，这里需要放一个空函数）
```python
@login_required
def chatroom(request: HttpRequest, dark=False):
    pass
    
@login_required
def innerroom(request: HttpRequest, room_name, post_name, dark=False):
   pass
```

### 5.3 signal

* 在设计User类的时候，并没有考虑到Profile类的初始化。实际上，我们希望的是在User类被创建的时候，就创建一个对应的Profile类，这需要通过信号函数实现
* 在chat文件夹下创建signal.py文件
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```
* 修改chat/apps.py如下
```python
from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"

    def ready(self):
        from . import signals
```

### 5.4 用管理员删除用户并重新注册用户

* 在执行了上述几个步骤后运行update，会发现以下情况

![](https://notes.sjtu.edu.cn/uploads/upload_3058c9f8deb3139489da279521e7e92e.png)

* 这是因为我们在注册用户之前还没有考虑过5.3，这时候需要我们登录管理员账号删除原本创建的两个用户，然后重新注册即可

![](https://notes.sjtu.edu.cn/uploads/upload_2d555547348166d665d0d8dcba75e0c6.png)

### 5.5 用户主页展示

![](https://notes.sjtu.edu.cn/uploads/upload_a1acde8daf9e8996d17c581021f86084.png)

### 5.6 更改用户个人信息

* 在settings界面上传个人图片并修改个人介绍，地点等


![](https://notes.sjtu.edu.cn/uploads/upload_3cde262dc6e4be0f0d328305eae3c151.png)



## 六、用户聊天设计

### 6.1 实时聊天原理：WebSocket
* 什么是WebSocket
    * WebSocket 是一种网络传输协议，可在单个 TCP 连接上进行全双工通信，位于 OSI 模型的应用层

* 为什么使用WebSocket
    * WebSocket可以在浏览器里使用且使用很简单
    * 客户端和服务器只需要完成一次握手，两者之间就可以创建持久性的连接，并进行双向数据传输。

* WebSocket建立过程

    * 客户端发送一个 HTTP GET 请求到服务器，请求的路径是 WebSocket 的路径（类似 ws://http://example.com/socket）。请求中包含一些特殊的头字段，如 Upgrade: websocket 和 Connection: Upgrade，以表明客户端希望升级连接为 WebSocket。
    * 服务器收到这个请求后，会返回一个 HTTP 101 状态码（协议切换协议）。同样在响应头中包含 Upgrade: websocket 和 Connection: Upgrade，以及一些其他的 WebSocket 特定的头字段，例如 Sec-WebSocket-Accept，用于验证握手的合法性。
    * 客户端和服务器之间的连接从普通的 HTTP 连接升级为 WebSocket 连接。之后，客户端和服务器之间的通信就变成了 WebSocket 帧的传输，而不再是普通的 HTTP 请求和响应。

### 6.2 用户聊天相关类的实现

* 与5.2一样，这里列出用户聊天相关类、表单等的简介
* models
    * Room类：聊天室
    * Tag类：标签
    * Post类：帖子
    * RoomMessage：聊天内容
* forms
    * RoomForm：创建聊天室的表单
    * PostForm：创建帖子的表单
    * AttachmentForm：附件相关表单
    * ChangeRoomForm：修改聊天室信息表单
    * EditPostForm：编辑帖子信息的表单
    * ConfirmDeletePostForm：删除帖子的表单
    * ConfirmDeleteChatroomForm：删除聊天室的表单
* views
    * chatroom：聊天室
    * innerroom：帖子
* 帖子和聊天室的关系
    * 每一个聊天室作为聊天的基本空间单位
    * 每一个聊天室在创建时会自动创建一个以chatting_开头的帖子，用于聊天
    * 在聊天室内部可以任意创建帖子，用于讨论相关话题

### 6.3 关键技术——roomers

* 在chat文件夹中创建roomers.py文件
```python
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Room, RoomMessage, Post


class Roommers(WebsocketConsumer):
    """
    The member of the Room
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None
```

* Roomers继承了Django库中一个重要的通信消费者类WebsocketConsumer
* Django Channels是一个用于构建实时Web应用程序的扩展，它使用了WebSocket和其他协议来实现实时通信。
* WebsocketConsumer用于处理WebSocket连接和消息的消费者，以下是它的一些重要方法
    * connect(self)：当一个WebSocket连接建立时，Channels将调用connect方法，在这个方法中执行与连接相关的初始化工作
    * disconnect(self, close_code)：当WebSocket连接关闭时，Channels将调用disconnect方法，执行一些清理工作。
    * receive(self, text_data=None, bytes_data=None)：当WebSocket接收到消息时，Channels将调用receive方法，处理接收到的消息。
    * send(self, text_data=None, bytes_data=None, close=False)：通过WebSocket发送消息给客户端。
    * group_send(self, group, message)：将消息发送给一个指定的组，用于实现广播消息或群聊功能。

* 以下是我对WebsocketConsumer类的connect的重构
    * 首先通过scope中包含的信息获得当前聊天室名称和帖子名称
    * room_group_name是一个特殊的变量，用于唯一标志特定的群组
    * 通过聊天室名称确定用户所在的room，并向当前用户发送他所在room的所有用户列表
    * 判断用户合法性，若合法，则向所在room的群组广播当前用户进入的信息
    * 对room实体的online变量添加当前用户
```python
def connect(self):
    # read info from self.scope
    self.room_name = self.scope['url_route']['kwargs']['room_name']
    self.post_name = self.scope['url_route']['kwargs']['post_name']
    self.room_group_name = f'chat_chatroom_{self.room_name}_{self.post_name}'
    self.room = Room.objects.get(name=self.room_name)
    self.user = self.scope['user']
    self.user_inbox = f'inbox_{self.user.username}'
    self.accept()
    async_to_sync(self.channel_layer.group_add)(
        self.room_group_name,
        self.channel_name,
    )

    # send all online users by self.send func
    self.send(json.dumps({
        'type': 'user_list',
        'users': [user.username for user in self.room.online.all()],
    }))

    # check if the user is valid
    if self.user.is_authenticated:
        # create a user inbox for private messages
        async_to_sync(self.channel_layer.group_add)(
            self.user_inbox,
            self.channel_name,
        )
        # send the join event to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'user_join',
                'user': self.user.username,
            }
        )
        self.room.online.add(self.user)
```
* disconnect原理与connect一致，代码不在这里展示
* 以下是我对WebsocketConsumer类的receive的重构
    * 这一部分与后面将会介绍的websocket.js相关
    * 当用户收到了消息，首先用json解析出其中的消息字典
    * 然后判断消息字典中是否存在"uid"的键值，若存在，说明这是一个删除聊天记录的命令
    * 若不存在，说明这是一个添加聊天的命令，需要向所在群组的所有用户广播这个聊天信息
```python
def receive(self, text_data=None, bytes_data=None):

    text_data_json = json.loads(text_data)
    if "uid" in text_data_json:
        uid = text_data_json['uid']
        rm = RoomMessage.objects.get(uid = uid)
        rm.delete()
    else:
        message = text_data_json['message']
        post_name = text_data_json['post_name']

        # check if the user is valid
        if not self.user.is_authenticated:
            return

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
            }
        )

        RoomMessage.objects.create(
            user=self.user, 
            room=self.room, 
            belong_post = Post.objects.get(title=post_name, belong_room=self.room),
            content=message
        )
```

### 6.4 asgi

* 在创建完毕roomers文件之后，需要再创建一个routing.py文件
```python
from django.urls import re_path
from .roomers import Roommers, FRRoommers

websocket_urlpatterns = [
    re_path(r'ws/chat/chatroom/(?P<room_name>\w+)/(?P<post_name>\w+)$', 
            Roommers.as_asgi()),
]
```


* 然后修改Chat_Website_Tutorial/asgi.py如下
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})

```

* 这么做的主要原因是为了将http请求和websocket请求分发到不同的处理程序


### 6.5 关键技术——websocket.js

* 在本报告中很少涉及css和js的介绍，这是因为作者认为读者应当自己掌握，但是websocket.js中涉及到了通信相关的内容，因此需要单独讲解一下其中涉及到的重要函数

* 以下是添加消息函数，这里采用的是当用户发送消息的时候，采用在js中添加html文本来实现实时聊天内容的增加
```javascript=
// add message
function add_message(user, message){
    img_url = user_img_urls[user];
    var flag = 0;
    if (img_url == undefined && flag == 0) {
        location.reload();
        flag = 1;
    }
    if (user != cur_user){
        chatLog.innerHTML += 
    `<li><div class="conversation-list" style="max-width: 40%;>
        <!-- HIS OR HER AVATAR -->
        <div class="chat-avatar"><img src=${img_url} alt=""></div>
        <!-- HIS OR HER AVATAR -->
        <!-- CONTENT MAIN -->
        <div class="user-chat-content" style="max-width: 100%;">
            <div class="ctext-wrap">
                <!-- CONTENT & TIME -->
                <div class="ctext-wrap-content" style="max-width: 100%;">
                    <p class="mb-0" style="word-break:break-all;">
                        ${message}
                    </p>
                </div>
                <!-- CONTENT & TIME -->
            </div>
            <!-- HIS OR HER NAME -->
            <div class="conversation-name">${user}</div>
        </div>
        <!-- CONTENT -->
    </div></li>`}
    else{        
        chatLog.innerHTML +=
    `<li class="right"><div class="conversation-list" style="max-width: 40%;">
        <!-- HIS OR HER AVATAR -->
        <div class="chat-avatar"><img src=${img_url} alt=""></div>
        <!-- HIS OR HER AVATAR -->
        <!-- CONTENT MAIN -->
        <div class="user-chat-content" style="max-width: 100%;">
            <div class="ctext-wrap">
                <!-- CONTENT & TIME -->
                <div class="ctext-wrap-content" style="max-width: 100%;">
                <p class="mb-0" style="word-break:break-all; text-align: left;">
                    ${message}
                </p>
                </div>
                <!-- CONTENT & TIME -->
            </div>
            <!-- HIS OR HER NAME -->
            <div class="conversation-name">${user}</div>
        </div>
        <!-- CONTENT -->
    </div></li>`
    }
}
```

* 以下是有用户进入或者离开时的处理
```python
# onlineUsersSelectorAdd
function onlineUsersSelectorAdd(user){
    if (document.querySelector("option[value='" + user + "']")) return;
    let newOption = document.createElement("option");
    newOption.value = user;
    newOption.innerHTML = user;
    onlineUsersSelector.appendChild(newOption);
}

# removes an option from 'onlineUsersSelector'
function onlineUsersSelectorRemove(user) {
    let oldOption = document.querySelector("option[value='" + user + "']");
    if (oldOption !== null) oldOption.remove();
}
```

* 以下是连接函数
* 其中"chat_message"、"user_list"这些type都是与chat/roomers.py中发送的消息字典对应的
* new WebSocket( ) 中的路径是与chat/routing.py中的路径是对应的
```javascript=
// connect
function connect() {
    chatSocket = new WebSocket("ws://" + 
                               window.location.host + 
                               "/ws/chat/chatroom/" + 
                               room_name +"/" + 
                               cur_post
                              );
    // connect the WebSocket
    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket.");
    }
    // deal with connection error
    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. 
                    Trying to reconnect in 2s...");
        setTimeout(function() {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };
    // deal with message error 
    chatSocket.onerror = function(err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
    // send message
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        switch (data.type) {
            case "chat_message":
                add_message(data.user, data.message);
                break;
            case "user_list":
                for (let i = 0; i < data.users.length; i++) 
                    onlineUsersSelectorAdd(data.users[i]);
                break;
            case "user_join":
                onlineUsersSelectorAdd(data.user);
                break;
            case "user_leave":
                onlineUsersSelectorRemove(data.user);
                break;
            default:
                console.error("Unknown message type!");
                break;
        }
        chatLog_container.scrollTop = chatLog.scrollHeight;
    }
    
}
```

### 6.6 signal
* 由于要求创建聊天室时自动创建一个帖子，并且我们希望聊天室在创建时会有一个创建成功的聊天记录，因此需要在chat/signal.py文件添加：
```python
from .models import Profile, RoomMessage, Room, Post, Tag
from django.shortcuts import get_object_or_404

@receiver(post_save, sender=Room)
def create_rm(sender, instance, created, **kwargs):
    if created:
        # create the default chatting_post
        author = User.objects.get(username=instance.owner_name)
        profile = get_object_or_404(Profile, user=author)
        post = Post.objects.create(
            title =  "chatting_" + instance.name,
            author = author, 
            author_profile = profile,
            about_post = "The special and default post for chatting",
            belong_room=instance, 
        )
        try:
            post.tags.add(get_object_or_404(Tag, name="default"))
            post.tags.add(get_object_or_404(Tag, name="chatting"))
        except:
            Tag.objects.create(name="default")
            Tag.objects.create(name="chatting")
            post.tags.add(get_object_or_404(Tag, name="default"))
            post.tags.add(get_object_or_404(Tag, name="chatting"))
        
        # create the defult success message for the chatting_post
        content = "Congratulations to {} for creating a new chatroom \
            named {}".format(instance.owner_name, instance.name)   
        RoomMessage.objects.create(
            user=author, 
            belong_post = post,
            room=instance, 
            content=content
        )
```


### 6.7 redis

* Redis（Remote Dictionary Server）是一个开源的内存数据存储系统，它提供了高性能、可扩展和灵活的键值存储。
* 在Chat_Website_Tutorial/settings.py添加以下代码，把channels的后端设置成redis
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}
```

### 6.8 页面展示

![](https://notes.sjtu.edu.cn/uploads/upload_c2f531acb137c093540b6722d844ef80.png)


## 七、实验总结与附加材料说明

### 7.1 程序文件列表

![](https://notes.sjtu.edu.cn/uploads/upload_a3da0026b1401fbc700aa0d71ca318b7.png)

### 7.2 体会与建议

* 聊天软件的制作有三大难点，一个是前端页面的制作，一个是django的系统学习，一个是websocket的熟练运用，这些都需要大量的前置学习
* 如何设计美观的界面是制作软件前必须要思考的问题，需要花较长时间去寻找和制作合适的html模板
* websocket、django的WebsocketConsumer类以及websocket.js以及asgi这些对象或者文件的关系需要熟练掌握
* 课程建议：建议可以将大作业改为多人合作

### 7.3 软件后续

* 目前软件实现了多人聊天、互传照片与文件等，后续还可以增加一些好友等其他功能
* 软件可以尝试搭建在服务器上，添加域名、升级成https和wss等

### 7.4附加材料说明

* 【启动redis.mp4】windows平台命令行启动redis server
* 【注册登录用户界面.mp4】如何注册账户以及修改用户个人信息
* 【用户聊天.mp4】两个用户的基本实时聊天（可支持多个用户）
* 【文件传输.mp4】用户之间文件和照片的传输，需要刷新显示
* 【消息撤回.mp4】撤回发送后的消息，需要刷新显示
* 【模式切换与退出.mp4】黑夜与白天模式的切换以及退出登录
