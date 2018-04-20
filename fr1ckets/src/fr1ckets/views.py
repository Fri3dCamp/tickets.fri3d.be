# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:noexpandtab
from flask import request, jsonify, render_template, redirect, url_for, g, Response, session
from flask_wtf import FlaskForm as Form
from wtforms import StringField, validators
from wtforms import BooleanField, IntegerField, TextAreaField
from wtforms.fields.html5 import EmailField, DateTimeField
from fr1ckets import app
from fr1ckets.texts import texts
from fr1ckets.model import model
from fr1ckets.mail import mail
from functools import wraps
import time
import json
import datetime

D = app.logger.debug

def check_auth_admin(u, p):
	return u == app.config['ADMIN_USERNAME'] and p == app.config['ADMIN_PASSWORD']

def check_auth_public(u, p):
	return u == app.config['PUBLIC_USERNAME'] and p == app.config['PUBLIC_PASSWORD']

def auth_basic():
	return Response('No', 401, { 'WWW-Authenticate' : 'Basic realm="Login Required"' })

def req_auth_admin(f):
	@wraps(f)
	def fn(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth_admin(auth.username, auth.password):
			return auth_basic()
		return f(*args, **kwargs)
	return fn

def req_auth_public(f):
	@wraps(f)
	def fn(*args, **kwargs):
		if not app.config['PUBLIC']:
			auth = request.authorization
			if not auth or not check_auth_public(auth.username, auth.password):
				return auth_basic()
		return f(*args, **kwargs)
	return fn

def generate_tshirt_names():
	out = []
	for tshirt in [ 'adult_f', 'adult_m' ]:
		for size in [ 'xs', 's', 'm', 'l', 'xl', 'xxl' ]:
			out.append("tshirt_{0}_{1}".format(tshirt, size))
	for tshirt in [ 'kid' ]:
		for size in [ 'xs', 's', 'm', 'l', 'xl' ]:
			out.append("tshirt_{0}_{1}".format(tshirt, size))

	return out

def prettify_purchase_code(code):
	return "+++{0}/{1}/{2}+++".format(code[:3], code[3:7], code[7:])

# WTForms is a very nice form generation/validation tool in which one
# adds members to a Form class which provides oneliners for HTML generation
# and form validation
#
# we're totally mis-using it!
#
# we don't use the HTML generation, since our form is prettier & more
# dynamic than what it provides, and we split it up into two forms, one
# generic (TicketForm) for the always-visible form entries, one dynamically
# generated by make_form_individual_tickets() for the collapsible per-ticket
# parts (because we don't know the number of tickets beforehand)
# we use those for form validation, so once validated the rest of the code
# can assume content correctness
class TicketForm(Form):
	email = EmailField('email', validators=[
		validators.Email(message="Really an email?"),
		])

	voucher_code_0 = StringField('voucher_code_0', validators=[])
	voucher_code_1 = StringField('voucher_code_1', validators=[])
	voucher_code_2 = StringField('voucher_code_2', validators=[])
	voucher_code_3 = StringField('voucher_code_3', validators=[])
	voucher_code_4 = StringField('voucher_code_4', validators=[])

	n_tickets = IntegerField('n_tickets', validators=[
		validators.NumberRange(min=0, max=20),
		])

	token = IntegerField('token', validators=[
		validators.NumberRange(min=0, max=100),
		])

	badge_robot_parts = IntegerField('badge_robot_parts', validators=[
		validators.NumberRange(min=0, max=20),
		])

	for tshirt in generate_tshirt_names():
		vars()[tshirt] = IntegerField(tshirt, validators=[
			validators.NumberRange(min=0, max=10),
			])

	terms_payment = BooleanField('', default=False,
		validators=[
			validators.DataRequired(message="did not agree to terms")
		])
	terms_supervision = BooleanField('', default=False,
		validators=[
			validators.DataRequired(message="did not agree to terms")
		])
	terms_excellent = BooleanField('', default=False,
		validators=[
			validators.DataRequired(message="did not agree to terms")
		])

class BusinessForm(Form):
	business_name = StringField("business_name", validators=[ validators.DataRequired() ])
	business_address = StringField("business_address", validators=[ validators.DataRequired() ])
	business_vat = StringField("business_vat", validators=[ validators.DataRequired() ])

def make_form_individual_tickets(n_tickets):
	class IndividualTicketForm(Form):
		pass

	if n_tickets:
		setattr(IndividualTicketForm, 'bringing_camper', BooleanField('bringing_camper'))

	for i in range(n_tickets):
		fmt = "tickets_{0}".format(i)
		name = fmt + '_name'
		setattr(IndividualTicketForm, name, StringField(name, validators=[ validators.DataRequired() ]))

		name = fmt + '_billable'
		setattr(IndividualTicketForm, name, BooleanField(name))

		name = fmt + '_dob_year'
		setattr(IndividualTicketForm, name, IntegerField(name,
			validators=[
				validators.NumberRange(min=1900, max=datetime.date.fromtimestamp(time.time()).year)
				]))
		name = fmt + '_dob_month'
		setattr(IndividualTicketForm, name, IntegerField(name,
			validators=[
				validators.NumberRange(min=1, max=12)
				]))
		name = fmt + '_dob_day'
		setattr(IndividualTicketForm, name, IntegerField(name,
			validators=[
				validators.NumberRange(min=1, max=31)
				]))

		fmt += "_options"
		for field in [ '_not_volunteering_during', '_volunteers_after', '_vegitarian' ]:
			name = fmt + field
			setattr(IndividualTicketForm, name, BooleanField(name, default=False))
	return IndividualTicketForm

def extract_billing_info(form_tickets):
	out = {}

	for e in [ 'name', 'address', 'vat' ]:
		field = getattr(form_tickets, 'business_{0}'.format(e), None)
		out[e] = field.data if field else ''

	return out

def extract_general_ticket_info(form_tickets):
	out = {}

	field = getattr(form_tickets, 'bringing_camper', None)
	out['bringing_camper'] = field.data if field else False

	return out

def extract_products(cursor, form_general, form_tickets):

	p = map(dict, model.products_get(cursor))
	known_tickets = sorted([ t for t in p if 'ticket' in t['name'] ], key=lambda t: t['max_dob'], reverse=True)
	known_tshirts = [ t for t in p if 'tshirt' in t['name'] ]
	known_tokens = [ t for t in p if 'token' in t['name'] ]
	known_badge_parts = [ t for t in p if 'badge' in t['name'] ]
	seen_business_tickets = False
	out = []

	n_tickets = form_general.n_tickets.data

	def find_knowns(known, form):
		out = []
		for k_t in known:
			n = getattr(form, k_t['name'], None)
			if not (n and n.data):
				continue
			out.append({
				'product_id' : k_t['id'],
				'n' : n.data,
				'person_name' : None,
				'person_dob' : None,
				'person_volunteers_during' : False,
				'person_volunteers_after' : False,
				'person_food_vegitarian' : False,
			})
		return out

	out.extend(find_knowns(known_tshirts, form_general))
	out.extend(find_knowns(known_tokens, form_general))
	out.extend(find_knowns(known_badge_parts, form_general))

	for i in range(n_tickets):
		fmt = 'tickets_{0}'.format(i)
		dob = datetime.datetime(getattr(form_tickets, fmt + '_dob_year').data,
			getattr(form_tickets, fmt + '_dob_month').data,
			getattr(form_tickets, fmt + '_dob_day').data)
		billable = getattr(form_tickets, fmt + '_billable').data
		relevant_ticket = None
		for t in [ t for t in known_tickets if t['billable'] == billable]:
			if dob >= t['max_dob']:
				relevant_ticket = t
				break
		if billable:
			seen_business_tickets = True
		out.append({
			'product_id' : relevant_ticket['id'],
			'n' : 1,
			'person_dob' : dob,
			'person_name' : getattr(form_tickets, fmt + '_name').data,
			'person_volunteers_during' : not getattr(form_tickets, fmt + '_options_not_volunteering_during').data,
			'person_volunteers_after' : getattr(form_tickets, fmt + '_options_volunteers_after').data,
			'person_food_vegitarian' : getattr(form_tickets, fmt + '_options_vegitarian').data,
		})
	
	return out, seen_business_tickets

def price_distribution_strategy(cursor, nonce):
	"""
	strategy to figure out where to apply any discounts
	"""
	price_total = model.get_purchase_total(g.db_cursor, nonce)
	price_billable = model.get_purchase_total(g.db_cursor, nonce, True)
	price_unbillable = price_total - price_billable
	price_discount = model.get_purchase_discount(g.db_cursor, nonce)

	if price_discount > price_total:
		# all expenses covered by discount
		return 0, 0

	if price_discount > price_unbillable:
		# total of unbillable covered by discount, leftover discount
		# applied to billable
		return 0, (price_billable - (price_discount - price_unbillable))

	# default, substract discount from unbillable
	return price_unbillable - price_discount, price_billable


@app.route('/tickets', methods=[ 'GET' ])
@req_auth_public
def tickets():
	if app.config['CLOSED']:
		return render_template('closed.html')
	form = TicketForm()
	tickets_available = app.config['TICKETS_MAX'] - model.tickets_actual_total(g.db_cursor)
	return render_template('tickets.html',
			selling_inhibited=app.config['INHIBIT_SELLING'],
			form=form, tickets_available=tickets_available)

@app.route('/api/tickets_register', methods=[ 'POST' ])
@req_auth_public
def ticket_register():
	form = TicketForm()
	tickets_total_sold = model.tickets_actual_total(g.db_cursor)
	tickets_available = app.config['TICKETS_MAX'] - tickets_total_sold

	if not form.validate_on_submit():
		return jsonify(
			status='FAIL',
			message=u"Het formulier is niet volledig! ({0})".format(", ".join(form.errors)))

	# the static part of the form is OK, we can check how large the dynamic part is
	# and build a validator accordingly
	n_tickets = form.n_tickets.data

	# check the reservation first
	reservation = model.reservation_find(g.db_cursor, form.email.data)
	print "found reservation: {0!r}".format(reservation)
	if not reservation['available_from'] <= datetime.datetime.utcnow():
		# not so fast
		time_to_go = reservation['available_from'] - datetime.datetime.utcnow()
		return jsonify(
			status='FAIL',
			message=u"U kan slechts reserveren vanaf {0} UTC, probeer nogmaals over {1} seconden!".format(reservation['available_from'], int(time_to_go.total_seconds())))

	# check the voucher first
	voucher_codes = []
	for i in range(5):
		voucher_codes.append(getattr(form, "voucher_code_{0}".format(i)).data)
	voucher_codes = filter(lambda x: len(x) > 0, voucher_codes)
	print "voucher_codes={0}".format(voucher_codes)
	#voucher = model.voucher_find(g.db_cursor, form.voucher_code_0.data)
	#print "found voucher: {0!r}".format(voucher)

	# validate the dynamic part
	individual_form = make_form_individual_tickets(n_tickets)()
	if not individual_form.validate_on_submit():
		# did not validate OK
		return jsonify(
			status='FAIL',
			message=u"Het formulier is niet volledig!")

	# the dynamic part of the form validated as well, get out all the data
	# and write to database
	products, contains_billables  = extract_products(g.db_cursor, form, individual_form)
	print "products={0!r}".format(products)
	business_form = None
	if contains_billables:
		# one or more of the products are billable, validate business info
		business_form = BusinessForm()
		if not business_form.validate_on_submit():
			# business form parse failed
			return jsonify(
				status='FAIL',
				message=u"De zakelijke details zijn niet volledig!")

	billing_info = extract_billing_info(business_form)
	general_ticket_info = extract_general_ticket_info(individual_form)

	# create it all
	queued = True if tickets_available < n_tickets else False
	purchase = model.purchase_create(g.db_cursor, form.email.data, voucher_codes, products, billing_info, general_ticket_info, queued)

	# get the prices back (includes voucher discounts, volunteering discounts, ...)
	price_normal, price_billable = price_distribution_strategy(g.db_cursor, purchase['nonce'])
	price_total = price_normal + price_billable

	model.purchase_history_append(g.db_cursor, purchase['id'],
		msg='created purchase for={0} n_tickets={1} total={2}'.format(form.email.data, n_tickets, price_total))

	mail_data = {
		'amount' : price_total,
		'days_max' : app.config['DAYS_MAX'],
		'email' : form.email.data,
		'payment_code' : prettify_purchase_code(purchase['payment_code']),
		'payment_account' : app.config['OUR_BANK_ACCOUNT'],
		'email' : form.email.data,
	}

	if form.email.data[-len('.notreal'):] != '.notreal':
		if not queued:
			mail.send_mail(
				from_addr=app.config['MAIL_MY_ADDR'],
				to_addrs=[ form.email.data, app.config['MAIL_CC_ADDR'] ],
				subject=texts['MAIL_TICKETS_ORDERED_OK_SUBJECT'],
				msg_html=texts['MAIL_TICKETS_ORDERED_OK_HTML'].format(**mail_data),
				msg_text=texts['MAIL_TICKETS_ORDERED_OK_TEXT'].format(**mail_data))
			model.purchase_history_append(g.db_cursor, purchase['id'],
				msg='mailed ok-please-pay to {0}'.format(form.email.data))
		else:
			mail.send_mail(
				from_addr=app.config['MAIL_MY_ADDR'],
				to_addrs=[ form.email.data, app.config['MAIL_CC_ADDR'] ],
				subject=texts['MAIL_TICKETS_ORDERED_QUEUE_SUBJECT'],
				msg_html=texts['MAIL_TICKETS_ORDERED_QUEUE_HTML'].format(**mail_data),
				msg_text=texts['MAIL_TICKETS_ORDERED_QUEUE_TEXT'].format(**mail_data))
			model.purchase_history_append(g.db_cursor, purchase['id'],
				msg='mailed ok-queued to {0}'.format(form.email.data))
		if not queued:
			mail.send_notif("new registration: {0} bought {1} tickets, total sold now {2}".format(form.email.data, n_tickets, n_tickets + tickets_total_sold))
		else:
			mail.send_notif("new registration: {0} bought {1} QUEUED tickets, total sold now {2}".format(form.email.data, n_tickets, n_tickets + tickets_total_sold))

	g.db_commit = True

	# smashing!
	return jsonify(
		status='SUCCESS',
		redirect=url_for('confirm', nonce=purchase['nonce']))

@app.route('/confirm/<nonce>', methods=[ 'GET' ])
@req_auth_public
def confirm(nonce=None):
	price_normal, price_billable = price_distribution_strategy(g.db_cursor, nonce)
	purchase = model.purchase_get(g.db_cursor, nonce=nonce)
	model.purchase_history_append(g.db_cursor, purchase['id'],
			msg='confirmed to {0}'.format(purchase['email']))
	return render_template('confirm.html',
			queued=purchase['queued'],
			price_total=price_normal + price_billable,
			price_billable=price_billable,
			payment_code=prettify_purchase_code(purchase['payment_code']),
			email=purchase['email'],
			payment_account=app.config['OUR_BANK_ACCOUNT'],
			days_max=app.config['DAYS_MAX'])

@app.route('/admin/payments', methods=[ 'GET' ])
@req_auth_admin
def payments():
	now = datetime.datetime.utcnow()
	time_delta = datetime.timedelta(days=app.config['DAYS_MAX'])

	p = map(dict, model.get_purchases(g.db_cursor, strip_removed=False))
	tickets_total = model.tickets_actual_total(g.db_cursor)
	tickets_available = app.config['TICKETS_MAX'] - tickets_total
	tickets_available_dequeueing = tickets_available
	purchases_dequeueable = 0

	considering_dequeue = True
	tickets_queued = 0
	for x in p:
		x['created_at'] = x['dequeued_at'] if x['dequeued_at'] else x['created_at']
		if not x['paid'] and not x['removed'] and (x['created_at'] + time_delta) < now:
			x['overtime'] = True
		else:
			x['overtime'] = False

		x['can_dequeue'] = False
		if considering_dequeue and x['queued'] and not x['removed']:
			# encountered a queued one, can we show it as dequeue-able?
			if x['n_tickets'] <= tickets_available_dequeueing:
				x['can_dequeue'] = True
				tickets_available_dequeueing -= x['n_tickets']
				purchases_dequeueable += 1
			else:
				considering_dequeue = False
		if x['queued']:
			tickets_queued += x['n_tickets']

		if x['can_dequeue'] or x['overtime'] or (x['n_billable'] > 0 and not x['billed']):
			x['latent'] = False
		else:
			x['latent'] = True

	return render_template('payments.html',
			tickets_total=tickets_total, tickets_available=tickets_available,
			purchases_dequeueable=purchases_dequeueable, tickets_queued=tickets_queued,
			purchases=p, page_opts={ 'internal' : True })

@app.route('/admin/reservations')
@req_auth_admin
def reservations():
	"""
	build a list of reservations, return
	"""
	r = model.reservation_get(g.db_cursor)
	return render_template('reservations.html', reservations=r,
			page_opts={
				'internal' : True
			})

@app.route('/admin/reservation_delete/<int:id>')
@req_auth_admin
def reservation_delete(id):
	"""
	delete a reservation based on id
	"""
	model.reservation_delete(g.db_cursor, id=id)
	g.db_commit = True
	return redirect(url_for('reservations'))

class ReservationForm(Form):
	"""
	reservation manipulation form
	"""
	email = EmailField('Email address', validators=[
		validators.Email(message="Really an email?"),
		])
	available_from = DateTimeField('Can be used from (UTC)', format='%Y-%m-%d %H:%M:%S', validators=[
		validators.Required('Had trouble parsing this date.'),
		])
	claimed = BooleanField('Has been claimed')
	claimed_at = DateTimeField('Was claimed at (UTC)', format='%Y-%m-%d %H:%M:%S', validators=[
		validators.Optional(),
		])
	comments = TextAreaField('Internal comments', validators=[
		validators.Optional(),
		])

@app.route('/admin/reservation_edit/<int:id>', methods=[ 'GET', 'POST'])
@req_auth_admin
def reservation_edit(id):
	"""
	overwrite reservation by id
	"""
	form = ReservationForm()
	if form.validate_on_submit():
		# form validated, pack and save
		changeset = {
			'email' : form.email.data,
			'available_from' : form.available_from.data,
			'claimed' : bool(form.claimed.data),
			'claimed_at' : form.claimed_at.data or None,
			'comments' : form.comments.data,
		}
		model.reservation_update(g.db_cursor, id, changeset)
		g.db_commit = True
		# back to list
		return redirect(url_for('reservations'))
	# no form entry or bad validation, show form
	res = map(dict, model.reservation_get(g.db_cursor, id))
	for r in res:
		r['claimed'] = bool(r['claimed'])
	return render_template('reservation_edit.html', reservation=res[0],
			form=form,
			page_opts={
				'internal' : True
			},
			form_dest=url_for('reservation_edit', id=id))

@app.route('/admin/reservation_add', methods=[ 'GET', 'POST'])
@req_auth_admin
def reservation_add():
	"""
	add a reservation
	"""
	form = ReservationForm()
	if form.validate_on_submit():
		# form validated, pack and save
		changeset = {
			'email' : form.email.data,
			'available_from' : form.available_from.data,
			'claimed' : bool(form.claimed.data),
			'claimed_at' : form.claimed_at.data or None,
			'comments' : form.comments.data,
		}
		reservation = model.reservation_create(g.db_cursor, changeset)
		g.db_commit = True
		# back to list
		return redirect(url_for('reservations'))
	# no form entry or bad validation, show the form, we use the
	# always-existing "default" reservation (used when no specific hit
	# was found) as a template, and substract a week since the caller
	# will likely want to make a prereservation
	default_id = model.reservation_find(g.db_cursor, 'default')['id']
	default_r = dict(model.reservation_get(g.db_cursor, default_id)[0])
	default_r['email'] = u''
	default_r['available_from'] -= datetime.timedelta(weeks=1)
	default_r['claimed'] = False #bool(default_r['claimed'])
	default_r['claimed_at'] = ""
	return render_template('reservation_edit.html', reservation=default_r,
			form=form,
			page_opts={
				'internal' : True
			},
			form_dest=url_for('reservation_add', id=id))

@app.route('/admin/vouchers')
@req_auth_admin
def vouchers():
	"""
	build a list of vouchers, return
	"""
	r = model.voucher_get(g.db_cursor)
	return render_template('vouchers.html', vouchers=r,
			page_opts={
				'internal' : True
			})

@app.route('/admin/voucher_delete/<int:id>')
@req_auth_admin
def voucher_delete(id):
	"""
	delete a voucher based on id
	"""
	model.voucher_delete(g.db_cursor, id=id)
	g.db_commit = True
	return redirect(url_for('vouchers'))

class VoucherForm(Form):
	"""
	voucher manipulation form
	"""
	discount = IntegerField(u'Discount on order in €', validators=[
		validators.NumberRange(message='Not a number!', min=0),
		])
	#available_from = DateTimeField('Can be used from (UTC)', format='%Y-%m-%d %H:%M:%S', validators=[
	#	validators.Required('Had trouble parsing this date.'),
	#	])
	claimed = BooleanField('Has been claimed')
	claimed_at = DateTimeField('Was claimed at (UTC)', format='%Y-%m-%d %H:%M:%S', validators=[
		validators.Optional(),
		])
	comments = TextAreaField('Internal comments', validators=[
		validators.Optional(),
		])

@app.route('/admin/voucher_edit/<int:id>', methods=[ 'GET', 'POST'])
@req_auth_admin
def voucher_edit(id):
	"""
	overwrite voucher by id
	"""
	form = VoucherForm()
	if form.validate_on_submit():
		# form validated, pack and save
		changeset = {
			'discount' : form.discount.data,
			#'available_from' : form.available_from.data,
			'claimed' : bool(form.claimed.data),
			'claimed_at' : form.claimed_at.data or None,
			'comments' : form.comments.data,
		}
		model.voucher_update(g.db_cursor, id, changeset)
		g.db_commit = True
		# back to list
		return redirect(url_for('vouchers'))
	# no form entry or bad validation, show form
	res = map(dict, model.voucher_get(g.db_cursor, id))
	for r in res:
		r['claimed'] = bool(r['claimed'])
	return render_template('voucher_edit.html', voucher=res[0],
			form=form,
			page_opts={
				'internal' : True
			},
			form_dest=url_for('voucher_edit', id=id))

@app.route('/admin/voucher_add', methods=[ 'GET', 'POST'])
@req_auth_admin
def voucher_add():
	"""
	add a voucher
	"""
	form = VoucherForm()
	if form.validate_on_submit():
		# form validated, pack and save
		changeset = {
			'discount' : form.discount.data,
			#'available_from' : form.available_from.data,
			'claimed' : bool(form.claimed.data),
			'claimed_at' : form.claimed_at.data or None,
			'comments' : form.comments.data,
		}
		code = model.voucher_create(g.db_cursor, changeset)
		g.db_commit = True
		# back to list
		return redirect(url_for('vouchers'))
	# no form entry or bad validation, show the form, we use the
	# always-existing "default" voucher (used when no specific hit
	# was found) as a template, and substract a week since the caller
	# will likely want to make a prevoucher
	default_r = model.voucher_find(g.db_cursor, 'none')
	default_r['discount'] = 0
	#default_r['available_from'] -= datetime.timedelta(weeks=1)
	default_r['claimed'] = False #bool(default_r['claimed'])
	default_r['claimed_at'] = ""
	return render_template('voucher_edit.html', voucher=default_r,
			form=form,
			page_opts={
				'internal' : True
			},
			form_dest=url_for('voucher_add', id=id))

@app.route('/admin/overview', methods=[ 'GET' ])
@req_auth_admin
def overview():
	purchases = map(dict, model.get_purchases(g.db_cursor, strip_removed=False))
	tickets_active = map(dict, model.get_stats_tickets(g.db_cursor))
	tickets_queued = map(dict, model.get_stats_tickets(g.db_cursor, queued=1))
	tshirts_active = map(dict, model.get_stats_tshirts(g.db_cursor))
	tshirts_queued = map(dict, model.get_stats_tshirts(g.db_cursor, queued=1))

	stats_purchases = { t :
		{
			'orders' : 0,
			'tickets' : 0,
			'tshirts' : 0,
			'tokens' : 0,
			'money' : 0,
		} for t in [ 'active_paid', 'active_unpaid', 'active_total', 'queued', 'total' ]
	}

	for det in purchases:
		dests = [ 'total' ]
		if det['removed']:
			continue
		if not det['queued']:
			dests.append('active_paid' if det['paid'] else 'active_unpaid')
			dests.append('active_total')
		else:
			dests.append('queued')
		for dest in dests:
			stats_purchases[dest]['tickets'] += det['n_tickets']
			stats_purchases[dest]['tshirts'] += det['n_tshirts']
			stats_purchases[dest]['tokens'] += det['n_tokens']
			stats_purchases[dest]['money'] += det['total_price']
			stats_purchases[dest]['orders'] += 1
	
	for t in stats_purchases:
		for k in stats_purchases[t]:
			stats_purchases[t][k] = int(stats_purchases[t][k])

	tickets_active_total = {}
	tickets_active_total['type'] = 'total active'
	tickets_queued_total = {}
	tickets_queued_total['type'] = 'total queued'
	tickets_total = {}
	tickets_total['type'] = 'total'
	for t in tickets_active:
		for k in t:
			if k[0:len('n_')] == 'n_':
				if k not in tickets_active_total:
					tickets_active_total[k] = 0
				if k not in tickets_total:
					tickets_total[k] = 0
				tickets_active_total[k] += t[k]
				tickets_total[k] += t[k]
			else:
				t[k] = t[k] + ' active'
	tickets_active.append(tickets_active_total)
	for t in tickets_queued:
		for k in t:
			if k[0:len('n_')] == 'n_':
				if k not in tickets_queued_total:
					tickets_queued_total[k] = 0
				if k not in tickets_total:
					tickets_total[k] = 0
				tickets_queued_total[k] += t[k]
				tickets_total[k] += t[k]
			else:
				t[k] = t[k] + ' queued'
	tickets_queued.append(tickets_queued_total)
	tickets = []
	tickets.extend(tickets_active)
	tickets.extend(tickets_queued)
	tickets.append(tickets_total)

	tshirts_active_total = {}
	tshirts_active_total['type'] = 'total active'
	tshirts_queued_total = {}
	tshirts_queued_total['type'] = 'total queued'
	tshirts_total = {}
	tshirts_total['type'] = 'total'
	for t in tshirts_active:
		for k in t:
			if k[0:len('n_')] == 'n_':
				if k not in tshirts_active_total:
					tshirts_active_total[k] = 0
				if k not in tshirts_total:
					tshirts_total[k] = 0
				tshirts_active_total[k] += t[k]
				tshirts_total[k] += t[k]
			else:
				t[k] = t[k] + ' active'
	tshirts_active.append(tshirts_active_total)
	for t in tshirts_queued:
		for k in t:
			if k[0:len('n_')] == 'n_':
				if k not in tshirts_queued_total:
					tshirts_queued_total[k] = 0
				if k not in tshirts_total:
					tshirts_total[k] = 0
				tshirts_queued_total[k] += t[k]
				tshirts_total[k] += t[k]
			else:
				t[k] = t[k] + ' queued'
	tshirts_queued.append(tshirts_queued_total)
	tshirts = []
	tshirts.extend(tshirts_active)
	tshirts.extend(tshirts_queued)
	tshirts.append(tshirts_total)

	return render_template('overview.html',
		purchases=stats_purchases,
		tickets=tickets,
		tshirts=tshirts,
		page_opts={
			'charting' : True,
			'internal' : True})

@app.route('/admin/volunteering', methods=[ 'GET' ])
@req_auth_admin
def volunteering():
	when = model.get_volunteering_times(g.db_cursor)
	what = model.get_volunteering_posts(g.db_cursor)
	volunteers = model.get_volunteers(g.db_cursor)
	sched = model.get_volunteering_schedule(g.db_cursor)
	purchases = model.get_volunteer_purchases(g.db_cursor)

	shifts = {
		'total' : 0,
		'complete' : 0,
	}
	slots = {
		'total' : 0,
		'complete' : 0
	}
	for t in sched:
		for p in sched[t]:
			s = sched[t][p]
			shifts['total'] += 1
			if s['people_present'] >= s['people_needed']:
				shifts['complete'] += 1

			slots['total'] += s['people_needed']
			slots['complete'] += s['people_present']

	volunteer_purchases = { 'total' : 0, 'complete' : 0 }
	volunteer_tickets = { 'total' : 0, 'complete' : 0 }
	for p in purchases:
		volunteer_tickets['total'] += p['n_volunteers']
		volunteer_purchases['total'] += 1
		if p['n_volunteers'] <= p['shifts_booked']:
			volunteer_purchases['complete'] += 1
			volunteer_tickets['complete'] += p['n_volunteers']

	return render_template('volunteers_admin.html', page_opts={ 'internal' : True},
		volunteers=volunteers, sched=sched, purchases=purchases, when=when,
		what=what, volunteer_purchases=volunteer_purchases,
		volunteer_tickets=volunteer_tickets, shifts=shifts, slots=slots)

@app.route('/admin/api/purchase_mark_paid/<int:purchase_id>/<int:paid>', methods=[ 'GET' ])
@req_auth_admin
def api_purchase_mark_paid(purchase_id, paid):
	model.purchase_mark_paid(g.db_cursor, purchase_id, paid)

	model.purchase_history_append(g.db_cursor, purchase_id, msg='set paid={0}'.format(paid))

	if paid:
		purchase = model.purchase_get(g.db_cursor, id=purchase_id)
		email = purchase['email']

		mail_data = { 'email' : email }
		if email[-len('.notreal'):] != '.notreal':
			mail.send_mail(
				from_addr=app.config['MAIL_MY_ADDR'],
				to_addrs=[ email, app.config['MAIL_CC_ADDR'] ],
				subject=texts['MAIL_PAYMENT_RECEIVED_SUBJECT'],
				msg_html=texts['MAIL_PAYMENT_RECEIVED_HTML'].format(**mail_data),
				msg_text=texts['MAIL_PAYMENT_RECEIVED_TEXT'].format(**mail_data))
		model.purchase_history_append(g.db_cursor, purchase['id'], msg='mailed purchase-paid to {0}'.format(email))
		mail.send_notif("payment received for registration: {0}".format(email))

	g.db_commit = True
	return "ok", 200

@app.route('/admin/api/purchase_mark_removed/<int:purchase_id>/<int:removed>', methods=[ 'GET' ])
@req_auth_admin
def api_purchase_mark_removed(purchase_id, removed):
	model.purchase_mark_removed(g.db_cursor, purchase_id, removed)

	model.purchase_history_append(g.db_cursor, purchase_id, msg='set removed={0}'.format(removed))

	if removed:
		purchase = model.purchase_get(g.db_cursor, id=purchase_id)
		email = purchase['email']
		mail_data = {
			'days_max' : app.config['DAYS_MAX'],
			'email' : email,
		}

		if email[-len('.notreal'):] != '.notreal':
			mail.send_mail(
				from_addr=app.config['MAIL_MY_ADDR'],
				to_addrs=[ email, app.config['MAIL_CC_ADDR'] ],
				subject=texts['MAIL_REMOVED_SUBJECT'],
				msg_html=texts['MAIL_REMOVED_HTML'].format(**mail_data),
				msg_text=texts['MAIL_REMOVED_TEXT'].format(**mail_data))
		model.purchase_history_append(g.db_cursor, purchase['id'], msg='mailed purchase-removed to {0}'.format(email))
		mail.send_notif("removed registration: {0}".format(email))

	g.db_commit = True
	return "ok", 200

@app.route('/admin/api/purchase_mark_billed/<int:purchase_id>/<int:billed>', methods=[ 'GET' ])
@req_auth_admin
def api_purchase_mark_billed(purchase_id, billed):
	model.purchase_mark_billed(g.db_cursor, purchase_id, billed)

	model.purchase_history_append(g.db_cursor, purchase_id, msg='set billed={0}'.format(billed))

	g.db_commit = True
	return "ok", 200

class PurchaseHistoryForm(Form):
	"""
	reservation manipulation form
	"""
	who = StringField('Your name', validators=[
		validators.Required(message="Need this"),
		])
	event = TextAreaField('Comment', validators=[
		validators.Required(message="Need this"),
		])

@app.route('/admin/purchase_view/<int:purchase_id>', methods=[ 'GET', 'POST'])
@req_auth_admin
def purchase_view(purchase_id):
	form = PurchaseHistoryForm()
	if form.validate_on_submit():
		model.purchase_history_append(g.db_cursor, purchase_id, creator=form.who.data,
			msg=form.event.data)
		g.db_commit = True
	purchase = model.purchase_get(g.db_cursor, id=purchase_id)
	items = model.purchase_items_get(g.db_cursor, purchase_id)
	voucher = model.voucher_get(g.db_cursor, purchase['voucher_id'])[0]
	history = model.purchase_history_get(g.db_cursor, purchase_id)
	purchase['payment_code'] = prettify_purchase_code(purchase['payment_code'])
	purchase['created_at'] = purchase['created_at'].isoformat()
	purchase['business_address'] = purchase['business_address'].splitlines()
	voucher['available_from'] = voucher['available_from'].isoformat()
	n_billables = bool(sum([ i['billable'] for i in items ]))
	price_normal, price_billable = price_distribution_strategy(g.db_cursor, purchase['nonce'])
	price_total = price_normal + price_billable
	return render_template('purchase_view.html', items=items, form=form,
			purchase=purchase, voucher=voucher,
			n_billables=n_billables, history=history,
			price_normal=price_normal, price_billable=price_billable, price_total=price_total,
			form_dest=url_for('purchase_view', purchase_id=purchase_id),
			page_opts={
				'internal' : True
			})

@app.route('/admin/api/purchase_mark_dequeued/<int:purchase_id>', methods=[ 'GET' ])
@req_auth_admin
def api_purchase_mark_dequeued(purchase_id):
	model.purchase_mark_dequeued(g.db_cursor, purchase_id)
	purchase = model.purchase_get(g.db_cursor, id=purchase_id)
	email = purchase['email']

	model.purchase_history_append(g.db_cursor, purchase['id'], creator='HUMAN', msg='dequeued')

	price_normal, price_billable = price_distribution_strategy(g.db_cursor, purchase['nonce'])
	price_total = price_normal + price_billable

	mail_data = {
		'amount' : price_total,
		'days_max' : app.config['DAYS_MAX'],
		'email' : email,
		'payment_code' : prettify_purchase_code(purchase['payment_code']),
		'payment_account' : app.config['OUR_BANK_ACCOUNT'],
	}

	if email[-len('.notreal'):] != '.notreal':
		mail.send_mail(
			from_addr=app.config['MAIL_MY_ADDR'],
			to_addrs=[ email, app.config['MAIL_CC_ADDR'] ],
			subject=texts['MAIL_UNQUEUED_SUBJECT'],
			msg_html=texts['MAIL_UNQUEUED_HTML'].format(**mail_data),
			msg_text=texts['MAIL_UNQUEUED_TEXT'].format(**mail_data))
		model.purchase_history_append(g.db_cursor, purchase['id'], msg='mailed purchase-dequeued to {0}'.format(email))
		mail.send_notif("dequeued registration: {0}".format(email))

	g.db_commit = True
	return "ok", 200

@app.route('/api/get_products', methods=[ 'GET' ])
@req_auth_public
def api_get_products():
	products = map(dict, model.products_get(g.db_cursor))
	for p in products:
		if p['max_dob']:
			p['max_dob'] = int(time.mktime(p['max_dob'].timetuple()))
	return json.dumps(products), 200

@app.route('/admin/api/get_timeline_tickets')
@req_auth_admin
def api_get_timeline_tickets():
	timeline_tickets = map(dict, model.get_timeline_tickets(g.db_cursor))

	sum = 0
	for t in timeline_tickets:
		epoch = datetime.datetime(1970, 1, 1)
		when = (t['at'] - epoch).total_seconds()
		t['at'] = int(when)
		sum += int(t['n'])
		t['n'] = sum

	return json.dumps({
		'at' : [ t['at'] for t in timeline_tickets ],
		'n' : [ t['n'] for t in timeline_tickets ]})

@app.route("/api/get_voucher/<code>", methods=[ 'GET' ])
@req_auth_public
def api_get_voucher(code):
	r = model.voucher_find(g.db_cursor, code)
	return json.dumps({
			'code' : r['code'],
			'discount' : r['discount'],
		})

@app.route("/api/get_reservation/<email>", methods=[ 'GET' ])
@req_auth_public
def api_get_reservation(email):
	r = model.reservation_find(g.db_cursor, email)
	return json.dumps({
			'available_from' : r['available_from_unix'],
		})

@app.route("/admin")
@req_auth_admin
def admin():
	return render_template('index.html')

@app.route("/")
@req_auth_public
def index():
	return redirect(url_for('tickets'))

@app.route("/api/set_volunteering_data/<nonce>", methods=[ 'GET', 'POST' ])
def api_set_volunteering_data(nonce):
	purchase = model.purchase_get(g.db_cursor, nonce=nonce)
	if not purchase:
		return json.dumps({ 'status' : 'FAIL', 'msg' : 'Onbekend email of email zonder volunteer-tickets :-('})
	email = purchase['email']
	updates_str = json.loads(request.form.keys()[0])

	# clear our own entries so we don't double-count them
	model.clear_volunteering_schedule(g.db_cursor, email)

	sched = model.get_volunteering_schedule(g.db_cursor)
	volunteers = model.get_volunteers(g.db_cursor, email_filter=email)
	all_shifts = {}
	for time_id in sched:
		for post_id in sched[time_id]:
			s = sched[time_id][post_id]
			all_shifts[s['shift_id']] ={
				'people_needed' : s['people_needed'],
				'people_present' : s['people_present'],
				'time_id' : time_id,
				'post_id' : post_id,
			}

	updates = {}
	for k in updates_str:
		updates[int(k)] = [ int(x) for x in updates_str[k] ]

	D("pre: {0}".format(all_shifts[1]))
	for person, shifts in updates.iteritems():
		if person not in volunteers:
			D('person {0} not in volunteers for email {1}'.format(person, email))
			return jsonify(status='FAIL', msg='one or more persons not reachable')
		for shift in shifts:
			if shift not in all_shifts:
				D('shift {0} not known for email {1}'.format(shift, email))
				return jsonify(status='FAIL', msg='unknown shift referenced')
			D("substracting from shft {0}".format(shift))
			all_shifts[shift]['people_present'] += 1
			D(all_shifts[1])
			if (all_shifts[shift]['people_needed'] - all_shifts[shift]['people_present']) < 0:
				D('overcommited on shift {0} by email {1}'.format(shift, email))
				return jsonify(status='FAIL', msg='overcommited on shift')

	D("post {0}".format(all_shifts[1]))
	for person in volunteers:
		if person not in updates or len(updates[person]) < app.config['VOLUNTEERING_MIN_SHIFTS']:
			D('undercommited for person {0} by email {1}'.format(person, email))
			return jsonify(status='FAIL', msg='not enough shifts entered')

	model.set_volunteering_schedule(g.db_cursor, updates)

	when = model.get_volunteering_times(g.db_cursor)
	what = model.get_volunteering_posts(g.db_cursor)

	mail_schedule = {}
	for person, shifts in updates.iteritems():
		name = volunteers[person]['name']
		mail_schedule[name] = []
		for s in sorted(shifts):
			mail_schedule[name].append((when[all_shifts[s]['time_id']]['name'], what[all_shifts[s]['post_id']]['name']))

	schedule_html = '<ul style="padding: 0; Margin: 0;">'
	schedule_text = ''
	for person in mail_schedule:
		schedule_html += '<li style="Margin: 0;">{0}:<ul>'.format(person)
		schedule_text += '* {0}:\n'.format(person)
		for e in mail_schedule[person]:
			when, what = e
			schedule_html += '    <li>{0}: {1}</li>'.format(when, what)
			schedule_text += '\t- {0}: {1}\n'.format(when, what)
		schedule_html += '</ul></li>'
	schedule_html += '</ul>'

	mail_data = {
		'email' : email,
		'schedule_html' : schedule_html,
		'schedule_text' : schedule_text,
	}
	if email[-len('.notreal'):] != '.notreal':
		mail.send_mail(
			from_addr=app.config['MAIL_MY_ADDR'],
			to_addrs=[ email, app.config['MAIL_CC_ADDR'] ],
			subject=texts['MAIL_VOLUNTEERING_SCHEDULE_SUBJECT'],
			msg_html=texts['MAIL_VOLUNTEERING_SCHEDULE_HTML'].format(**mail_data),
			msg_text=texts['MAIL_VOLUNTEERING_SCHEDULE_TEXT'].format(**mail_data))
		model.purchase_history_append(g.db_cursor, purchase['id'], msg='mailed volunteering-schedule-updated to {0}'.format(email))
		mail.send_notif("updated volunteering schedule: {0}".format(email))

	g.db_commit = True
	return jsonify(status='OK')

@app.route("/api/get_volunteering_data/<nonce>", methods=[ 'GET' ])
def api_get_volunteering_data(nonce):
	purchase = model.purchase_get(g.db_cursor, nonce=nonce)
	if not purchase:
		return json.dumps({ 'status' : 'FAIL', 'msg' : 'Onbekend email of email zonder volunteer-tickets :-('})
	email = purchase['email']
	when = model.get_volunteering_times(g.db_cursor)
	what = model.get_volunteering_posts(g.db_cursor)
	sched = model.get_volunteering_schedule(g.db_cursor)
	volunteers_all = model.get_volunteers(g.db_cursor)
	volunteers_mine = model.get_volunteers(g.db_cursor, email_filter=email)
	volunteers = {
		'all' : volunteers_all,
		'mine' : volunteers_mine.keys()
	}

	if not len(volunteers_mine):
		return json.dumps({ 'status' : 'FAIL', 'msg' : 'Onbekend email of email zonder volunteer-tickets :-('})

	def anonymize(name):
		t = name.strip().split(' ')
		if len(t) > 1:
			return "{0} {1}".format(t[0], ''.join([ i[0] for i in t[1:] ]))
		else:
			return name
	for v in volunteers_all:
		if v not in volunteers_mine:
			volunteers_all[v]['name'] = anonymize(volunteers_all[v]['name'])
			del volunteers_all[v]['email']

	return json.dumps({ 'status': 'OK',
		'times' : when,
		'posts' : what,
		'sched' : sched,
		'volunteers' : volunteers,
	})

class VolunteersLaunchForm(Form):
	"""
	takes an email, launch to correct volunteering page
	"""
	email = EmailField('Email address', validators=[
		validators.Email(message="Really an email?"),
		])

@app.route("/volunteers", methods=[ 'GET', 'POST' ])
def volunteers_launch():
	form = VolunteersLaunchForm()
	if form.validate_on_submit():
		purchase = model.purchase_get(g.db_cursor, email=form.email.data)
		if purchase:
			return redirect(url_for('volunteers', nonce=purchase['nonce']))
	if request.method == 'POST':
		return render_template('volunteers_launchpad.html', form=form, badentry=True)
	return render_template('volunteers_launchpad.html', form=form)

@app.route("/volunteers/<nonce>")
def volunteers(nonce=None):
	return render_template('volunteers.html', page_opts={ 'shift' : True})
