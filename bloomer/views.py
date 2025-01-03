from django.shortcuts import render
from django.http import JsonResponse
from .models import*

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth import get_user_model
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import CustomUserCreationForm
from django.shortcuts import get_object_or_404
import datetime
# Create your views here
User = get_user_model()  # Dynamically get the user model



@login_required
def map(request):
    # Get the current day of the week (0=Monday, 6=Sunday)
    today_index = datetime.datetime.today().weekday()

    # Map index to model fields
    day_mapping = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    today_field = day_mapping[today_index]

    user_steps, created = Steps.objects.get_or_create(user=request.user)

    totalsteps = user_steps.total_steps()
    percentages = {}
    if totalsteps > 0:
        percentages = {
            'monday': (user_steps.monday / total_steps) * 100,
            'tuesday': (user_steps.tuesday / total_steps) * 100,
            'wednesday': (user_steps.wednesday / total_steps) * 100,
            'thursday': (user_steps.thursday / total_steps) * 100,
            'friday': (user_steps.friday / total_steps) * 100,
            'saturday': (user_steps.saturday / total_steps) * 100,
            'sunday': (user_steps.sunday / total_steps) * 100,
        }

    # Check if the user has steps data
    

    # Reset steps if today is Sunday
    if today_index == 6:  # Sunday
        user_steps.monday = 0
        user_steps.tuesday = 0
        user_steps.wednesday = 0
        user_steps.thursday = 0
        user_steps.friday = 0
        user_steps.saturday = 0
        user_steps.sunday = 0
        user_steps.save()

    # Get today's steps dynamically
    today_steps = getattr(user_steps, today_field, 0)

    # Pass step data to the template
    context = {
        'steps': user_steps,
        'total_steps': user_steps.total_steps(),
        'today_steps': today_steps,
        'percentages': percentages,
    }
    return render(request, 'map/map.html', context)

@login_required
def update_steps(request):
    if request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body)
            new_steps = data.get('steps', 0)

            if not isinstance(new_steps, int) or new_steps < 0:
                return JsonResponse({'error': 'Invalid steps value'}, status=400)

            # Get the current day of the week (0=Monday, 6=Sunday)
            today_index = datetime.datetime.today().weekday()

            # Map index to model fields
            day_mapping = {
                0: "monday",
                1: "tuesday",
                2: "wednesday",
                3: "thursday",
                4: "friday",
                5: "saturday",
                6: "sunday",
            }
            today_field = day_mapping[today_index]

            # Update steps for the current user and day
            user_steps, created = Steps.objects.get_or_create(user=request.user)
            setattr(user_steps, today_field, new_steps)
            user_steps.save()

            return JsonResponse({
                'message': 'Steps updated successfully',
                'today': today_field,
                'steps': new_steps,
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def prof(request):
    # Your logic here
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None  # Handle case when no profile exists
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    posts_with_details = [
        {
            'post': post,
            'like_count': post.like_count(),
            'created_at': post.created_at,
            'image': post.image.url if post.image else None,
        }
        for post in posts
    ]
    following =user.following.count()
    followers =user.followers.count()
    total_posts =user.posts.count()
    return render(request,'profile/profile.html', {'posts_with_details': posts_with_details,'following': following,'followers':followers,'total_posts': total_posts,'profile': profile})

@login_required
def user_posts(request, username):
    """
    Display posts created by a specific user.
    """
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    posts_with_details = [
        {
            'post': post,
            'like_count': post.like_count(),
            'created_at': post.created_at,
            'image': post.image.url if post.image else None,
        }
        for post in posts
    ]
    following = user.following.count()
    followers = user.followers.count()
    total_posts = user.posts.count()
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None  # Handle case when no profile exists

    is_following = user.followers.filter(id=request.user.id).exists()

    return render(
        request,
        'home/uspro.html',
        {
            'user': user,
            'posts_with_details': posts_with_details,
            'following': following,
            'followers': followers,
            'total_posts': total_posts,
            'profile': profile,
            'is_following': is_following,
        },
    )
    

@login_required   
def postpage(request):
    # Your logic here
    return render(request, 'post.html')

@login_required
def upload_post(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        post = Post.objects.create(user=request.user, image=image)
        return JsonResponse({"message": "Post uploaded successfully", "post_id": post.id}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def upload_profile(request):
    if request.method == "POST" and request.FILES.get("pic"):
        # Get the uploaded profile picture
        pic = request.FILES["pic"]
        
        # Check if the user already has a profile, if not, create one
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Assign the new profile picture if it was uploaded
        profile.pic = pic
        profile.save()  # Save the profile with the new picture
        
        return JsonResponse({"message": "Profile picture uploaded successfully", "profile_id": profile.id}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)
    
@login_required
def feed(request):
    """
    Display all posts created by all users.
    """
    user = request.user
    following = user.following.all()  # Get all users the user is following
    following_with_profiles = [
        {
            'username': followed_user.username,
            'profile': followed_user.profile.pic.url if hasattr(followed_user, 'profile') and followed_user.profile.pic else None
        }
        for followed_user in following
    ]

    # Fetch all posts
    posts = Post.objects.all().order_by('-created_at')  # Latest posts first
    posts_with_details = [
        {
            'post': post,
            'like_count': post.like_count(),
            'created_at': post.created_at,
            'username': post.user.username,
            'pic': post.user.profile.pic.url if hasattr(post.user, 'profile') and post.user.profile.pic else None,
            'image': post.image.url if post.image else None,  # Ensure correct access to image URL
        }
        for post in posts
    ]

    return render(
        request, 
        'home/index.html', 
        {'posts_with_details': posts_with_details, 'posts': posts, 'following_with_profiles': following_with_profiles}
    )

def register(request):
    """
    Register a new user.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('http://127.0.0.1:8000/login')  # Update the URL as needed
        else:
            messages.error(request, "Error occurred during registration. Please check the form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    """
    Log in a user.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('feed')  # Redirect to the feed or any other page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def follow_user(request, username):
    """
    Toggle follow/unfollow for a user and return the updated state.
    """
    target_user = get_object_or_404(User, username=username)

    if request.method == "POST":
        if target_user != request.user:
            if target_user.followers.filter(id=request.user.id).exists():
                target_user.followers.remove(request.user)
                is_following = False
            else:
                target_user.followers.add(request.user)
                is_following = True

            # Return updated follower count and follow status
            return JsonResponse({
                "success": True,
                "is_following": is_following,
                "followers": target_user.followers.count(),
            })

    return JsonResponse({"success": False})


@login_required
def following_list(request, username):
    """
    View users a specific user is following.
    """
    user = get_object_or_404(User, username=username)
    following = user.following.all()  # Get all users the user is following
    return render(request, 'map/following.html', {'user': user, 'following': following})

@login_required
def followers_list(request, username):
    """
    View followers of a specific user.
    """
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()  # Get all followers of the user
    return render(request, 'map/followers.html', {'user': user, 'followers': followers})
