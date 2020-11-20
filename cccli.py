#!/usr/bin/python
#
# Generate/list virtual credit cards with the privacy.com api
# Requires issuer API token
#
# 2020 :: Neko


import sys
import json
import getopt
import requests


class PrivacyAPI:

    __api_url__ = 'https://api.privacy.com/v1'
    __api_token__ = None

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def __api_post__(self, endpoint, postdata):
        response = requests.post(
            "{}/{}".format(
                self.__api_url__,
                endpoint),
            headers={
                'content-type': 'application/json',
                'accept': 'application/json',
                'Authorization': 'api-key {}'.format(self.__api_token__)},
            json=postdata)
        return response

    def __api_get__(self, endpoint, params):
        # todo: pagination
        params = params if params else []
        s_params = '&'.join(["{}={}".format(p[0], p[1]) for p in params])
        return requests.get(
            '{}/{}?{}'.format(
                self.__api_url__,
                endpoint,
                s_params),
            headers={
                'accept': 'application/json',
                'authorization': 'api-key {}'.format(self.__api_token__)})

    def __api_callback__(self, response):
        print(response.text)
        return response

    def __api_key_from_file__(self, path):
        self.__api_token__ = open(path, 'r').readline().strip()

    def funding_accounts(self, account_type):
        if account_type not in ['bank', 'card']:
            account_type = None
        return self.__api_callback__(
            self.__api_get__(
                'fundingsource{}'.format(
                '/' + account_type if account_type else ''),
                None))

    def cards(self, params):
        return self.__api_callback__(
            self.__api_get__(
                'card', params))

    def transactions(self, trx_status):
        if trx_status not in ['approvals', 'declines', 'all']:
            trx_status = 'all'
        return self.__api_callback__(
            self.__api_get__(
                'transaction/{}'.format(trx_status), None))

    def create_card(self, name, card_type, spend_limit, spend_limit_duration):
        if card_type not in ['SINGLE_USE', 'MERCHANT_LOCKED']:
            card_type = 'SINGLE_USE'
        if spend_limit_duration not in ['TRANSACTION', 'MONTHLY', 'ANNUALLY', 'FOREVER']:
            spend_limit_duration = 'FOREVER'
        spend_limit = int(spend_limit or 100)
        postdata = {
            'memo': name or "{}_{}_{}".format(spend_limit, card_type, spend_limit_duration),
            'type': card_type,
            'spend_limit': int(spend_limit),
            'spend_limit_duration': spend_limit_duration }
        return self.__api_callback__(
            self.__api_post__(
                'card', postdata))

p_fund_acct = lambda x: "Acct: {} State: {} Type: {}".format(
    x['account_name'],
    x['state'],
    x['type'])

p_card = lambda x: "{} {}/{} {}  -  {}".format(
    x['pan'],
    x['exp_month'],
    x['exp_year'],
    x['cvv'],
    x['memo'])

p_trx = lambda x: "{} ".format(
    x['created']
    x['amount']
    x['merchant']
    x['status'])

with PrivacyAPI() as api:
    api.__api_key_from_file__('/path/to/token.txt')
    if '-l' in sys.argv:
        for c in list(map(p_card, json.loads(api.cards(None).text)['data'])):
            print(c)
    if '-t' in sys.argv:
        for t in list(map(p_trx, json.loads(api.transactions(None).text)['data'])):
            print(t)
    if '-f' in sys.argv:
        for f in list(map(p_fund_acct, json.loads(api.funding_accounts(None).text))):
            print(f)
    if '-c' in sys.argv:
        print()
        print("Card types      : *SINGLE_USE, MERCHANT_LOCKED")
        print("Spend durations : TRANSACTION, MONTHLY, ANNUALLY, *FOREVER")
        print("* = default")
        print()
        try:
            response = api.create_card(
                input("> Card name      : "),
                input("> Card type      : "),
                input("> Spend limit    : "),
                input("> Spend duration : "))
            print(response.text)
        except:
            pass
