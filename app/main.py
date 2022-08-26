from crypto_currency import crypto_currency
import settings
import logging

import boto3
import ccxt


logger = logging.getLogger().setLevel(logging.INFO)
print('Loading function...')


def _get_parameters(keys):
    ssm = boto3.client('ssm', region_name=settings.region)
    res = ssm.get_parameters(
        Names=keys, WithDecryption=True
    )
    try:
        return res['Parameters']
    except:
        logger.error(f'get_parameters: not Parameters {res}')
        raise


def lambda_handler(event, context):
    params = _get_parameters(['/bitbank/apikey', '/bitbank/apisecret'])
    bitbank = ccxt.bitbank()
    API = crypto_currency.ApiClient(
        bitbank, params[0]['Value'], params[1]['Value'])
    data = {
        "status_code": 400,
        "body": 'none'
    }
    print('-------------------')
    API.expire_at_cancel_order()
    order = API.send_order()
    if order:
        data["status_code"] = 200
        data["body"] = order

    return data
