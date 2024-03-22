from rest_framework import serializers
from .models import Index, IndexPrice
from django.contrib.auth.models import User

class IndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = '__all__'

class IndexPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexPrice
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    