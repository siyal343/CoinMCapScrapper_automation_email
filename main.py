
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from pydantic import BaseModel
import asyncio






async def load_url(session: AsyncHTMLSession, url: str) -> BeautifulSoup:
    response = await session.get(url)


    await response.html.arender(sleep=3, scrolldown=15, keep_page=True)


    return BeautifulSoup(response.html.html, "html.parser")


def gather_data(soup: BeautifulSoup) -> list:

    class Coin(BaseModel):
        coin_logo: str
        coin_name: str
        coin_ticker: str
        coin_price: str
        change_1hr: str
        change_24hr: str
        change_7d: str
        market_cap: str
        volume_24hr: str
        circ_supply: str

    coins = []

    table = soup.find("table", class_="cmc-table")
    table_rows = table.find_all("tr")

    for row in table_rows[2:]:
        coin_logo = row.find("img", {"class": "coin-logo"})["src"]

        name_tag = row.find("p", {"class": "sc-4984dd93-0 kKpPOn"})
        coin_name = name_tag.text

        ticker_tag = row.find("p", {"class": "coin-item-symbol"})
        coin_ticker = ticker_tag.text

        price_tag = row.find("div", {"class": "sc-a0353bbc-0"})
        coin_price = price_tag.text

        change_tag = row.find_all("span", {"class": "sc-d55c02b-0"})
        change_1hr = change_tag[0].text
        change_24hr = change_tag[1].text
        change_7d = change_tag[2].text

        market_cap_tag = row.find("span", {"class": "sc-7bc56c81-0"})
        market_cap = market_cap_tag.text

        volume_24hr_tag = row.find(
            "p", {"class": "sc-4984dd93-0 jZrMxO font_weight_500"}
        )
        volume_24hr = volume_24hr_tag.text
        circ_supply_tag = row.find("p", {"class": "sc-4984dd93-0 WfVLk"})
        circ_supply = circ_supply_tag.text

        tempCoin = Coin(
            coin_logo=coin_logo,
            coin_name=coin_name,
            coin_ticker=coin_ticker,
            coin_price=coin_price,
            change_1hr=change_1hr,
            change_24hr=change_24hr,
            change_7d=change_7d,
            market_cap=market_cap,
            volume_24hr=volume_24hr,
            circ_supply=circ_supply,
        )

        coins.append(tempCoin)

    return coins

async def main():

    base_url = "https://coinmarketcap.com/"

    pages_to_scrape = 10

    url = base_url + '?page=' + str(pages_to_scrape)

    session = AsyncHTMLSession()

    for i in range(1, pages_to_scrape + 1):
        url = base_url + '?page=' + str(i)
        soup = await load_url(session, url)
        print(gather_data(soup))

    await session.close()



if __name__ == "__main__":
    asyncio.run(main())


