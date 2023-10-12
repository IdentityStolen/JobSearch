from rest_framework import serializers
from .models import Location, Job


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['city', 'state']


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'org_name', 'posted_date', 'close_date']

