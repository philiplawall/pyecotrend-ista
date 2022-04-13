import aiohttp
import json

from lxml import html
from random import randint

from .const import LOGIN_HEADER, LOGIN_URL


class PyEcotrendIsta:
    def __init__(self, email: str, password: str) -> None:
        self._accessToken = None
        self._header = None
        self._supportCode = None
        self._uuid = None

        self._email = email
        self._password = password

    async def login(self):
        payload = {
            "email": self._email,
            "password": self._password,
            "fromMobileApp": "true"
        }
        LOGIN_HEADER['User-Agent'] = await self.getUA()
        async with aiohttp.ClientSession() as session:
            async with session.post(LOGIN_URL, headers=LOGIN_HEADER, data=json.dumps(payload)) as response:
                try:
                    if response.status != 200:
                        raise Exception("Login fail, check your input!")
                    json_str_resp = await response.json()
                    self._accessToken = json_str_resp['accessToken']
                    await self.__setAccount()
                except Exception as err:
                    raise Exception(err)
                finally:
                    await session.close()

    async def __setAccount(self):
        self._header = LOGIN_HEADER
        self._header.pop("Accept-Encoding")
        self._header.pop("Content-Type")
        self._header['User-Agent'] = await self.getUA()
        self._header["Authorization"] = "Bearer {}".format(self._accessToken)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.prod.eed.ista.com/account", headers=self._header) as response:
                res = await response.json()
                await session.close()
                self._a_ads = res['ads']
                self._a_authcode = res['authcode']
                self._a_betaPhase = res['betaPhase']
                self._a_consumptionUnitUuids = res['consumptionUnitUuids']
                self._a_country = res['country']
                self._a_email = res['email']
                self._a_emailConfirmed = res['emailConfirmed']
                self._a_enabled = res['enabled']
                self._a_fcmToken = res['fcmToken']
                self._a_firstName = res['firstName']
                self._a_isDemo = res['isDemo']
                self._a_keycloakId = res['keycloakId']
                self._a_lastName = res['lastName']
                self._a_locale = res['locale']
                self._a_marketing = res['marketing']
                self._a_mobileLoginStatus = res['mobileLoginStatus']
                self._a_notificationMethod = res['notificationMethod']
                self._a_notificationMethodEmailConfirmed = res['notificationMethodEmailConfirmed']
                self._a_password = res['password']
                self._a_privacy = res['privacy']
                self._a_residentAndConsumptionUuidsMap = res['residentAndConsumptionUuidsMap']
                self._a_residentTimeRangeUuids = res['residentTimeRangeUuids']
                self._supportCode = res['supportCode']
                self._a_tos = res['tos']
                self._a_tosUpdated = res['tosUpdated']
                self._a_transitionMobileNumber = res['transitionMobileNumber']
                self._a_unconfirmedPhoneNumber = res['unconfirmedPhoneNumber']
                self._a_userGroup = res['userGroup']
                self._uuid = res['activeConsumptionUnit']

    async def consum_raw(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.prod.eed.ista.com/consumptions?consumptionUnitUuid={}".format(self._uuid), headers=self._header
            ) as response:
                await session.close()
                return await response.json()

    def getSupportCode(self):
        return self._supportCode

    async def consum_small(self):
        consum_raw = await self.consum_raw()
        consum_now: list = []
        for consumption in consum_raw['consumptions']:
            consum_now.append({"date": consumption['date']})
            for reading in consumption["readings"]:
                if reading['type']:
                    consum_now.append({
                        'type': reading['type'],
                        'value': reading['value'],
                        'valuekwh': reading['additionalValue'],
                        'unit': reading['unit'],
                        'unitkwh': reading['additionalUnit'],
                    })
        return consum_now

    async def getUA(self):
        url = (
            "https://webcache.googleusercontent.com/"
            "search?q=cache:FxxmQW9XrRcJ:https://techblog.willshouse.com/"
            "2012/01/03/most-common-user-agents/+&cd=4&hl=de&ct=clnk&gl=us"
        )
        xpath = '//*[@id="post-2229"]/div[2]/textarea[2]'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                xml = html.fromstring(await response.text())
                elem = xml.xpath(xpath)[0]
                data = json.loads(elem.text)
                i = randint(0, len(data) - 1)
                return data[i]['useragent']

#    async def consum(self):
#        consum_raw = await self.consum_raw()
#        for consumption in consum_raw['consumptions']:
#            for reading in consumption["readings"]:
#                if reading['type']:
#                    print(reading['type'])
#                    print(reading['value'])
#                    print(reading['unit'])
#                    print('zusätzlicher Wert', reading['additionalValue'])
#                    print('zusätzliche Einheit', reading['additionalUnit'])
#                    print('geschätzt', reading['estimated'])
#                    print('Verbrauch verglichen', reading['comparedConsumption'])
#                    print('Kosten verglichen', reading['comparedCost'])
#                    if isinstance(reading['averageConsumption'], dict):
#                        print('durchschnittlicher Verbrauchswert', reading['averageConsumption']['averageConsumptionValue'])
#                        print('Verbrauchswert der Wohnung', reading['averageConsumption']['residentConsumptionValue'])
#                        print('durchschnittlicher Verbrauchsanteil', reading['averageConsumption']['averageConsumptionPercentage'])
#                        print('Prozentsatz des Einwohnerverbrauchs', reading['averageConsumption']['residentConsumptionPercentage'])
#                        print('zusätzlicher durchschnittlicher Verbrauchswert', reading['averageConsumption']['additionalAverageConsumptionValue'])
#                        print('zusätzlicher Verbrauchswert der Einwohner', reading['averageConsumption']['additionalResidentConsumptionValue'])
#                        print('zusätzlicher durchschnittlicher Verbrauchsprozentsatz', reading['averageConsumption']['additionalAverageConsumptionPercentage'])
#                        print('zusätzlicher Prozentsatz des Einwohnerverbrauchs', reading['averageConsumption']['additionalResidentConsumptionPercentage'])
#                    else:
#                        print('durchschnittlicher Verbrauch', reading['averageConsumption'])
