import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def get_sentiment_score(text):
    return analyzer.polarity_scores(text)['compound']


def analyze_stock(ticker):
    t = yf.Ticker(ticker)
    news = t.news
    sentiment_scores = []
    for item in news:
        title = item.get('title', '')
        sentiment_scores.append(get_sentiment_score(title))
    avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    return avg_score


def main():
    tickers = ['AAPL', 'GOOGL', 'MSFT']
    results = {t: analyze_stock(t) for t in tickers}
    for t, score in results.items():
        print(f"{t}: sentiment score {score:.3f}")

if __name__ == '__main__':
    main()
