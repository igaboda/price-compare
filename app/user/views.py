from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import redirect
from django.urls import reverse

from user.forms import LoginForm
from libs.utils import handle_favorite


class UserLogin(FormView):
    """Logs in user if already exists, otherwise creates user and logs in."""
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
            user = get_user_model().objects.create_user(email, password)

        prod_ids = self.request.session.get('searched_products', None)
        fav_dict = self.request.session.get('favorite', None)

        login(self.request, user)

        if prod_ids:
            self.request.session['searched_products'] = prod_ids

        # handle favorite if user was redirected to login from favorite form
        if fav_dict:
            handle_favorite(fav_dict, user)
            del self.request.session['favorite']

        return super().form_valid(form)

    def get_success_url(self):
        if 'searched_products' in self.request.session:
            return reverse('product:search-results')
        super().get_success_url()


def user_logout(request):
    logout(request)
    return redirect('product:product-search')


class FavoritesHandler(View):
    """Follows or unfollows given product in user's favorites. If user not authenticated then redirects to login view."""
    def post(self, request):
        product_id = request.POST.get('product-id')
        action = request.POST.get('action')
        fav_dict = {'action': action, 'product-id': product_id}

        if not request.user.is_authenticated:
            request.session['favorite'] = fav_dict
            return redirect('user:login')

        handle_favorite(fav_dict, request.user)

        return redirect('product:search-results')
