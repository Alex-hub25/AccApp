from django.apps import AppConfig


class AccountsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts_app'
    verbose_name = 'Accounts'

    def ready(self):
        import accounts_app.models  # noqa: F401 — registers signals
