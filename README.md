# Hrflow indeed
<!-- ADD GITHUB URL -->
Made by HADJI KHALIL (aka H-ADJI)

## Objectif

Scripts to collect data from indeed job board, the collected jobs will be indexed in hrflow internal databases using python + hrflow APIs.

## High level architecture

![architecture image](/assets/indeed_crawler.png "architecture")

## Setup

- Add a  **.env**  file in the root of the project with the following variables.

```dosini
API_KEY="YOUR_API_KEY"
USER_EMAIL ="YOUR_EMAIL"
BOARD_KEY="YOUR_BOARD_KEY"
```

### --> Using your local python environment

- **IMPORTANT** : python >= 3.9 to support all asyncio features

- Install packages and dependencies (requirements.txt) using :

```sh
pip install -r requirements.txt
```

- Install a browser for playwright using playwright install chromium (or any other browser you want)

```sh
playwright install chromium
```

- Run the code.

```sh
python main.py
```

### --> Using docker runtime environment

- **IMPORTANT** : docker runtime with the new CLI >= 1.13.
- For Unix based systems (where Makefile is supported) execute the following command.

```sh
make
```

- For windows based systems (you should rethink your career as a programmer) use the docker desktop GUI to build the image and run the container.

## Tools used

- **Playwright** : Browser automation tool made by Microsoft, offering the best performance with a modern API and asyncio support.
- **Playwright-stealth** : Library to patch browser environment variables to imitate a real user browser to avoid fingerprints of automated browsers.
- **Parsel** : HTML parsing backend used by scrapy, uses the Python-C language FFI (Foreign Functions Interfaces) for super fast parsing.
- **ChompJS**  : Library used to parse javascript objects into Python dictionaries, more powerful and flexible than json from std-library.
- **Asyncio** : Coroutine / Event loop based concurrency implementation in python, very good for IO heavy application.
- **Hrflow** : Hrflow SDK to communicate with parsing and indexing APIs.
- **Loguru** : Simple and beautiful logging.

## Deployement

The program what bundled using docker, and the resulting artifact was deployed on a docker optimized VM on GCP.
![deployement](/assets/gcp_vm.png "gcp")

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
