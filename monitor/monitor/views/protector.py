from urlparse import urlparse
import pyramid.httpexceptions as exc

def protect_from_direct_access(request):
    print(request.host_url)
    port = urlparse(request.host_url).port
    print(port)

    if port != 80 and port != 443 and port != 6543 and port is not None:
        raise exc.HTTPForbidden()