#!/usr/bin/env python
import requests
from lxml import html
import pprint
import sys
import random
import string
import time
import datetime
import json
import multiprocessing

auth=('we\'re doing our best to keep creds out of github', 'but you know what, the first three folks to hit me up at the infodesk who actually read this -- a beer on me')
url = sys.argv[1]
n_concurrent = int(sys.argv[2])

def D(*args, **kwargs):
	print("DEBUG {0} {1}".format(pprint.pformat(*args), pprint.pformat(kwargs) if kwargs else ''))

class Form(object):
	tshirt_choices = [ 'tshirt_adult_m_' + size for size in [ 'xs', 's', 'm', 'l', 'xl', 'xxl', '3xl', '4xl' ] ]
	tshirt_choices.extend([ 'tshirt_adult_f_' + size for size in [ 'xs', 's', 'm', 'l', 'xl', 'xxl' ] ])
	tshirt_choices.extend([ 'tshirt_kid_' + size for size in [ 'xs', 's', 'm', 'l', 'xl' ] ])
	token_choices = [ 0, 5, 10, 15, 20, 30, 40, 50, 100 ]
	mug_choices = [ x for x in range(0, 9) ]
	donation_choices = [ x for x in range(0, 9) ]
	camper_spot_choices = [ x for x in range(0, 9) ]
	hoodie_choices = [ 'hoodie_adult_m_' + size for size in [ 'xs', 's', 'm', 'l', 'xl', 'xxl', '3xl', '4xl' ] ]
	hoodie_choices.extend([ 'hoodie_adult_f_' + size for size in [ 'xs', 's', 'm', 'l', 'xl' ] ])
	hoodie_choices.extend([ 'hoodie_kid_' + size for size in [ 'xs', 's', 'm', 'l', 'xl' ] ])
	badge_accessory_a_choices = [ x for x in range(0, 9) ]
	badge_accessory_b_choices = [ x for x in range(0, 9) ]

	def __init__(self):
		self.data = {}
		self.n_tickets = 0
		for k in [ 'payment', 'supervision', 'excellent' ]:
			self.data['terms_'+k] = 'on'
		for t in self.tshirt_choices:
			self.data[t] = 0
		for t in self.hoodie_choices:
			self.data[t] = 0
		self.data['n_tickets'] = self.n_tickets

	def set_static(self, email, token):
		self.data['email'] = email
		self.data['csrf_token'] = token

	def set_tokens(self, n):
		if n in self.token_choices:
			self.data['token'] = n
		else:
			print "not a valid token amount, this {0}".format(n)

	def set_badge_accessory_as(self, n):
		if n in self.badge_accessory_a_choices:
			self.data['badge_accessory_a'] = n
		else:
			print "not a valid badge_accessory_a amount, this {0}".format(n)

	def set_badge_accessory_bs(self, n):
		if n in self.badge_accessory_b_choices:
			self.data['badge_accessory_b'] = n
		else:
			print "not a valid badge_accessory_b amount, this {0}".format(n)



	def set_donations(self, n):
		if n in self.donation_choices:
			self.data['donation'] = n
		else:
			print "not a valid donation amount, this {0}".format(n)

	def set_mugs(self, n):
		if n in self.mug_choices:
			self.data['mug'] = n
		else:
			print "not a valid mug amount, this {0}".format(n)

	def set_camper_spots(self, n):
		if n in self.camper_spot_choices:
			self.data['camper_spot'] = n
		else:
			print "not a valid camper_spot amount, this {0}".format(n)
	
	def set_tshirt(self, which, n):
		if which in self.tshirt_choices:
			self.data[which] = n
		else:
			print "not a valid tshirt, this {0}".format(which)

	def set_hoodie(self, which, n):
		if which in self.hoodie_choices:
			self.data[which] = n
		else:
			print "not a valid hoodie, this {0}".format(which)

	def add_ticket(self, name, dob, billable, volunteers_during, volunteers_after, veggy):
		t = 'tickets_{0}_'.format(self.n_tickets)
		self.n_tickets += 1
		self.data['n_tickets'] = self.n_tickets
		self.data.update({
			t+'name' : name,
			t+'dob_year' : dob.year,
			t+'dob_month' : dob.month,
			t+'dob_day' : dob.day,
		})
		# yes, browers don't show these when not checked
		if billable:
			self.data[t+'billable'] = 'on'
		if volunteers_during:
			self.data[t+'options_volunteers_during'] = 'on'
		if volunteers_after:
			self.data[t+'options_volunteers_after'] = 'on'
		if veggy:
			self.data[t+'options_vegitarian'] = 'on'

	def set_business_info(self, name, address, vat):
		self.data.update({
			'business_name' : name,
			'business_address' : address,
			'business_vat' : vat,
		})

	def need_business_info(self):
		return len([ self.data[k] for k in self.data if '_billable' in k and self.data[k] == 'on'])

	def __str__(self):
		return pprint.pformat(self.data)

class RandomForm(Form):

	def __init__(self):
		Form.__init__(self)

	def fill(self, n_tickets, token):
		base = ''.join([ random.choice(string.ascii_letters) for _ in range(5) ])
		age_min = int(time.time())
		age_max = 0

		self.set_static('{0}@{0}.notreal'.format(base), token)
		self.set_tokens(random.choice(self.token_choices))
		self.set_mugs(random.choice(self.mug_choices))
		self.set_donations(random.choice(self.donation_choices))
		self.set_camper_spots(random.choice(self.camper_spot_choices))
		self.set_badge_accessory_as(random.choice(self.badge_accessory_a_choices))
		self.set_badge_accessory_bs(random.choice(self.badge_accessory_b_choices))

		for t in range(n_tickets):
			ext = ''.join([ random.choice(string.ascii_letters) for _ in range(4) ])
			name = '{0} {1}'.format(ext, base)
			dob = datetime.datetime.fromtimestamp(random.randrange(age_max, age_min))
			self.add_ticket(name, dob, not bool(random.randint(0, 8)),
				*(bool(random.randint(0, 1)) for _ in range(3) ))
			self.set_tshirt(random.choice(self.tshirt_choices), 1)
			self.set_hoodie(random.choice(self.hoodie_choices), 1)

		if self.need_business_info():
			self.set_business_info(
					base + 'corp NV',
					base + 'street 1\n' + base + 'ville\n' + base + 'land',
					'BTW 111.111.4444')

def order_random_tickets(queue, url, min_tickets, max_tickets):
	s = requests.session()
	
	ret = {}
	ret['error_data'] = []

	# get the ticket page
	ts = time.time()
	r = s.get(url+'/tickets', auth=auth)
	ret['tickets_page'] = 'ERROR' if r.status_code != 200 else time.time() - ts

	# parse the page, we need the CSRF token
	try:
		page = html.fromstring(r.text)
		csrf_token = page.forms[0].fields['csrf_token']
	except Exception as e:
		ret['tickets_page'] = 'ERROR'
		ret['error_data'].append(r.text)
		csrf_token = 'foo'

	# generate tickets
	form = RandomForm()
	form.fill(random.randrange(min_tickets, max_tickets+1), csrf_token)

	# check the reservation on email
	ts = time.time()
	r = s.get(url+'/api/get_reservation/' + form.data['email'], auth=auth)
	ret['reservation'] = 'ERROR' if r.status_code != 200 else time.time() - ts

	# actually order the tickets
	ts = time.time()
	r = s.post(url+'/api/tickets_register', auth=auth, data=form.data)
	ret['registration'] = 'ERROR' if r.status_code != 200 else time.time() - ts

	# check the JSON outcome
	try:
		registration_result = json.loads(r.text)
	except:
		ret['registration'] = 'ERROR'
		registration_result = []
		ret['error_data'].append(r.text)

	if 'redirect' in registration_result:
		ts = time.time()
		r = s.get(url+registration_result['redirect'], auth=auth)
		ret['confirmation'] = 'ERROR' if r.status_code != 200 else time.time() - ts
	else:
		ret['registration'] = 'ERROR'
		ret['confirmation'] = 'ERROR'
		ret['error_data'].append(registration_result)

	if not 'ERROR' in ret.values():
		ret['total'] = sum([ ret[k] for k in ret.keys() if 'data' not in k])

	ret['data'] = form.data

	queue.put(ret)

start = time.time()
processes = []
for i in range(n_concurrent):
	q = multiprocessing.Queue()
	p = multiprocessing.Process(target=order_random_tickets, args=(q,url,1,3))
	processes.append((p, q))
	p.start()

outcomes = []
for p, q in processes:
	outcomes.append(q.get())
	p.join()

n_errors = len([ o for o in outcomes if 'ERROR' in o.values() ])
totals = [ o['total'] for o in outcomes if 'total' in o ]
avg_total = sum(totals)/len(totals)
for o in outcomes:
	if not 'total' in o:
		pprint.pprint("error:")
		pprint.pprint(o)

print "{0} calls completed on {1}, n_errors={2} avg_total={3}".format(len(outcomes),
		time.time()-start, n_errors, avg_total)
