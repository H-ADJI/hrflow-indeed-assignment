INDEED_BASE_URL = "https://uk.indeed.com"
# Data selection xpaths :
JOB_CARD_SELECTOR = "//div[@class='jobsearch-LeftPane']/div[@id='mosaic-jobResults']/div/ul/li/div[@class[contains( . , 'cardOutline')]]"
JOB_ID_SELECTOR = ".//table//td[@class='resultContent']//a[@id]/@data-jk"
JOB_URL_SELECTOR = ".//table//td[@class='resultContent']//a[@id]/@href"
JOB_TITLE_SELECTOR = ".//table//td[@class='resultContent']//a[@id]/span/@title"
JOB_SALARY_SELECTOR = ".//div[@class='metadata salary-snippet-container']//text()"
COMPANY_NAME_SELECTOR = ".//span[@class='companyName']/text()"
COMPANY_LOCATION_SELECTOR = ".//div[@class='companyLocation']/text()"
COMPANY_RATING_SELECTOR = ".//span[@class='ratingNumber']/span/text()"
JOB_SHIFT_SELECTOR = ".//div[@class='metadata']/div[svg[@aria-label='Shift']]/text()"
JOB_TYPE_SELECTOR = ".//div[@class='metadata']/div[svg[@aria-label='Job type']]/text()"
JOB_DETAIL_JSON_SELECTOR = "//script[@type='application/ld+json']"
JOB_METADATA_JSON_SELECTOR = "//script[contains(text(), 'window._initialData')]"
# Navigation / interactions xpaths :
SEARCH_QUERY_WHERE_SELECTOR = "//input[@id='text-input-where']"
NEXT_PAGE_BUTTON_SELECTOR = "//a[@aria-label='Next Page']"
CURRENT_PAGE_NUMBER_SELECTOR = "//button[@data-testid='pagination-page-current']"
CLOSE_POPUP_SELECTOR = "//button[@aria-label='close']"
JOBS_PANE_SELECTOR = "//div[@class='jobsearch-LeftPane']"


UK_CITIES = [
    "Nottingham",
    "Oxford",
    "Peterborough",
    "Plymouth",
    "Portsmouth",
    "Preston",
    "Ripon",
    "Salford",
    "Salisbury",
    "Sheffield",
    "Southampton",
    "Southend-on-Sea",
    "St Albans",
    "Stoke on Trent",
    "Sunderland",
    "Truro",
    "Wakefield",
    "Wells",
    "Westminster",
    "Winchester",
    "Wolverhampton",
    "Worcester",
    "York",
    "Bangor",
    "Cardiff",
    "Newport",
    "St Asaph",
    "St Davids",
    "Swansea",
    "Wrexham",
    "Aberdeen",
    "Dundee",
    "Dunfermline",
    "Edinburgh",
    "Glasgow",
    "Inverness",
    "Perth",
    "Stirling",
    "Armagh",
    "Bangor",
    "Belfast",
    "Lisburn",
    "Londonderry",
    "Newry",
    "Bath",
    "Birmingha",
    "Bradford",
    "Brighton & Hove",
    "Bristol",
    "Cambridge",
    "Canterbury",
    "Carlisle",
    "Chelmsford",
    "Chester",
    "Chichester",
    "Colchester",
    "Coventry",
    "Derby",
    "Doncaster",
    "Durham",
    "Ely",
    "Exeter",
    "Gloucester",
    "Hereford",
    "Kingston-upon-Hull",
    "Lancaster",
    "Leeds",
    "Leicester",
    "Lichfield",
    "Lincoln",
    "Liverpool",
    "London",
    "Manchester",
    "Milton Keynes",
    "Newcastle-upon-Tyne",
    "Norwich",
]
