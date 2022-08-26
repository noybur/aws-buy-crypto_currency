import configparser

from utils.utils import bool_from_str


BUY = 'buy'
SELL = 'sell'

conf = configparser.ConfigParser()
conf.read('settings.ini')

product_code = conf['base']['product_code']
order_type = conf['base']['order_type']
limit_price_percent = 0
post_only = False
if order_type == 'limit':
    limit_price_percent = float(conf['base']['limit_price_percent'])
    post_only = bool_from_str(conf['base']['post_only'])

expire_hour = int(conf['base']['expire_hour'])

size = conf['base']['size']
amount_buy = bool_from_str(conf['base']['amount_buy'])
amount = int(conf['base']['amount'])

region = conf['aws']['region']
