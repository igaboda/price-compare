from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from user.forms import LoginForm
from user.models import Favorite


class UserLogin(FormView):
    form_class = LoginForm
    template_name = 'user/login.html'
    success_url = '/'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(
            request=self.request,
            username=email,
            password=password,
        )
        if not user:
            get_user_model().objects.create_user(email, password)
        else:
            login(self.request, user)
        return super().form_valid(form)


def user_logout(request):
    logout(request)
    return redirect('product:product-search')


class FavoritesHandler(View):
    def post(self, request):
        current_user = request.user
        product_id = request.POST.get('product-id')
        action = request.POST.get('follow')
        if action == 'follow':
            favorite = Favorite()
            favorite.save()
            favorite.user.add(current_user)
            favorite.product_id.add(product_id)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
