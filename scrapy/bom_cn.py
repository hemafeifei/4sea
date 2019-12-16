#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _settings import *
import pandas as pd
from datetime import datetime, timedelta
import os

# pn = "18925103199"
pn = "13397662615"
url = 'https://danjuanapp.com/ccount?channel=1100104020'
pn_id = 'tel'
clk = 'send-btn'

def bob(url, pn_id, pn, clk, lim):
    n = 0
    while n < lim:
        get_pn_validation(url=url,
                          pn_id=pn_id,
                          pn=pn,
                          clk_class=clk)
        n+=1

if __name__ == '__main__':
    bob(url=url, pn_id=pn_id, pn=pn, clk=clk, lim=600)