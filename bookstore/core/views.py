from django.views.generic import TemplateView
from django.shortcuts import render
from books.models import Product, Category

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Sách Trong Nước (lấy từ category 'sach-viet-nam' hoặc 'sach-trong-nuoc')
        try:
            # Ưu tiên tìm slug 'sach-viet-nam' như cũ, hiển thị là "Sách Trong Nước"
            vn_category = Category.objects.filter(slug__in=['sach-viet-nam', 'sach-trong-nuoc']).first()
            if vn_category:
                vn_category_ids = vn_category.get_descendants_and_self_ids()
                context['domestic_books'] = Product.objects.filter(
                    is_active=True, 
                    category_id__in=vn_category_ids
                ).order_by('-created_at')[:10]
            else:
                context['domestic_books'] = Product.objects.none()
        except:
            context['domestic_books'] = Product.objects.none()

        # 2. Sách Mới Nhất - Ưu tiên Văn Học
        try:
            lit_category = Category.objects.filter(slug__in=['van-hoc', 'van-hoc-nghe-thuat']).first()
            if lit_category:
                lit_ids = lit_category.get_descendants_and_self_ids()
                context['new_books'] = Product.objects.filter(
                    is_active=True,
                    category_id__in=lit_ids
                ).order_by('-created_at')[:10]
            else:
                 # Fallback nếu không có danh mục Văn học
                context['new_books'] = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
        except:
            context['new_books'] = Product.objects.none()

        # 3. Sách Nổi Bật - Lấy từ Tiểu Thuyết
        try:
            novel_category = Category.objects.filter(slug__in=['tieu-thuyet']).first()
            if novel_category:
                novel_ids = novel_category.get_descendants_and_self_ids()
                context['best_sellers'] = Product.objects.filter(
                    is_active=True,
                    category_id__in=novel_ids
                ).order_by('-created_at')[:10] # Hoặc order theo logic khác
            else:
                 # Fallback
                context['best_sellers'] = Product.objects.filter(is_active=True).order_by('-price')[:5]
        except:
             context['best_sellers'] = Product.objects.none()
        
        return context


