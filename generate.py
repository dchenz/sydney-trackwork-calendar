import os
import sys
from datetime import datetime
from typing import NotRequired, TypedDict

import pytz
import requests

ENV_TFNSW_OPENDATA_API_KEY = "TFNSW_OPENDATA_API_KEY"

SYDNEY_TIME = pytz.timezone("Australia/Sydney")

MODE_BUSES = "buses"
MODE_FERRIES = "ferries"
MODE_LIGHT_RAIL = "lightrail"
MODE_METRO = "metro"
MODE_NSW_TRAINS = "nswtrains"
MODE_REGIONAL_BUSES = "regionbuses"
MODE_SYDNEY_TRAINS = "sydneytrains"


class Translation(TypedDict):
    text: str
    language: str


class ActivePeriod(TypedDict):
    start: str
    end: NotRequired[str]


class InformedEntity(TypedDict):
    agencyId: str
    routeId: str
    directionId: int


class TextWithTranslation(TypedDict):
    translation: list[Translation]


class Alert(TypedDict):
    activePeriod: list[ActivePeriod]
    informedEntity: list[InformedEntity]
    cause: str
    effect: str
    headerText: TextWithTranslation
    descriptionText: TextWithTranslation
    url: TextWithTranslation


class AlertEntity(TypedDict):
    id: str
    alert: Alert


class Header(TypedDict):
    gtfsRealtimeVersion: str
    incrementality: str
    timestamp: int


class GetAlertsResponse(TypedDict):
    header: Header
    entity: list[AlertEntity]


ALERTS_API = "https://api.transport.nsw.gov.au/v2/gtfs/alerts"


def fetchAlerts(transportType: str) -> GetAlertsResponse:
    apiKey = os.getenv(ENV_TFNSW_OPENDATA_API_KEY)
    if not apiKey:
        raise Exception(f"{ENV_TFNSW_OPENDATA_API_KEY} is missing")
    try:
        url = f"{ALERTS_API}/{transportType}?format=json"
        response = requests.get(url, headers={"authorization": f"apikey {apiKey}"})
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        print(response.text, file=sys.stderr)
        raise


def getEnglishText(text: TextWithTranslation) -> str | None:
    for translation in text["translation"]:
        if translation["language"] == "en":
            return translation["text"]


def getActivePeriod(alert: Alert) -> tuple[datetime, datetime] | None:
    for period in alert["activePeriod"]:
        start = period["start"]
        end = period.get("end", start)
        activePeriodStart = datetime.fromtimestamp(int(start)).astimezone(SYDNEY_TIME)
        activePeriodEnd = datetime.fromtimestamp(int(end)).astimezone(SYDNEY_TIME)
        return activePeriodStart, activePeriodEnd


def parseAlerts(alertsData: GetAlertsResponse):
    for entity in alertsData["entity"]:
        alert = entity["alert"]

        print(getActivePeriod(alert), getEnglishText(alert["headerText"]))


def main():
    alertsData = fetchAlerts(MODE_SYDNEY_TRAINS)
    parseAlerts(alertsData)


if __name__ == "__main__":
    main()
