from django.contrib import admin
from .models import Item, Category


# Register the Item model with the admin interface.
# After registering, you can manage Items at /admin/catalog/item/.
# Django automatically generates list views, detail forms, and
# search/filter capabilities.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Customize how Items appear in the admin interface."""

    # list_display controls which columns appear in the item list.
    list_display = ["name", "price", "in_stock", "created_at"]

    # list_filter adds filter sidebar options.
    list_filter = ["in_stock"]

    # search_fields enables a search box that searches these fields.
    search_fields = ["name"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ["name"]
    search_fields = ["name"]
