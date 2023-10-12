import json

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from .models import Location, Job, RelatedOrgs
from rest_framework import filters, status
from .serializers import LocationSerializer, JobSerializer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, parser_classes
from django.http import HttpResponseBadRequest
from django.db.models import Q, Max, Min
from functools import reduce
import operator
from .utils import process_location, get_keywords_to_search_for
from datetime import datetime
from wordhoard import Synonyms
from collections import defaultdict


# @api_view(['GET'])
# def get_jobs(request, format=None):
#     print(f"request is: {request}")
#     location = Location.objects.get(id=2182)
#
#     jobs = Job.objects.filter(location=location)
#     searializer = JobSerializer(jobs, many=True)
#     return JsonResponse(searializer.data, safe=False)


# class CustomJobSearch(filters.SearchFilter):
#     # serializer_class = JobSerializer
#     # queryset = Job.objects.all()
#     # filter_backends = (SearchFilter, OrderingFilter)
#     # search_fields = ('location__city')
#
#     def get_search_fields(self, view, request):
#         location = request.query_params.get('location')
#         print(f"Location is: {location}")
#
#
# class SearchJobs(ListAPIView):
#     serializer_class = JobSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["category", "name"]

# user authentication not considered for the project.
class CustomJobFilterApiView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Job.objects.all()

        parameters = {}
        for search_param in self.request.query_params:
            parameters[search_param.lower()] = self.request.query_params[search_param]

        print(parameters)

        # comma seperated city & state (e.g. Phoenix, Arizona)
        # location is a required parameter.
        if 'location' not in parameters:
            error_message = {'error': 'location is required'}
            return JsonResponse(error_message, status=status.HTTP_400_BAD_REQUEST)

        comma_count = parameters['location'].count(',')

        if comma_count != 1:
            error_message = {'error': 'invalid number of commas, please enter city, state'}
            return JsonResponse(error_message, status=status.HTTP_400_BAD_REQUEST)

        city, state = process_location(parameters['location'])

        try:
            loc_obj = Location.objects.get(city=city, state=state)
        except Location.DoesNotExist:
            error_message = {'error': 'city & state combo doesn\'t exist'}
            return JsonResponse(error_message, status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(location_id=loc_obj.id)

        # keywords are optional
        keywords = parameters.get('keywords', None)

        if keywords:
            keywords = get_keywords_to_search_for(keywords)
            print(f"Output keywords are: {keywords}")
            filtering_cond = reduce(operator.or_, (Q(title__icontains=keyword) for keyword in keywords))
            queryset = queryset.filter(filtering_cond)

        # no expired job posting are shown, timezones ignored.
        queryset = queryset.filter(Q(close_date__gte=datetime.now()))

        # instead of sorting which is n log n, use min & max which should be n.
        # make sense to compare by posted date first & title second.
        newest = queryset.aggregate(Max("posted_date"), Max("title"))
        oldest = queryset.aggregate(Min("posted_date"), Min("title"))

        # output = list(queryset.values())

        data = {
            "number of jobs": queryset.count(),
            "oldest job": {
                "role": oldest['title__min'],
                "posted_date": oldest['posted_date__min']
            },
            "newest job": {
                "role": newest['title__max'],
                "posted_date": newest['posted_date__max']
            },
            # "output": output
        }
        return JsonResponse(data)


class CustomOrganizationsApiView(APIView):
    def get(self, request, *args, **kwargs):
        # queryset = Job.objects.all()

        parameters = {}
        for search_param in self.request.query_params:
            parameters[search_param.lower()] = self.request.query_params[search_param]

        city = parameters.get("city", None)
        state = parameters.get("state", None)

        # city is a required parameter.
        if not city or not state:
            error_message = {'error': 'Both city & state are required'}
            return JsonResponse(error_message, status=status.HTTP_400_BAD_REQUEST)

        try:
            loc_obj = Location.objects.get(city=city, state=state)
        except Location.DoesNotExist:
            error_message = {'error': 'city & state combo doesn\'t exist'}
            return JsonResponse(error_message, status=status.HTTP_400_BAD_REQUEST)

        queryset = Job.objects.filter(location_id=loc_obj)

        job_ids = list(queryset.values_list('id', flat=True))
        related_orgs = RelatedOrgs.objects.filter(job_id__in=job_ids)
        # same organization might be referred in many jobs
        related_orgs_queryset = related_orgs.values_list('code_id', flat=True).distinct()

        org_titles = list(queryset.values_list('org_name', 'title'))

        # represent the data as dictionary with org name as a key & jobs as values
        org_title_dict = defaultdict(list)
        [org_title_dict[org_title[0]].append(org_title[1]) for org_title in org_titles]

        data = {
            "number of jobs in that city": queryset.count(),
            "number of different organizations represented in those jobs": related_orgs_queryset.count(),
            # list of organizations along with jobs listed below
            "list of organizations with jobs there": org_title_dict
        }
        return JsonResponse(data)
