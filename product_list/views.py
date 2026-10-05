from django.views.generic import ListView

from general.view_mixins import GetVerboseNameMixin
from product_list.models import Product


class ProductListView(GetVerboseNameMixin, ListView):
    model = Product
