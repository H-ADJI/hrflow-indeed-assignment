# Hrflow assignment
<!-- ADD GITHUB URL -->
Made by HADJI KHALIL (aka H-ADJI)

## Objectif

Scripts to collect data from indeed job board, the collected jobs will be indexed in hrflow internal databases using python + hrflow APIs.


## setup

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
The following fields are available but where not considered :
- work model : remote / in-person / hybrid

### The job page 
The following fields will be extracted from a job page :
- description
- job location
- company_name
- title
- date posted
- valid until
- job_type / employement_type (full list)
- salary (detailed infos)



### some job links to verify the fields 
- https://uk.indeed.com/viewjob?jk=16f799d068784637&tk=1h32l3o0kjtuo801&from=serp&vjs=3 
- https://uk.indeed.com/viewjob?jk=3db748ddcf374946&tk=1h32l3o0kjtuo801&from=serp&vjs=3