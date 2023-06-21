# Hrflow assignment
<!-- ADD GITHUB URL -->
Made by HADJI KHALIL (aka H-ADJI)

## Objectif

Scripts to collect data from indeed job board, the collected jobs will be indexed in hrflow internal databases using python + hrflow APIs.

## setup

- **IMPORTANT** : python >= 3.9 to support all asyncio features
- install packages and dependencies (requirements.txt)
- install a browser for playwright using playwright install chromium

## Scraping flow

- clicking the location for suggestion
- getting the search parameter from home page
- choosing a location
- navigating to the job list
- paginating until no next page
- deal with popup when navigating pages
- extract each page html
- parse html to get the jobs urls
- visit each job page
- extract job data from json in script tag
- merge data from feed with data from job page
- done

## Data fields

### The job feed

The following fields will be extracted from indeed job feed :

- in platform job id
- title
- url
- company name
- company rating
- company_location
- salary (raw format)
- job_type / employement_type
- shift
- work model : remote / in-person / hybrid (computed from location)

### The job page

The following fields will be extracted from a job page :

- in platform job id
- title
- description
- job location
- company_name
- title
- date posted
- valid until
- job_type / employement_type (full list)
- salary (detailed infos)
- job benefits
- company description
- company logo url
- company name
- company indeed profile
- company indeed reviews
- company average rating / same as from feed
- company rating count
