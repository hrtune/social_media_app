from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.http import HttpResponse
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
from django.db.models import Q

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    user_following_list = [ q.user for q in user_following ]
    feed = [ Post.objects.filter(user=n) for n in user_following_list ]
    feed.append(Post.objects.filter(user=request.user.username))

    feed_list = list(chain(*feed))

    # list of user objects this user is not following
    suggestion_list = [ u for u in User.objects.all() if (u.username not in user_following_list) and (u.username != request.user.username) ]

    return render(request, 'index.html', { 'user_profile' : user_profile, 'posts' : feed_list, 'suggestion_list' : suggestion_list})

@login_required(login_url='signin')
def search(request):
    query = request.GET['q']
    if query:
        matched_users = User.objects.filter(username__icontains=query)
        user_profile = [ Profile.objects.get(id_user=u.id) for u in matched_users if  ]
    else:
        user_profile = list(Profile.objects.all())

    return render(request, 'search.html', { 'user_profile' : user_profile })

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if follower == user:
            return redirect(request.path)
        
        # if the user is already a follower then...
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            FollowersCount.objects.create(follower=follower, user=user)


        return redirect('/profile/' + user)
    # method is get then
    else:
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)
    followed = FollowersCount.objects.filter(follower=request.user.username, user=pk).first() != None
    user_following = len(FollowersCount.objects.filter(follower=pk))
    user_followers = len(FollowersCount.objects.filter(user=pk))

    context = {
        'user_object' : user_object, # user who owns this profile
        'user_profile' : user_profile,
        'user_posts' : user_posts,
        'user_posts_length' : user_posts_length,
        'followed' : followed,
        'user_following' : user_following,
        'user_followers' : user_followers,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        image = request.FILES.get('image_upload')
        if image != None:
            user = request.user.username
            caption = request.POST['caption']
            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()
        return redirect(request.path)

    # if the request is get...
    return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(username=username, post_id=post_id).first()

    if like_filter == None:
        LikePost.objects.create(username=username, post_id=post_id)
        post.num_of_likes += 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.num_of_likes -= 1
        post.save()
        return redirect('/')


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
        user_profile.profileimg = image
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
                Profile.objects.create(user=user_model, id_user=user_model.id)
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