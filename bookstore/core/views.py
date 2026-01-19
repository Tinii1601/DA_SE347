# core/views.py
import math
import re
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from books.models import Book, Category
from .models import Store, ContentPage, NewsPost
from .forms import ContactForm

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


class StoreListView(ListView):
    model = Store
    template_name = "stores.html"
    context_object_name = "stores"

    def get_queryset(self):
        qs = Store.objects.filter(is_active=True)
        city = self.request.GET.get("city")
        if city:
            qs = qs.filter(city=city)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = (
            Store.objects.filter(is_active=True)
            .exclude(city="")
            .values_list("city", flat=True)
            .distinct()
            .order_by("city")
        )
        context["selected_city"] = self.request.GET.get("city", "")
        return context


class ContentPageDetailView(DetailView):
    model = ContentPage
    template_name = "page_detail.html"
    context_object_name = "page"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class NewsListView(TemplateView):
    template_name = "news_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        promo_posts = NewsPost.objects.filter(
            is_active=True, category=NewsPost.CATEGORY_PROMO
        ).order_by("-created_at")
        event_posts = NewsPost.objects.filter(
            is_active=True, category=NewsPost.CATEGORY_EVENT
        ).order_by("-created_at")
        context["promo_posts"] = promo_posts
        context["event_posts"] = event_posts
        context["recent_posts"] = NewsPost.objects.filter(is_active=True).order_by(
            "-created_at"
        )[:6]
        return context


class NewsDetailView(DetailView):
    model = NewsPost
    template_name = "news_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return NewsPost.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recommended_posts"] = NewsPost.objects.filter(
            is_active=True
        ).exclude(pk=self.object.pk).order_by("-created_at")[:3]
        return context


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = "/lien-he/"

    def form_valid(self, form):
        cleaned = form.cleaned_data
        to_email = getattr(settings, "CONTACT_EMAIL", None) or getattr(
            settings, "DEFAULT_FROM_EMAIL", None
        )
        if not to_email:
            to_email = "nguyenthikimngoc1402@gmail.com"

        subject = f"[Lien he] {cleaned['subject']}"
        context = {
            "name": cleaned["name"],
            "email": cleaned["email"],
            "phone": cleaned["phone"] or "Khong co",
            "subject": cleaned["subject"],
            "message": cleaned["message"],
            "submitted_at": timezone.now(),
        }
        html_body = render_to_string("emails/contact_email.html", context)
        text_body = render_to_string("emails/contact_email.txt", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=to_email,
            to=[to_email],
            reply_to=[cleaned["email"]],
        )
        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=True)

        messages.success(self.request, "Đã gửi liên hệ thành công. Chúng tôi sẽ phản hồi sớm.")
        return super().form_valid(form)

_COORD_PATTERNS = (
    re.compile(r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)"),
    re.compile(r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)"),
    re.compile(r"[?&]q=(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)"),
    re.compile(r"[?&]query=(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)"),
)


def _extract_coords(map_url: str):
    if not map_url:
        return None
    for pattern in _COORD_PATTERNS:
        match = pattern.search(map_url)
        if match:
            return float(match.group(1)), float(match.group(2))
    return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@require_GET
def nearest_store(request):
    try:
        lat = float(request.GET.get("lat"))
        lng = float(request.GET.get("lng"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "invalid_location"}, status=400)

    stores = Store.objects.filter(is_active=True).exclude(map_url="").only(
        "name",
        "address",
        "city",
        "map_url",
    )
    nearest = None
    nearest_distance = None

    for store in stores:
        coords = _extract_coords(store.map_url)
        if not coords:
            continue
        distance = _haversine_km(lat, lng, coords[0], coords[1])
        if nearest is None or distance < nearest_distance:
            nearest = store
            nearest_distance = distance

    if not nearest:
        return JsonResponse({"error": "no_store_coordinates"}, status=404)

    return JsonResponse(
        {
            "name": nearest.name,
            "address": nearest.address,
            "city": nearest.city,
            "map_url": nearest.map_url,
            "distance_km": round(nearest_distance, 2),
        }
    )

