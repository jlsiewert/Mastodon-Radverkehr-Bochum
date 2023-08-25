import requests
import datetime
from urllib.parse import urljoin
import regex as re
from typing import List, Generator
from dataclasses import dataclass
import pandas as pd

class RadverkehrAPI:
    @dataclass
    class Result:
        df: pd.DataFrame

        def __init__(self, csv_url: str):
            self.df = pd.read_csv(csv_url, index_col=0)
            self.df.index = pd.to_datetime(self.df.index)

        def get_day(self, date: datetime.datetime):
            datestring = date.strftime("%Y-%m-%d")
            return self.df.loc[datestring]

    @dataclass
    class HourlyResult:
        """
        Hourly results of data provided by the API
        """
        id: str
        name: str
        data: "Result"

    def __init__(self, url: str = "https://opendata.ruhr/api/3/", id: str = "verkehrszahlung-fahrradverkehr"):
        self.url = url
        self.id = id

    def get_resources(self, date: datetime.datetime = None) -> List[str]:
        """
        Get the ids of all resources for the day before the given day
        """
        date = date if date else datetime.datetime.now()

        # get all resources from api
        resources_url = urljoin(self.url, "action/package_show")
        res = requests.get(resources_url, params={"id": self.id})

        if res.ok:
            result = res.json()
            # get all hourly resource id where the name matches the format "{year} (*) - stündlich"
            regex = date.strftime("%Y .+ - stündlich")
            return [r["id"] for r in result["result"]["resources"] if re.match(regex, r["name"])]
        else:
            print("Could not get resources")

    def get_resource(self, id: str) -> HourlyResult:
        resouce_url = urljoin(self.url, "action/resource_show")
        res = requests.get(resouce_url, params={"id": id})
        if res.ok:
            json = res.json()["result"]
            csv = json["url"]
            data = RadverkehrAPI.Result(csv)

            return RadverkehrAPI.HourlyResult(json["id"],json["name"],data);
        else:
            raise Exception("Could not read result data")

    def get_all_data_for_date(self, date: datetime.datetime) -> Generator[HourlyResult, None, None]:
        resources = api.get_resources(date=date)
        for res in resources:
            r = self.get_resource(res)
            yield r



if __name__ == "__main__":
    api = RadverkehrAPI()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    for r in api.get_all_data_for_date(yesterday):
        print(r.name)
        print(r.data.get_day(yesterday))