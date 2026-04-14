from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.db import transaction



from .models import *
from .forms import *

# Create your views here.


# === LOGIN === #

def handle_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect("dashboard")
                else:
                    return redirect("overview")
                
        else:
            form.add_error("Invalid email or password.")
    
    else:
        form = LoginForm()

    print("FORM ERRORS:", form.errors)
    return render(request, "login.html", {"form": form})


# --- ADMIN TEST --- #
def is_admin(user):
    return user.is_staff


#|==========================|
#|-- GRACE-SIDE FUNCTIONS --|
#|==========================|

# === DASHBOARD & ACCOUNT SELECT === #

    # --- ACCOUNT CHECKER --- #
# def get_account(request):
#     account_id = request.session.get('account_id')
#     if not account_id:
#         return None
#     try:
#         return Client.objects.get(id=account_id)
#     except Client.DoesNotExist:
#         return None
    


@login_required
@user_passes_test(is_admin)
def render_dashboard(request):
    account = None
    account_id = request.session.get('account_id')
    if account_id:
        try:
            account = Client.objects.get(id=account_id)
            return redirect("account_overview")
        except Client.DoesNotExist:
            account = None

    if request.method == "POST":
        form = ClientSelectForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data("client")
            request.session['account'] = account.id
            return redirect("dashboard")
    else:
        form = ClientSelectForm(initial={'client': account}) if account else ClientSelectForm()

    return render("dashboard")



def account_select(request):
    if 'account' in request.session:
        del request.session['account']
    return redirect('dashboard')



# === CREATE NEW ACCOUNT === #

User = get_user_model()
@login_required
@user_passes_test(is_admin)
def create_account(request):
    if request.method == "POST":
        client_form = UserClientCreationForm(request.POST)
        user_form = UserCreationForm(request.POST)
        if client_form.is_valid() and user_form.is_valid():
            email = user_form.cleaned_data("email")
            password = user_form.cleaned_data("password") # delete this line for production, will be handled by 'user.set_unusable_password()' below
            user = User.objects.create_user(username=email, email=email, password=password) # delete 'password=password', added here for testing.
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password() # this will enable user-created passwords on password reset email
            user.save()

            profile = Profile.objects.create(user=user)
            profile.save()

            client = client_form.save(commit=False)
            client.profile = profile
            client.email = email #-----------------------> # necessary?
            if not profile.clients.exists():
                client.is_user = True
            else:
                client.is_user = False
            client.save()

            # -- client reset password -- #
            reset_form = PasswordResetForm({'email': email})
            if reset_form.is_valid():
                reset_form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name = 'password_reset.html',
                )

            messages.success(request, f"User {email} created and password reset email sent.")
            return render(request, 'create_account', {
                "client_form": client_form, 
                "user_form": user_form
                })
    else:
        client_form = UserClientCreationForm()
        user_form = UserCreationForm()
    return render(request, 'create_account', {
        "client_form": client_form,
        "user_form": user_form,
    })



### === GET ACCOUNT INFO === ###
#-- for use in following admin methods --#
def get_account(request):
    account = None
    account_id = request.session.get('account', None)
    if account_id:
        account = Client.objects.get(id=account_id)
        return account



# === DEACTIVATE / ACTIVATE ACCOUNT === #

@login_required
@user_passes_test(is_admin)
def deactivate(request):
    account = get_account(request)
    
    form = ConfirmPasswordForm()

    if account.is_user == True:
        if request.method == "POST":
            form = ConfirmPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                authenticated_user = authenticate(username=request.user.username, password=password)
                if authenticated_user is not None:
                    try:
                        account.is_active = False
                        account.save()
                        return redirect('overview')
                    except Exception:
                        messages.error(request, f"Oops, something went wrong deactivating {account.first_name} {account.last_name}'s account.")
                else:
                    messages.error(request, f"Incorrect password.")
            else:
                form = ConfirmPasswordForm()
        return render(request, 'deactivate.html', {'form': form, 'account': account})
    

@login_required
@user_passes_test(is_admin)
def activate(request):
    account = get_account(request)
    
    form = ConfirmPasswordForm()

    if account.is_user == True:
        if request.method == "POST":
            form = ConfirmPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                authenticated_user = authenticate(username=request.user.username, password=password)
                if authenticated_user is not None:
                    try:
                        account.is_active = True
                        account.save()
                        return redirect('overview')
                    except Exception:
                        messages.error(request, f"Oops, something went wrong deactivating {account.first_name} {account.last_name}'s account.")
                else:
                    messages.error(request, f"Incorrect password.")
            else:
                form = ConfirmPasswordForm()
        return render(request, 'deactivate.html', {'form': form, 'account': account})
    


# === DELETE ACCOUNT === #

@login_required
@user_passes_test(is_admin)
def delete_account(request):
    account = get_account(request)

    form = ConfirmPasswordForm()

    profile = account.profile
    user = User.objects.get(profile=profile)

    if account.is_user == True:
        if request.method == 'POST':
            form = ConfirmPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                authenticated_user = authenticate(username=request.user.username, password=password)
                if authenticated_user is not None:
                    try:
                        with transaction.atomic():
                            account.c_worksheets.all().delete()
                            for location in account.profile.locations_by_profile.all():
                                location.l_worksheets.all().delete()
                            print("l_sheets deleted")
                            account.delete()
                            print("account deleted")
                            profile.locations_by_profile.all().delete()
                            print("locations deleted")
                            profile.clients.all().delete()
                            print("clients deleted")
                            profile.delete()
                            print("profile deleted")
                            user.delete()
                            print("user deleted")

                            messages.success(request, f"Account has been permanently deleted.")
                            return redirect('dashboard')
                    except Exception as e:
                        print("THIS: ", repr(e))
                        raise
                        messages.error(request, f"An error occurred.")
                        return redirect('admin_client_overview')
                else:
                    messages.error(request, "Incorrect password.")
                    return redirect('delete_account')
            else:
                messages.error(request, "Please enter a valid password.")
        else:
            form = ConfirmPasswordForm()
    return render(request, 'delete_account.html', {'form': form, 'account': account})



# === ACCOUNT OVERVIEW === #

@login_required
@user_passes_test(is_admin)
def account_overview(request):
    account = get_account(request)

    account_owner = Client.objects.get(id=account.id) # might break
    clients = Client.objects.filter(profile=account.profile)
    locations = Location.objects.filter(profile=account.profile)

    context = {
        'account': account,
        'account_owner': account_owner,
        'clients': clients,
        'locations': locations,
    }

    return render(request, 'account_overview.html', context)



# === ADD CLIENT === #

@login_required
@user_passes_test(is_admin)
def add_client(request):
    account = get_account(request)
    form = AdditionalClientCreationForm()

    if request.method == "POST":
        if form.is_valid():
            client = form.save(commit=False)
            client.profile = account.profile
            client.is_user = False
            client.save()
            return redirect('overview')
    else:
        form = AdditionalClientCreationForm()

    return render(request, 'add_client.html', {'form': form,})
        


# === ADD LOCATION === #

@login_required
@user_passes_test(is_admin)
def add_location(request):
    account = get_account(request)
    form = LocationCreationForm()

    if request.method == "POST":
        if form.is_valid():
            location = form.save(commit=False)
            location.profile = account.profile
            location.save()
            return redirect('overview')
    else:
        form = LocationCreationForm()

    return render(request, 'add_client.html', {'form': form,})



# === EDIT CLIENT === #