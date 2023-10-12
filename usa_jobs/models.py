from django.db import models


class Location(models.Model):
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    class Meta:
        index_together = [
            ['city', 'state'],
        ]

        unique_together = [
            ['city', 'state']
        ]


class Job(models.Model):
    title = models.CharField(max_length=255)
    org_name = models.CharField(max_length=255)
    posted_date = models.DateTimeField()
    # close_date to track what is active posting & future: clean up job postings that aren't active.
    close_date = models.DateTimeField(null=True)
    # future: date_updated to incrementally sync with elastic search.
    date_updated = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        index_together = [
            ['location', 'title'],
            ['posted_date', 'title']
        ]

        unique_together = [
            ['location', 'title', 'org_name', 'posted_date', 'close_date']
        ]


# future: to display organizations corresponding to organization codes
class Organization(models.Model):
    code = models.CharField(max_length=255, db_index=True)
    org_name = models.CharField(max_length=255)


class RelatedOrgs(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    code = models.ForeignKey(Organization, on_delete=models.CASCADE)
