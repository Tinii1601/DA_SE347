from decimal import Decimal
from django.conf import settings
from books.models import Product

class Cart(object):
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            # Use get_final_price if available or price
            price = product.price
            if hasattr(product, 'get_final_price'):
                price = product.get_final_price()
                
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(price),
                'selected': True,
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        
        # Create a map for easy lookup
        product_map = {str(product.id): product for product in products}

        for product_id, item_data in self.cart.items():
            # Create a copy of the item data to yield so we don't modify the session
            item = item_data.copy()
            item['product'] = product_map.get(product_id)
            # Ensure price is present (might be missing if product deleted?)
            if item['product']:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                item['selected'] = item_data.get('selected', True)
                yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_selected_items(self):
        selected_ids = [pid for pid, item in self.cart.items() if item.get('selected', True)]
        if not selected_ids:
            return []
        products = Product.objects.filter(id__in=selected_ids, is_active=True, category__is_active=True)
        product_map = {str(product.id): product for product in products}
        selected_items = []
        for product_id in selected_ids:
            item_data = self.cart.get(product_id)
            product = product_map.get(product_id)
            if not item_data or not product:
                continue
            item = item_data.copy()
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            item['selected'] = item_data.get('selected', True)
            selected_items.append(item)
        return selected_items

    def get_selected_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
            if item.get('selected', True)
        )

    def set_selected(self, selected_ids):
        selected_ids = {str(pid) for pid in selected_ids}
        for product_id in self.cart.keys():
            self.cart[product_id]['selected'] = product_id in selected_ids
        self.save()

    def set_all_selected(self, selected=True):
        for product_id in self.cart.keys():
            self.cart[product_id]['selected'] = selected
        self.save()

    def remove_selected(self):
        to_remove = [pid for pid, item in self.cart.items() if item.get('selected', True)]
        for product_id in to_remove:
            del self.cart[product_id]
        if to_remove:
            self.save()

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()
