from rest_framework import viewsets

from apiserver.models import DatePost
from apiserver.permissions import IsAuthenticated, IsOwnerCoupleOrReadOnly
from apiserver.serializers import DatePostSerializer


def injectcoupleid(f):
    def wrapper(*args, **kwargs):
        request = args[1]

        mutable = getattr(request.data, '_mutable')  # mutable hack for django test client method ['PUT', 'PATCH']
        if not mutable:  # turn on
            setattr(request.data, '_mutable', True)

        request.data.update({'couple': request.user.couple_id})

        if not mutable:  # turn off
            setattr(request.data, '_mutable', False)

        return f(*args, **kwargs)

    return wrapper


class DatePostViewSet(viewsets.ModelViewSet):
    queryset = DatePost.objects.all()
    serializer_class = DatePostSerializer
    filter_fields = ('title', 'tags')
    ordering_fields = ('title', 'created')
    permission_classes = (IsAuthenticated, IsOwnerCoupleOrReadOnly)

    @injectcoupleid
    def create(self, *args, **kwargs):
        return super(DatePostViewSet, self).create(*args, **kwargs)

    @injectcoupleid
    def update(self, request, *args, **kwargs):
        return super(DatePostViewSet, self).update(request, *args, **kwargs)

    @injectcoupleid
    def partial_update(self, request, *args, **kwargs):
        return super(DatePostViewSet, self).partial_update(request, *args, **kwargs)
