#!/usr/bin/env python
from fr1ckets import app
from fr1ckets.model import setup, model
from flask import g
import sys
import datetime
import csv
import pprint
import os
import unicodedata

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
	app.debug = True
	app.secret_key = app.config['SECRET_KEY']
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')


email = sys.argv[1]
names = sys.argv[2:]

dest_ticket_name = 'ticket_vip_all'

with app.app_context():
	setup.setup_db()

	print "email={0} names={1}".format(email, names)

	products = model.products_get(g.db_cursor)
	ticket = None
	for p in products:
		if p['name'] == dest_ticket_name:
			ticket = p
	if not p:
		print "can't find ticket {0}".format(dest_ticket_name)
		raise Exception

	purchased_items = []
	for n in names:
		purchased_items.append({
			'product_id' : ticket['id'],
			'n' : 1,
			'person_name' : n,
			'person_dob' : '1970-01-01',
			'person_volunteers_before' : 0,
			'person_volunteers_during' : 0,
			'person_volunteers_after' : 0,
			'person_food_vegitarian' : 0,
		})
	billing = { 'name' : '', 'address' : '', 'vat' : '' }
	general = { 'transportation' : 'CAR' }
	model.purchase_create(g.db_cursor, email,
		voucher_codes=[], products=purchased_items,
		billing_info=billing, general_ticket_info=general,
		queued=0)

	g.db_commit = True
	setup.wrapup_db(None)
