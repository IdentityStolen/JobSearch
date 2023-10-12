import time
from django.core.management.base import BaseCommand
import requests
from typing import List
from dateutil import parser
from usa_jobs.models import Location, Job, Organization, RelatedOrgs
from usa_jobs.utils import process_location
import os

HEADERS = {
    "Host": os.getenv('HOST'),
    "User-Agent": os.getenv('USER_AGENT'),
    "Authorization-Key": os.getenv('AUTHORIZATION_KEY')
}

SEPERATOR = ','


def calc_time(func):
    """
    decorator function to display how much time any function takes
    :param func: function
    :return: nothing
    """
    def inner(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        end = time.time()
        print(f"Function {func.__name__} took {end - start} second/s")
        return ret
    return inner


class Scraper:
    def __init__(self, location, keyword=None, url="https://data.usajobs.gov/api/search?"):
        self.location = location
        self.keyword = keyword
        self.url = [url]

    @calc_time
    def update_codes_and_organizations(self):
        """
        Update Organization model by scraping. This model helps to get related organizations for given job.
        From USAJOBS upstream website, only jobs represented under UserArea.Details.OrganizationCodes are
        considered relevant, others seem irrelevant.
        :return: nothing
        """
        try:
            url = "https://data.usajobs.gov/api/codelist/agencysubelements"

            r = requests.get(url)

            if r.status_code == 200:
                response = r.json()
                for codes in response['CodeList']:
                    for valid_val in codes['ValidValue']:
                        # ParentCode not considered for related organizations for reducing project's scope
                        if valid_val['IsDisabled'].lower() == 'no':
                            # bring in org if not disabled,
                            # org disabled after brought in our db is not considered for removal for reducing
                            # project scope.
                            code = valid_val['Code'].strip()
                            org = valid_val['Value'].strip()
                            print(f"Code={code}: Org: {org}")

                            org_obj, _ = Organization.objects.get_or_create(code=code, org_name=org)
        except Exception as e:
            print(f"Error occurred while scraping for Organizations: {e}")
            raise e

    @calc_time
    def get_data(self):
        """
        Update Location, Job & RelatedOrgs models by scraping
        :return: nothing
        """
        # update organizations & corresponding codes first, this is required for fetching related organizations
        self.update_codes_and_organizations()

        self.url.append(f"LocationName={self.location}")
        if self.keyword:
            self.url.append(f"Keyword={self.keyword}")

        url_to_scrape = ''.join(self.url)
        try:
            response = requests.get(url_to_scrape, headers=HEADERS)

            if response.status_code == 200:
                ret_data = response.json()

                locs_imported, jobs_imported = 0, 0
                for result in ret_data['SearchResult']['SearchResultItems']:
                    d = result['MatchedObjectDescriptor']
                    title = d["PositionTitle"]
                    org_name = d["OrganizationName"]
                    # assumption: upstream data is harmonized with respect to date formats.
                    posted_date = parser.parse(d["PublicationStartDate"])
                    close_date = parser.parse(d["ApplicationCloseDate"])
                    # related_org = d['UserArea']["Details"].get("SubAgencyName", None)
                    org_codes_str = d['UserArea']["Details"].get("OrganizationCodes", None)
                    # assumption: upstream, they are always split by '/' seperator, harmonized
                    org_codes_ = org_codes_str.split('/')
                    org_codes = list(map(str.strip, org_codes_))

                    locs_counts, jobs_counts = 0, 0
                    for location in d['PositionLocation']:
                        place: str = location["LocationName"]
                        city, state = process_location(place, SEPERATOR)
                        print(f"title={title}: org={org_name}: location={place}: city={city}: state={state}: "
                              f"posted_date= {posted_date}: close_date={close_date}: org_codes={org_codes}")

                        loc_obj, created = Location.objects.get_or_create(
                            city=city,
                            state=state
                        )

                        if created:
                            locs_counts += 1

                        job_obj, created = Job.objects.get_or_create(
                            location=loc_obj,
                            title=title,
                            org_name=org_name,
                            posted_date=posted_date,
                            close_date=close_date
                        )

                        if created:
                            jobs_counts += 1

                        for org_code in org_codes:
                            organization_obj = Organization.objects.get(code=org_code)
                            _, _ = RelatedOrgs.objects.get_or_create(job=job_obj, code=organization_obj)

                    locs_imported += locs_counts
                    jobs_imported += jobs_counts
                # future scope: store metrics later in the database.
                print(f"Number of locations ingested: {locs_imported}, number of jobs ingested: {jobs_imported}")
            else:
                print(f"For location = {self.location} and keyword = {self.keyword} ,error occurred scraping data, "
                      f"status code = {response.status_code}, no locations/jobs ingested.")
        except Exception as e:
            print(f"Scraping went wrong: {e}")


class Command(BaseCommand):
    help = "Scrape usajobs endpoint for specified location & keywords"

    def add_arguments(self, parser):
        parser.add_argument(
            '--location',
            action='store',
            required=True,
            help="Comma seperated city & state")
        parser.add_argument(
            '--keywords',
            action='store',
            help="Comma seperated list of keywords")

    def handle(self, *args, **options):
        location = options.get("location", None)

        if not (location or ',' in location):
            print(f"Formatting error in inputed location: {location}")

        keywords = options.get("keywords", None)

        kws = keywords.split(',') if keywords else None

        agent = None
        if kws:
            # upstream service runs on single keyword
            for keyword in kws:
                agent = Scraper(location, keyword)
                agent.get_data()
        else:
            agent = Scraper(location)
            agent.get_data()
