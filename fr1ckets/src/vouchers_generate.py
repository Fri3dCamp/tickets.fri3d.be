#!/usr/bin/env python
from fr1ckets import app
from fr1ckets.model import setup, model
from flask import g
import sys
import datetime
import csv
import pprint
import os

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
	app.debug = True
	app.secret_key = app.config['SECRET_KEY']
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')

if len(sys.argv) <= 4:
	print "usage: {0} how_many discount_in_eur reason".format(sys.argv[0])
	sys.exit(1)

N_VOUCHERS = int(sys.argv[1])
DISCOUNT = int(sys.argv[2])
REASON = " ".join(sys.argv[3:])

with app.app_context():
	setup.setup_db()
	d = {
		'discount' : DISCOUNT,
		'claimed' : False,
		'claimed_at' : None,
		'comments' : 'generated by script',
		'reason' : REASON,
	}
	for i in range(N_VOUCHERS):
		code = model.voucher_create(g.db_cursor, d)
		print code

	g.db_commit = True
	setup.wrapup_db(None)
