from django.template.response import TemplateResponse

from app.apps import AppConfig


class InstallationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, *_):
        # application status guard
        if self.guard():
            return TemplateResponse(request, 'site/setup.html').render()
        return None

    def guard(self, detected=False):
        """
        Detect if application is available.

        If the first attempt failed, call update() and detect it again.

        Return True if failed.
        """
        failed = AppConfig.application is None

        if failed and not detected:
            AppConfig.update()
            failed = self.guard(True)

        return failed
