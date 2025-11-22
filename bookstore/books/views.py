# books/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Book, Category
from .forms import BookSearchForm

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.filter(is_active=True).select_related('category')
        
        # Lọc theo danh mục
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            category_ids = category.get_descendants_and_self_ids()
            queryset = queryset.filter(category_id__in=category_ids)

        # Sắp xếp
        sort_by = self.request.GET.get('sort', '-created_at') # Mặc định là hàng mới
        valid_sorts = [
            'title', '-title', 
            'price', '-price', 
            '-created_at'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = None
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            context['category'] = category
            context['subcategories'] = category.children.all()
            context['breadcrumb'] = category.get_ancestors()
        else:
            # Nếu không có danh mục nào được chọn, hiển thị các danh mục cấp cao nhất
            context['top_level_categories'] = Category.objects.filter(parent__isnull=True)
        
        # Giữ lại tham số sort khi chuyển trang
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    slug_field = 'slug'


class BookSearchView(ListView):
    model = Book
    template_name = 'books/search.html'
    context_object_name = 'books'

    def get_queryset(self):
        form = BookSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            queryset = Book.objects.filter(is_active=True)
            if q:
                queryset = queryset.filter(title__icontains=q) | queryset.filter(author__icontains=q)
            if category:
                queryset = queryset.filter(category=category)
            return queryset
        return Book.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookSearchForm(self.request.GET)
        return context