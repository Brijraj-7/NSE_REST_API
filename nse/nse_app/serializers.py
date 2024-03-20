from rest_framework import serializers
from .models import Index, IndexPrice

class IndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = '__all__'

class IndexPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexPrice
        fields = '__all__'
