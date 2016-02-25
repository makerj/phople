from rest_framework import serializers

from .models import User, Couple, DatePost, DatePostComment, DatePostMedia

EMPTY = []


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

    def create(self, validated_data):
        v = validated_data.get
        return User.objects.create_user(username=v('username'), password=v('password'))


class UserSerializerPublic(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'name', 'email', "profile_image", "profile_background_image",
                  'gender', 'age', 'couple')


class CoupleSerializer(serializers.ModelSerializer):
    users = UserSerializerPublic(many=True, required=False, read_only=True)

    class Meta:
        model = Couple


class DatePostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatePostComment


class DatePostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatePostMedia


class DatePostSerializer(serializers.ModelSerializer):
    datepostcomments = DatePostCommentSerializer(many=True)
    datepostmedias = DatePostMediaSerializer(many=True)

    class Meta:
        model = DatePost

    def create(self, validated_data):
        datepostmedias_data = validated_data.pop('datepostmedias', EMPTY)
        datepostcomments_data = validated_data.pop('datepostcomments', EMPTY)
        datepost = DatePost.objects.create(**validated_data)

        for datepostmedia_data in datepostmedias_data:
            DatePostMedia.objects.create(datepost=datepost, **datepostmedia_data)
        for datepostcomment_data in datepostcomments_data:
            DatePostComment.objects.create(datepost=datepost, **datepostcomment_data)

        return datepost

    def update(self, instance, validated_data):
        datepostmedias_data = validated_data.pop('datepostmedias', EMPTY)
        datepostcomments_data = validated_data.pop('datepostcomments', EMPTY)

        for datepostmedia_data in datepostmedias_data:
            DatePostMedia.objects.filter(id=datepostmedia_data.pop(id)).update(datepostmedia_data)
        for datepostcomment_data in datepostcomments_data:
            DatePostComment.objects.filter(id=datepostcomment_data.pop(id)).update(**datepostcomment_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
