from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
        ]


class LoggedInUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["id", "username", "email", "first_name", "last_name"]
