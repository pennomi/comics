from django.http import HttpResponseRedirect

from apps.comics.models import Comic, AliasUrl


class ComicUrlMiddleware:
    """
    Add a new attribute to the request object that represents the comic object, as calculated by the requesting URL.

    Also redirect any alias URLs (eg. www) to the canonical URL, for SEO reasons.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META['HTTP_HOST'].split(':')[0]

        # First check if the request is coming from an alias URL, if so, redirect it to the canonical one.
        try:
            alias = AliasUrl.objects.get(domain=host)
            new_url = f"{request.scheme}://{alias.comic.domain}{request.path}"
            if request.META['QUERY_STRING']:
                new_url += f"?{request.META['QUERY_STRING']}"
            return HttpResponseRedirect(new_url)
        except AliasUrl.DoesNotExist:
            pass

        # Calculate the requested comic from the url
        try:
            request.comic = Comic.objects.get(domain=host)
        except Comic.DoesNotExist:
            request.comic = None

        response = self.get_response(request)
        return response
