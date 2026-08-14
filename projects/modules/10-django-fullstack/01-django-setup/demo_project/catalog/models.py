from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Item(models.Model):
    """A simple item in our catalog.

    Each attribute becomes a database column:
    - name: a short text field (VARCHAR in SQL), max 200 characters
    - price: a decimal number with up to 8 digits and 2 decimal places
    - in_stock: a boolean (True/False), defaults to True
    - created_at: a datetime that is set automatically when created

    The __str__ method controls how this object appears in the admin
    interface and in print() statements.
    """
    # CharField requires max_length. It maps to VARCHAR(200) in SQL.
    name = models.CharField(max_length=200)

    # DecimalField is precise (unlike FloatField). Use it for money.
    # max_digits=8 means up to 99999999. decimal_places=2 means two decimals.
    price = models.DecimalField(max_digits=8, decimal_places=2)

    # BooleanField stores True or False. default=True means new items
    # are in stock unless you say otherwise.
    in_stock = models.BooleanField(default=True)

    # DateTimeField with auto_now_add=True records the creation timestamp.
    # Django sets this automatically; you never assign it manually.
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        """Return the item name when this object is printed or displayed."""
        return self.name

