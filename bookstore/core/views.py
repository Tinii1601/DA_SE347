from django.views.generic import TemplateView
from django.shortcuts import render
from books.models import Product, Category

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            vn_category = Category.objects.get(slug='sach-viet-nam')
            vn_category_ids = vn_category.get_descendants_and_self_ids()
            context['new_vietnamese_books'] = Product.objects.filter(
                is_active=True, 
                category_id__in=vn_category_ids
            ).order_by('-created_at')[:8]
        except Category.DoesNotExist:
            context['new_vietnamese_books'] = Product.objects.none()

        context['new_books'] = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
        context['best_sellers'] = Product.objects.filter(is_active=True).order_by('-price')[:5]
        
        return context


