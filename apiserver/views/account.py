import django.contrib.auth as dauth
import nap
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apiserver.models import User, Couple
from apiserver.permissions import IsAuthenticated, IsNotAuthenticated
from apiserver.serializers import UserSerializer, UserSerializerPublic, CoupleSerializer


@api_view(['GET', 'POST'])
def login(request):
    # ignore already logged user
    if request.user and request.user.is_authenticated():
        return Response(UserSerializerPublic(request.user).data)

    # gathering credential
    if request.method == 'GET':
        username, password = request.query_params.get('username', None), request.query_params.get('password', None)
    else:
        username, password = request.data.get('username'), request.data.get('password')

    # authenticate (find user and compare credential)
    user = dauth.authenticate(username=username, password=password)
    if user is None:  # Not exists
        return Response('user not exists or incorrect password', status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(user, AnonymousUser):  # bad credentials
        return Response('bad credentials were given', status=status.HTTP_400_BAD_REQUEST)

    # login (create session)
    dauth.login(request, user)
    data = UserSerializerPublic(user).data
    return Response(data)


@api_view(['GET'])
def login_facebook(request):
    """
    login via facebook (gist at https://gist.github.com/makerj/24f34189125565a5575b)

    PREREQUISITES: getting 'code' at frontend using oauth uri like this:
        https://www.facebook.com/dialog/oauth?
        client_id=563193193877116&
        response_type=code&
        scope=user_friends,public_profile,email&
        redirect_uri=http://api.phople.us/login_facebook

    :param request: request
    :return: public user information
    """
    f = settings.CREDENTIAL['Facebook']
    appid, appsecret = f['APP_ID'], f['APP_SECRET']
    app_access_token = '{}|{}'.format(appid, appsecret)
    # error case
    if request.query_params.get('error') or not request.query_params.get('code'):
        return Response('login rejected by user', status=status.HTTP_403_FORBIDDEN)

    # step1: retrieving 'access token'
    code = request.query_params.get('code')
    uri = 'https://graph.facebook.com/v2.3/oauth/access_token?' \
          'client_id={appid}&redirect_uri={uri}&client_secret={appsecret}&code={code}'
    uri = uri.format(appid=appid, uri='http://api.phople.us/login_facebook', appsecret=appsecret, code=code)
    access_token_response = nap.url.Url(uri).get().json()
    access_token = access_token_response.get('access_token')

    # step2: retrieving user information by using access token
    # 2.1 inspect access token. expected response:
    inspected = nap.url.Url('https://graph.facebook.com/debug_token').get(
        params={'input_token': access_token, 'access_token': app_access_token}).json().get('data')
    is_valid, user_id = inspected.get('is_valid', False), inspected.get('user_id', -1)
    if not is_valid:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # 2.2 retrieving user information
    uri = 'https://graph.facebook.com/{uid}?' \
          'fields=id,name,first_name,last_name,age_range,link,gender,locale,picture,updated_time,verified,email&' \
          'access_token={access_token}'
    uri = uri.format(uid=user_id, access_token=access_token)
    fbuser = nap.url.Url(uri).get().json()
    info = {
        'user': fbuser,
        'access_token': access_token_response,
    }

    user = _oauth_login(request, username=fbuser['user_id'], password=None)
    data = UserSerializerPublic(user).data
    return Response(data)


def _oauth_login(request, **kwargs):
    """
    authenticate + login for oauth user
    if user is None then creates user using given user information
    :param request: request
    :param kwargs: user information
    :return: User object
    """
    user = dauth.authenticate(username=kwargs.get('username'), password=kwargs.get('password'))
    if user is None:
        # automatic signup for social user
        user = User.objects.create_user(kwargs.pop('username'), kwargs.pop('password'))
        for k, v in kwargs.items():
            setattr(user, k, v)
        user.save()
    dauth.login(request, user)
    return user


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def me(request):
    # return user information for logged user
    if request.method == 'GET':
        return Response(UserSerializerPublic(request.user).data)
    # update user information
    elif request.method == 'POST':
        seri = UserSerializer(request.user, request.data, partial=True)
        if seri.is_valid():
            seri.save()
        return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def logout(request):
    # logout (clear session)
    dauth.logout(request)
    return Response()


@api_view(['GET'])
def user_exists(request, username):
    if User.objects.filter(username=username).exists():
        return Response(status=status.HTTP_306_RESERVED)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsNotAuthenticated,))
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        newuser = serializer.save()
        returninfo = UserSerializerPublic(newuser)
        return Response(returninfo.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def signdown(request):  # equivalent to withdrawal(request):
    request.user.delete()
    dauth.logout(request)
    return Response(status.HTTP_200_OK)


class CoupleViewSet(viewsets.ModelViewSet):
    queryset = Couple.objects.all()
    serializer_class = CoupleSerializer
    filter_fields = ('title',)
    ordering_fields = ('title',)  # http://example.com/api/users?ordering=account,-username
    permission_classes = (IsAuthenticated,)

    # def list(self, request): GET /couple
    #     pass
    #
    # def create(self, request): POST /couple
    #     pass
    #
    # def retrieve(self, request, pk=None): GET /couple/1
    #     pass
    #
    # def update(self, request, pk=None): PUT /couple/1
    #     pass
    #
    # def partial_update(self, request, pk=None): PATCH /couple/1
    #     pass
    #
    # def destroy(self, request, *args, **kwargs):  # DELETE /couple/1
    #     pass
