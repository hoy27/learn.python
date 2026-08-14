from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Configuration class for the catalog app.

    Django uses this to identify your app. The `name` attribute must
    match the directory name. You can set a human-readable `verbose_name`
    for the admin interface.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
