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
        queryset = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
        
        # Lọc theo danh mục
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            category_ids = category.get_descendants_and_self_ids()
            queryset = queryset.filter(category_id__in=category_ids)

        # Lọc theo khoảng giá (preset)
        price_range = self.request.GET.get('price_range', '').strip()
        if price_range == '0-100':
            queryset = queryset.filter(price__lte=100000)
        elif price_range == '100-200':
            queryset = queryset.filter(price__gte=100000, price__lte=200000)
        elif price_range == '200-500':
            queryset = queryset.filter(price__gte=200000, price__lte=500000)
        elif price_range == '500-up':
            queryset = queryset.filter(price__gte=500000)

        # Lọc theo khoảng giá tùy chỉnh (min - max)
        price_min = self.request.GET.get('price_min', '').strip()
        price_max = self.request.GET.get('price_max', '').strip()
        if price_min:
            try:
                queryset = queryset.filter(price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                queryset = queryset.filter(price__lte=float(price_max))
            except ValueError:
                pass

        # Lọc theo tồn kho
        in_stock = self.request.GET.get('in_stock', '').strip()
        if in_stock in ['1', 'true', 'on']:
            queryset = queryset.filter(stock__gt=0)

        # Lọc theo khuyến mãi
        on_sale = self.request.GET.get('on_sale', '').strip()
        if on_sale in ['1', 'true', 'on']:
            queryset = queryset.filter(discount_percentage__gt=0)

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
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            context['category'] = category
            context['subcategories'] = category.children.filter(is_active=True)
            context['breadcrumb'] = category.get_ancestors()
        else:
            # Nếu không có danh mục nào được chọn, hiển thị các danh mục cấp cao nhất
            context['top_level_categories'] = Category.objects.filter(parent__isnull=True, is_active=True)
        
        # Lọc params hiện tại
        price_range = self.request.GET.get('price_range', '').strip()
        price_min = self.request.GET.get('price_min', '').strip()
        price_max = self.request.GET.get('price_max', '').strip()
        in_stock = self.request.GET.get('in_stock', '').strip() in ['1', 'true', 'on']
        on_sale = self.request.GET.get('on_sale', '').strip() in ['1', 'true', 'on']

        active_filters = []
        if price_range == '0-100':
            active_filters.append({'key': 'price_range', 'label': 'Dưới 100.000₫'})
        elif price_range == '100-200':
            active_filters.append({'key': 'price_range', 'label': '100.000₫ - 200.000₫'})
        elif price_range == '200-500':
            active_filters.append({'key': 'price_range', 'label': '200.000₫ - 500.000₫'})
        elif price_range == '500-up':
            active_filters.append({'key': 'price_range', 'label': 'Trên 500.000₫'})

        if price_min and price_max:
            active_filters.append({'key': 'custom_price', 'label': f'{int(float(price_min)):,}₫ - {int(float(price_max)):,}₫'.replace(',', '.')})
        elif price_min:
            active_filters.append({'key': 'price_min', 'label': f'Từ {int(float(price_min)):,}₫'.replace(',', '.')})
        elif price_max:
            active_filters.append({'key': 'price_max', 'label': f'Đến {int(float(price_max)):,}₫'.replace(',', '.')})

        if in_stock:
            active_filters.append({'key': 'in_stock', 'label': 'Chỉ còn hàng'})
        if on_sale:
            active_filters.append({'key': 'on_sale', 'label': 'Đang giảm giá'})

        context['current_price_range'] = price_range
        context['current_price_min'] = price_min
        context['current_price_max'] = price_max
        context['current_in_stock'] = in_stock
        context['current_on_sale'] = on_sale
        context['active_filters'] = active_filters
        context['has_active_filters'] = bool(active_filters)

        # Giữ lại tham số sort khi chuyển trang
        current_sort = self.request.GET.get('sort', '-created_at')
        context['current_sort'] = current_sort

        # Query strings cho pagination và sort link
        q_no_page = self.request.GET.copy()
        if 'page' in q_no_page:
            q_no_page.pop('page')
        context['query_params_no_page'] = q_no_page.urlencode()

        q_no_sort = self.request.GET.copy()
        if 'sort' in q_no_sort:
            q_no_sort.pop('sort')
        if 'page' in q_no_sort:
            q_no_sort.pop('page')
        context['query_params_no_sort'] = q_no_sort.urlencode()
        
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
        context["avg_rating"] = round(avg_rating, 1)

        user_review = None
        if self.request.user.is_authenticated:
            user_review = approved_reviews.filter(user=self.request.user).first()
        context["user_review"] = user_review
        
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
            queryset = Product.objects.filter(is_active=True, category__is_active=True)
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
