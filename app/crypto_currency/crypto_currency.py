import datetime
import logging
import time

import ccxt

import settings
from utils.utils import truncate


logger = logging.getLogger(__name__)


class ApiClient(object):
    def __init__(self, client, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = client
        self.client.apiKey = api_key
        self.client.secret = api_secret

    def get_balance(self):
        try:
            balance = self.client.fetch_balance()
            if balance:
                return [asset for asset in balance['info']['data']
                        ['assets'] if asset['asset'] == 'jpy'][0]
        except Exception as e:
            logger.error(f'get_balance error={e}')
            raise

    # ビットコイン価格取得
    def get_ticker(self):
        try:
            orderbook = self.client.fetch_order_book(settings.product_code)
            if orderbook['asks'] and not orderbook['bids']:
                return None
            bid = orderbook['bids'][0][0]
            ask = orderbook['asks'][0][0]
            spread = (ask - bid)
        except ccxt.NetworkError as e:
            logger.error(
                f'{self.client.id} fetch_order_book failed due to a network error: {e}')
        except ccxt.ExchangeError as e:
            logger.error(
                f'{self.client.id} fetch_order_book failed due to a  exchange error: {e}')
        except Exception as e:
            logger.error(
                f'{self.client.id} fetch_order_book failed with: {e}')

        return {'bid': bid, 'ask': ask, 'spread': spread}

    def _size(self, ticker):
        if not settings.amount_buy:
            return settings.size
        try:
            f = settings.amount / ticker['ask']
            return truncate(f, 4)
        except Exception as e:
            logger.error(
                f'size error:  amount={settings.amount}, ask={ticker["ask"]} : {e}')
        return 0

    def _limit_price(self, ticker):
        if ticker["bid"] > 0 and settings.limit_price_percent > 0:
            return ticker["bid"] * settings.limit_price_percent
        return 0

    def send_order(self):
        for _ in range(5):
            try:

                ticker = self.get_ticker()
                order = self.client.create_order(
                    symbol=settings.product_code,
                    type=settings.order_type,
                    price=self._limit_price(ticker),
                    side=settings.BUY,
                    amount=self._size(ticker),
                    params={"post_only": settings.post_only}
                )
                if order:
                    logger.info(f"send_order= {order}")
                    return order
            except ccxt.BaseError as e:
                logger.error(f"send_order= {e}")
            time.sleep(5)

        return None

    def cancel_order(self, order):
        """ 注文をキャンセル """
        try:
            self.client.cancel_order(
                symbol=settings.product_code, id=order["id"])
        except Exception as e:
            logger.error(f"cancel_order= {e}, order={order}")

    def expire_at_cancel_order(self):
        ''' 注文 有効期限外をキャンセル '''
        orders = self.client.fetch_open_orders(symbol=settings.product_code)
        for o in orders:
            expire_at = datetime.datetime.fromtimestamp(
                o['timestamp']/1000) + datetime.timedelta(hours=settings.expire_hour)
            if expire_at > datetime.datetime.now():
                continue
            self.cancel_order(o)
