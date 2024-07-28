from secrets import token_hex

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView
from requests import Timeout

from .models import Profile, Declaration, Author
from .parser import Parser


class CustomLogoutView(LogoutView):
    http_method_names = "get"

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse("api:index"))


class IndexTemplateView(TemplateView):
    template_name = "api/index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        kwargs["auth"] = self.request.user.is_authenticated
        return super().get(request, *args, **kwargs)


@csrf_exempt
def get_declaration(request: HttpRequest):
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        return JsonResponse({"error": "X-API-KEY header required"}, status=400)
    try:
        profile = Profile.objects.get(api_key=api_key)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "wrong api_key"}, status=403)

    profile.requests_count += 1
    profile.save()
    headers = {
        "requests_count": profile.requests_count
    }

    declaration_id = request.GET.get("id")

    if not declaration_id:
        response = {
            "available_ids": [i for i in Declaration.objects.values_list("id", flat=True)]
        }
        return JsonResponse(response, headers=headers)

    try:
        declaration = Declaration.objects.select_related("author").get(id=declaration_id)
    except Declaration.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404, headers=headers)

    return JsonResponse(declaration.as_dict(), headers=headers)


class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "api/profile.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        if self.request.user.is_superuser:
            kwargs["super"] = True
        else:
            kwargs["key"] = Profile.objects.get(user=self.request.user).api_key

        return super().get(request, *args, **kwargs)


class LoadDataTemplateView(UserPassesTestMixin, TemplateView):
    template_name = "api/load_data.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request: HttpRequest, *args, **kwargs):
        try:
            data = Parser.run(10)
            if data is not None:
                kwargs["data"] = data
                for declaration, author in kwargs["data"]:
                    declaration["author"] = Author.objects.create(**author)
                    Declaration.objects.create(**declaration)
        except Timeout:
            kwargs["timeout"] = True

        return super().get(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "api/register.html"
    success_url = reverse_lazy("api:profile")

    @staticmethod
    def _gen_api_key():
        api_key = token_hex(20)
        while Profile.objects.filter(api_key=api_key).exists():
            api_key = token_hex(20)
        return api_key

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object, api_key=self._gen_api_key())

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)
        return response
