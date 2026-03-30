from django.contrib.auth.models import User
from rest_framework import serializers
from posts.models import Post
from django.utils import timezone

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # remove before creating user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  # create_user hashes this
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    member_since_days = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'date_joined', 'full_name', 'member_since_days']
        read_only_fields = ['username', 'email', 'date_joined']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_member_since_days(self, obj):
        delta = timezone.now() - obj.date_joined
        return delta.days


class PostSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    author_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_id', 'created_at']

    def validate(self, data):
        author = data.get('author_id')
        title = data.get('title')
        if Post.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                {"title": "You already have a post with this title."}
            )
        return data

    def create(self, validated_data):
        author = validated_data.pop('author_id')
        return Post.objects.create(author=author, **validated_data)