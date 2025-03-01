from django.apps import AppConfig

class WebAppConfig(AppConfig):  # Replace 'WebAppConfig' with your app's actual config name
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webapp'  # Replace 'webapp' with your actual app name

    def ready(self):
        import webapp.models  # Ensure this imports your signals
