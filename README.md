This repository explains one of the backend interview projects for datapeople.io, and was created specifically for Shreeniwas Kulkarni. 

## Overview

In this project you will be pulling data from an external api into a local cache, you will then use that cache to serve your own api. The code and instructions you provide should allow for us to run the entire system (both the ingestion and the API) using docker compose. 

## Guidelines for this project

In order to best simulate a real world experience, we have designed a problem that you may not be able to
solve without asking questions, making assumptions, and working around problems. We want to understand how you
will work with others on your team as well as how you solve problems, throughout the process you should feel free to 
ask any questions about the goal or process that you wish.

## Step 1: Data ingestion

The data for our API will come a third party api, keys are free.

We will be getting job data from 

Usajobs.gov: https://developer.usajobs.gov/Tutorials/Search-Jobs (there is a link to apply for an API key in that page)


Import all jobs available in the usajobs.gov search api into a local database. Your import process should be able to be rerun every certain amount of time in order to get updated data. At the end of the ingestion process your local db should have all the information needed to run the apis specified below without having to further query the apis. 

The ingestion process should provide metrics on the process (number of jobs ingested, number of different locations ingested, time for each step)

## Step 2 Api creation

Create a REST API service with the following interface:

Endpoint 1 (jobs):
- inputs:
  - location
  - list of keywords (optional, matched from the keywords from position title, not the general text)
- outputs
  - number of jobs
  - oldest job (role and posted date)
  - newest job (role and posted date)

Endpoint 2 (organizations):
- inputs:
  - city
  - state
- outputs:
  - number of jobs in that city 
  - number of different organizations represented in those jobs
  - list of organizations with jobs there

## Some tips:
- Choose a strategy for keyword matching and be explicit with it.
- Make sure your indices and data structure are tailored to the api, be ready to talk about expansibility and scalability of your solution

## Deployment

- There are two options for deployment:
  - Docker (Default): Develop in your own local machine and have us test it in ours. Assume that we will be starting with nothing but the repo and docker + docker-compose on a bare linux machine. How you choose to deploy is entirely up to you but your entire project (ingestion, api serving and database hosting must be containerized)
  - Terraform (AWS): Should you wish to host your project on AWS instead, we will pay up to $25 in compute costs, please submit your terraform files and instructions so we can replicate and test your system

- Document all deployment instructions. 

# Logistics
- Use this repository to check in your code along with deployment instructions. If this has dependencies, provide instructions on how to install those dependencies so we can deploy and test your code
- Once you have read these instructions, set up a 30 min call with Ron (details in the email you received) to go over any questions you have. After that, start the assignment and set up a time once you are done to go over your code. 
- This exercise should take about ~5-10 hours of your time, plus time to actually run the code to load the data during testing and deployment.
- We will pay candidates $250 to complete this project regardless of whether you get offered a position at Datapeople. However, in order for you to receive this payment, we require the project to be completed (i.e. code checked in and tested as working).
- When in doubt, ask. If you need guidance on anything just ask Pablo or Haley, and we'll set up a time to talk with either Pablo or one of the other engineering staff.
- We are rooting for you to succeed!
