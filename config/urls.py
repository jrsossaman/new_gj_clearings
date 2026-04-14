"""
URL configuration for new_gj_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
import app.views

urlpatterns = [
#    path("admin/", admin.site.urls),

# === LOGIN / OUT === #
    path("", app.views.handle_login, name="login"),
    path("logout/", app.views.auth_views.LogoutView.as_view(), name="logout"),

#|==========================|
#|-- GRACE-SIDE FUNCTIONS --|
#|==========================|

# === DASHBOARD & ACCOUNT MANAGEMENT === #
    path("dashboard/", app.views.render_dashboard, name="dashboard"),
    path("account_select/", app.views.account_select, name="account_select"),
    path("create_account/", app.views.create_account, name="create_account"),
    path("deactivate_account/", app.views.deactivate, name="deactivate"),
    path("activate_account/", app.views.activate, name="activate"),
    path("delete_account", app.views.delete_account, name="delete_account"),

# === INDIVIDUAL CLIENTS / LOCATIONS C.R.U.D. === #
    path("account_overview/", app.views.account_overview, name="overview"),
    path("add_client/", app.views.add_client, name="add_client"),
    path("add_location/", app.views.add_location, name="add_location"),
    path("edit_client/<int:pk>/", app.views.edit_client, name="edit_client"),
    path("edit_location/<int:pk>/", app.views.edit_location, name="edit_location"),
    path("delete_client/<int:pk>/", app.views.delete_client, name="delete_client"),
    path("delete_location/<int:pk>/", app.views.delete_location, name="delete_location"),

# === WORKSHEET === #
    path("worksheet/", app.views.worksheet, name="worksheet"),
    path("previous_sessions/", app.views.previous_sessions, name="previous_sessions"),

#|============================|
#| -- CLIENT-SIDE FUNCTIONS --|
#|============================|

# === PROFILE VIEWS === #
    path("profile/", app.views.profile, name="profile"),
    path("overview/", app.views.overview, name="overview"),
    path("summary/", app.views.summary, name="summary"),
    path("information/", app.views.information, name="information"),

# === PASSWORD HANDLING === #


]
