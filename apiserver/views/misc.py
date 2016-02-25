from rest_framework.decorators import api_view, parser_classes, renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


@api_view(['GET', 'POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def requestinfo(request):
    import re
    info = {
        'method': request._request.method,
        'body': str(request._request.body),
        'META': re.sub(
            r'(apache|python|django|boto|/home/\w+/gitrepo/phople|mod_wsgi|wsgi)', '-', str(request.META), flags=re.I),
        'FILES': request.FILES,
        'POST': request.POST,
        'user': str(request.user),
        'query_params': request.query_params,
        'data': request.data
    }
    return Response(data=info)
