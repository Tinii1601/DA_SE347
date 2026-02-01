# core/context_processors.py
from django.db.models import Prefetch
from books.models import Category

def categories_processor(request):
    """
    Cung cấp danh sách các thể loại cha (top-level) cho mọi template.
    Mỗi thể loại cha sẽ chứa các thể loại con của nó.
    """
    # Lấy các danh mục cha (không có parent) và tải trước các con của chúng để tối ưu
    active_children = Prefetch(
        'children',
        queryset=Category.objects.filter(is_active=True).prefetch_related(
            Prefetch('children', queryset=Category.objects.filter(is_active=True))
        )
    )
    parent_categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related(active_children)
    return {
        'parent_categories': parent_categories
    }
