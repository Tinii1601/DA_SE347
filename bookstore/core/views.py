# core/views.py
from django.views.generic import TemplateView
from django.shortcuts import render
from books.models import Book, Category

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy 8 sách mới nhất từ danh mục "Sách Việt Nam" và các con của nó
        try:
            # Giả sử slug của danh mục "Sách Việt Nam" là 'sach-viet-nam'
            vn_category = Category.objects.get(slug='sach-viet-nam')
            vn_category_ids = vn_category.get_descendants_and_self_ids()
            context['new_vietnamese_books'] = Book.objects.filter(
                is_active=True, 
                category_id__in=vn_category_ids
            ).order_by('-created_at')[:8]
        except Category.DoesNotExist:
            context['new_vietnamese_books'] = Book.objects.none()

        # Bạn có thể giữ lại hoặc thay đổi logic cho các mục khác
        context['new_books'] = Book.objects.filter(is_active=True).order_by('-created_at')[:10]
        context['best_sellers'] = Book.objects.filter(is_active=True).order_by('-price')[:5]
        
        return context


