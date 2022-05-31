from rest_framework import serializers


class LinkedInSerializer(serializers.Serializer):
    query = serializers.CharField(allow_null = True)
    limit = serializers.IntegerField(allow_null = True)