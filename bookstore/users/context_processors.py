from .models import WishlistItem


def wishlist_processor(request):
    if request.user.is_authenticated:
        ids = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        return {'wishlist_ids': set(ids)}
    return {'wishlist_ids': set()}
