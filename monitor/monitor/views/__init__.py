from urlparse import urlparse

def protect_from_direct_access(request):
    print(request.host_url)
    port = urlparse(request.host_url).port
    print(port)

    if port != 80 and port!=443:
        print("NOOOOOO!!!!")