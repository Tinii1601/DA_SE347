from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .forms import BookSearchForm
from orders.forms import CartAddProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Lọc theo danh mục
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            category_ids = category.get_descendants_and_self_ids()
            queryset = queryset.filter(category_id__in=category_ids)

        # Sắp xếp
        sort_by = self.request.GET.get('sort', '-created_at') # Mặc định là hàng mới
        valid_sorts = [
            'name', '-name', 
            'price', '-price', 
            '-created_at'
        ]
        
        # Map title sorting to name for backward compatibility in URL params
        if sort_by == 'title': sort_by = 'name'
        if sort_by == '-title': sort_by = '-name'

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

class ProductDetailView(DetailView):
    model = Product
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_product_form'] = CartAddProductForm()
        approved_reviews = self.object.reviews.filter(is_approved=True)
        total_reviews = approved_reviews.count()
        rating_counts = {i: approved_reviews.filter(rating=i).count() for i in range(1, 6)}
        rating_percent = {
            i: int((rating_counts[i] / total_reviews) * 100) if total_reviews else 0
            for i in range(1, 6)
        }
        rating_rows = [
            {"star": i, "count": rating_counts[i], "percent": rating_percent[i]}
            for i in range(5, 0, -1)
        ]
        avg_rating = (
            sum(rating * count for rating, count in rating_counts.items()) / total_reviews
            if total_reviews else 0
        )
        context["approved_reviews"] = approved_reviews
        context["total_reviews"] = total_reviews
        context["rating_rows"] = rating_rows
        context["avg_rating"] = avg_rating
        
        # Breadcrumb logic
        if self.object.category:
            context['breadcrumb'] = self.object.category.get_ancestors()
            context['category'] = self.object.category
            
        return context


class ProductSearchView(ListView):
    model = Product
    template_name = 'books/search.html'
    context_object_name = 'books'

    def get_queryset(self):
        form = BookSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            queryset = Product.objects.filter(is_active=True)
            if q:
                queryset = queryset.filter(name__icontains=q)
            if category:
                queryset = queryset.filter(category=category)
            return queryset
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookSearchForm(self.request.GET)
        return context
