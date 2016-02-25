class DisableCSRF(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


class CsrfCookieToHeader(object):
    def process_request(self, request):
        csrftoken = request.COOKIES.get('csrftoken')
        if csrftoken:
            request.META['HTTP_X_CSRFTOKEN'] = csrftoken
