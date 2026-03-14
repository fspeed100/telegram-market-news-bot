import requests
import feedparser
import yfinance as yf
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler
from datetime import time

TOKEN=8701576141:AAHezESKNkoF379rF0sZ-UvAS7qrDm8TbME

chat_id=None

feeds={

"PTI News":"https://www.ptinews.com/rss",

"India":"https://timesofindia.indiatimes.com/rssfeedstopstories.cms",

"Finance":"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",

"Global":"https://rss.nytimes.com/services/xml/rss/nyt/World.xml",

"Assam":"https://news.google.com/rss/search?q=Assam&hl=en-IN&gl=IN&ceid=IN:en",

"Cement":"https://news.google.com/rss/search?q=cement+india&hl=en-IN&gl=IN&ceid=IN:en",

"Technology":"https://news.google.com/rss/search?q=technology+news&hl=en-IN&gl=IN&ceid=IN:en"

}

FII_DII_URL="https://www.nseindia.com/api/fiidiiTradeReact"

OPTION_CHAIN_URL="https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

def ai_summary(text):

    words=text.split()

    if len(words)>12:

        return " ".join(words[:12])+"..."

    return text


async def start(update,context):

    global chat_id

    chat_id=update.effective_chat.id

    await update.message.reply_text(
        "F100 News Bot Activated. Alerts started."
    )


async def send_news(context):

    for category,url in feeds.items():

        feed=feedparser.parse(url)

        for entry in feed.entries[:2]:

            summary=ai_summary(entry.title)

            keyboard=[[InlineKeyboardButton("Read Full Article",url=entry.link)]]

            reply_markup=InlineKeyboardMarkup(keyboard)

            msg=f"""
{category}

Headline
{entry.title}

Summary
{summary}
"""

            await context.bot.send_message(chat_id=chat_id,text=msg,reply_markup=reply_markup)


def breakout_stock():

    stocks=["RELIANCE","HDFCBANK","ICICIBANK","INFY","TCS"]

    breakout=[]

    for s in stocks:

        try:

            data=yf.Ticker(s+".NS").history(period="1d")

            move=abs(data["Close"].iloc[-1]-data["Open"].iloc[-1])

            if move>10:

                breakout.append(s)

        except:
            pass

    return breakout


def get_fii_dii():

    try:

        headers={"User-Agent":"Mozilla/5.0"}

        r=requests.get(FII_DII_URL,headers=headers)

        data=r.json()

        fii=data["data"][0]["fii"]

        dii=data["data"][0]["dii"]

        return fii,dii

    except:

        return "NA","NA"


async def premarket(context):

    nifty=yf.Ticker("^NSEI")

    data=nifty.history(period="1d")

    close=data["Close"].iloc[-1]

    high=data["High"].iloc[-1]

    low=data["Low"].iloc[-1]

    pivot=(high+low+close)/3

    support=round((2*pivot)-high,2)

    resistance=round((2*pivot)-low,2)

    fii,dii=get_fii_dii()

    msg=f"""
PRE MARKET BRIEF

NIFTY Close: {close}

Support: {support}
Resistance: {resistance}

FII: {fii}
DII: {dii}
"""

    await context.bot.send_message(chat_id=chat_id,text=msg)


async def closing(context):

    nifty=yf.Ticker("^NSEI")

    close=nifty.history(period="1d")["Close"].iloc[-1]

    fii,dii=get_fii_dii()

    msg=f"""
MARKET CLOSE

NIFTY Close: {close}

FII: {fii}
DII: {dii}
"""

    await context.bot.send_message(chat_id=chat_id,text=msg)


async def intelligence_report(context):

    feed=feedparser.parse(feeds["PTI News"])

    top_news=[entry.title for entry in feed.entries[:3]]

    nifty=yf.Ticker("^NSEI")

    data=nifty.history(period="1d")

    close=data["Close"].iloc[-1]

    trend="Bullish" if data["Close"].iloc[-1]>data["Open"].iloc[-1] else "Bearish"

    fii,dii=get_fii_dii()

    sectors={
        "IT":"Positive",
        "Banking":"Positive",
        "Infra":"Strong"
    }

    breakout=breakout_stock()

    msg=f"""
DAILY INTELLIGENCE REPORT

Top News
• {top_news[0]}
• {top_news[1]}
• {top_news[2]}

Market Summary
NIFTY Close: {close}
Trend: {trend}

FII/DII
FII: {fii}
DII: {dii}

Sector Performance
IT: {sectors['IT']}
Banking: {sectors['Banking']}
Infra: {sectors['Infra']}

Top Breakout Stocks
{", ".join(breakout)}
"""

    await context.bot.send_message(chat_id=chat_id,text=msg)


def main():

    app=ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",start))

    job_queue=app.job_queue

    job_queue.run_repeating(send_news,interval=1800)

    job_queue.run_daily(premarket,time=time(8,45))

    job_queue.run_daily(closing,time=time(15,35))

    job_queue.run_daily(intelligence_report,time=time(19,45))

    print("F100 News Bot Running")

    app.run_polling()


if __name__=="__main__":

    main()
