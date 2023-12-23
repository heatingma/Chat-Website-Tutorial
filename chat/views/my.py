from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from chat.models import Profile
from users.models import User


@login_required
def my(request: HttpRequest, dark=False):
    # judge the dark or light model
    if request.GET:
        dark = request.GET['dark']
        dark = False if dark == 'False' else True

    username = request.user.username
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)   
            
    return render(
        request=request, 
        template_name='chat/my.html', 
        context={
            'profile': profile,
            'dark': dark,
            'light': not dark,
        }
    )