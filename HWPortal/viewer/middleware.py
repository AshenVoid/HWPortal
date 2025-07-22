from django.contrib import messages


class ClearMessagesMiddleware:
    # Čištění zpráv pro nepřihlášené uživatele při přístupu na auth stránky
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path in [
            "/login",
            "/register",
        ]:
            storage = messages.get_messages(request)
            for message in storage:
                pass

        response = self.get_response(request)
        return response
