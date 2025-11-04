from django.core.mail import send_mail
import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    return render(request, 'design/home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect('login')

    return render(request, 'design/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Generate OTP
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['temp_user_id'] = user.id

            # Send OTP to email
            subject = "Your Login OTP"
            message = f"Hello {user.username},\n\nYour One-Time Password (OTP) is: {otp}\n\nIf you didn’t request this, please ignore this email."
            from_email = None  # Uses DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.info(request, "An OTP has been sent to your email address.")
            except Exception as e:
                print(f"Error sending OTP email: {e}")
                messages.error(request, "Error sending OTP. Please try again.")
                return redirect('login')

            return redirect('otp_verify')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'design/login.html')


def otp_verify(request):
    if 'otp' not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = str(request.session.get('otp'))

        if entered_otp == stored_otp:
            user_id = request.session.get('temp_user_id')
            User = get_user_model()
            user = User.objects.get(id=user_id)
            login(request, user)

            # Clean up session
            request.session.pop('otp', None)
            request.session.pop('temp_user_id', None)

            messages.success(request, "OTP verified successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'design/otp.html')


@login_required(login_url='login')
def dashboard(request):
    user = request.user
    context = {'user': user}
    return render(request, 'design/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "You’ve been logged out.")
    return redirect('login')


def design_editor(request):
    """Main design editor view with Neuropilot ML integration"""
    context = {
        'user': request.user,
        'project_name': 'New Project',  # You can make this dynamic
    }
    return render(request, 'design/design_editor.html', context)