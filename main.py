from requests_html import HTMLSession, AsyncHTMLSession
from bs4 import BeautifulSoup
from pydantic import BaseModel
import asyncio
from typing import Optional
import pandas as pd
import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")


async def load_url(session: AsyncHTMLSession, url: str) -> BeautifulSoup:
    try:
        response = await session.get(url)
        await response.html.arender(sleep=2, scrolldown=15, keep_page=True)
        return BeautifulSoup(response.html.html, "html.parser")
    except Exception as e:
        print(e)

def gather_data(soup: BeautifulSoup) -> list:
    class Coin(BaseModel):
        coin_rank: Optional[int]
        coin_logo: Optional[str]
        coin_name: Optional[str]
        coin_ticker: Optional[str]
        coin_price: Optional[str]
        change_1hr: Optional[str]
        change_24hr: Optional[str]
        change_7d: Optional[str]
        market_cap: Optional[str]
        volume_24hr: Optional[str]
        circ_supply: Optional[str]

    coins = []

    table = soup.find("table", class_="cmc-table")
    table_rows = table.find_all("tr")

    for row in table_rows[2:]:
        coin_rank = (
            row.find("p", {"class": "sc-4984dd93-0 iWSjWE"}).text
            if row.find("p", {"class": "sc-4984dd93-0 iWSjWE"})
            else None
        )
        coin_logo = (
            row.find("img", {"class": "coin-logo"})["src"]
            if row.find("img", {"class": "coin-logo"})
            else None
        )
        coin_name = (
            row.find("p", {"class": "sc-4984dd93-0 kKpPOn"}).text
            if row.find("p", {"class": "sc-4984dd93-0 kKpPOn"})
            else None
        )
        coin_ticker = (
            row.find("p", {"class": "coin-item-symbol"}).text
            if row.find("p", {"class": "coin-item-symbol"})
            else None
        )
        coin_price = (
            row.find("div", {"class": "sc-a0353bbc-0"}).text
            if row.find("div", {"class": "sc-a0353bbc-0"})
            else None
        )
        change_1hr, change_24hr, change_7d = [
            tag.text if tag else None
            for tag in row.find_all("span", {"class": "sc-d55c02b-0"})
        ]
        market_cap = (
            row.find("span", {"class": "sc-7bc56c81-0"}).text
            if row.find("span", {"class": "sc-7bc56c81-0"})
            else None
        )
        volume_24hr = (
            row.find("p", {"class": "sc-4984dd93-0 jZrMxO font_weight_500"}).text
            if row.find("p", {"class": "sc-4984dd93-0 jZrMxO font_weight_500"})
            else None
        )
        circ_supply = (
            row.find("p", {"class": "sc-4984dd93-0 WfVLk"}).text
            if row.find("p", {"class": "sc-4984dd93-0 WfVLk"})
            else None
        )

        tempCoin = Coin(
            coin_rank=int(coin_rank),
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

async def extract_data(session: AsyncHTMLSession):
    base_url = "https://coinmarketcap.com/"
    pages_to_scrape = 10
    session = session

    coins = []

    for i in range(1, pages_to_scrape + 1):
        url = f"{base_url}?page={i}"
        soup = await load_url(session, url)
        coins = coins + gather_data(soup)

    await session.close()

    return coins

def get_dateTime():
    now = datetime.datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H%M%S")
    return dt_string

def save_to_excel(Coins, currentDateTime):
    data = [coin.dict() for coin in Coins]
    df = pd.DataFrame(data)
    # get the current date and time to append the excel file name
    dt_string = currentDateTime
    df.to_excel(f"Coins_{dt_string}.xlsx", index=False)


def email_excel(currentDateTime):
    msg = MIMEMultipart()

    msg["Subject"] = "Top 1000 Cryptocurrencies"

    msg["From"] = EMAIL_ADDRESS

    msg["To"] = "siyal343@gmail.com"

    body = "Scrapped 1000 Cryptocurrencies Rankings"

    msg.attach(MIMEText(body, "plain"))

    with open(f"Coins_{currentDateTime}.xlsx", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename= Coins_{currentDateTime}.xlsx"
        )
        msg.attach(part)


    with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)

    os.remove(f"Coins_{currentDateTime}.xlsx")


async def main():
    session = AsyncHTMLSession()
    return await extract_data(session)


if __name__ == "__main__":
    Coins = asyncio.run(main())
    print(f"there were {len(Coins)} coins extracted")
    currentDateTime = get_dateTime()
    save_to_excel(Coins, currentDateTime)
    email_excel(currentDateTime)    


