
def isURL(request):

    if request.startswith("http://") or request.startswith("https://"):
        return True

