from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.http import HttpResponse
from .models import Profile

@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')

@login_required(login_url='signin')
def upload(request):
    return HttpResponse("<h1>Upload View</h1>")

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')

        email = request.POST['email']
        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.user.email = email
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect(request.path)

    return render(request, 'setting.html', { 'user_profile' : user_profile })

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log the user in and redirect to setting page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')

        else:
            # about messages :  https://docs.djangoproject.com/en/4.1/ref/contrib/messages/
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None: # if authenticated,
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')