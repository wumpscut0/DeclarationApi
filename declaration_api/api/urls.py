from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import IndexTemplateView, ProfileTemplateView, RegisterView, CustomLogoutView, LoadDataTemplateView, \
    get_declaration

app_name = "api"

urlpatterns = [
    path("", view=IndexTemplateView.as_view(), name="index"),
    path("register/", view=RegisterView.as_view(), name="register"),
    path("logout", view=CustomLogoutView.as_view(), name="logout"),
    path("login/", view=LoginView.as_view(
        template_name="api/login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("accounts/profile/", view=ProfileTemplateView.as_view(), name="profile"),
    path("accounts/profile/load_data", view=LoadDataTemplateView.as_view(), name="load_data"),
    path("api/v1/declaration", view=get_declaration, name="declaration_api"),
]
