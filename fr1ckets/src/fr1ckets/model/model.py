from fr1ckets import app
import string
import random
import datetime
import copy
import MySQLdb

D = app.logger.debug

def random_string(length=32):
	return ''.join(
		[ random.SystemRandom().choice(
				string.ascii_lowercase +
				string.ascii_uppercase + string.digits)
			for _ in range(length)
		])

def random_voucher(length=10):
	return ''.join(
		[ random.SystemRandom().choice(string.ascii_uppercase)
			for _ in range(length)
		])

def voucher_find(cursor, code):
	"""
	find any unclaimed voucher with this code, if none is found we return
	the default voucher

	the timezone stuff is ugly, but mysql happily returns
	"""
	q = "SET @@session.time_zone='+00:00';"
	cursor.execute(q)
	q = """
		select
			id,
			code,
			discount,
			reason
		from
			voucher
		where
			code = %(code)s
			and claimed = 0;
		"""
	qd = { 'code' : code}

	cursor.execute(q, qd)
	rs = cursor.fetchall()

	return rs[0] if len(rs) > 0 else {
		'id' : None,
		'code' : 'none',
		'discount' : 0,
		'reason' : '',
	}

def voucher_claim(cursor, code, purchase_id):
	res = voucher_find(cursor, code)
	if not res['id']:
		return

	q = """
		update
			voucher
		set
			claimed = 1,
			claimed_at = utc_timestamp(),
			purchase_id = %(purchase_id)s
		where
			code = %(code)s
			AND claimed = 0;
		"""
	qd = {
		'code' : code,
		'purchase_id' : purchase_id,
	}

	cursor.execute(q, qd)
	return res

def voucher_get(cursor, id=None):
	f = ""
	if id:
		f = " where id=%(id)s"
	q = """
		select
			id,
			code,
			discount,
			claimed,
			claimed_at,
			comments,
			reason
		from
			voucher
		""" + f + ";"
	cursor.execute(q, { 'id' : id })
	return cursor.fetchall()

def vouchers_for_purchase(cursor, purchase_id):
	q = """
		select
			id,
			code,
			discount,
			claimed,
			claimed_at,
			comments,
			reason
		from
			voucher
		where
			purchase_id = %(purchase_id)s;"""
	cursor.execute(q, { 'purchase_id' : purchase_id })
	return cursor.fetchall()

def voucher_delete(cursor, id):
	q = """
		delete from
			voucher
		where
			id=%(id)s
			AND code != 'default';
		"""
	cursor.execute(q, { 'id' : id })

def voucher_update(cursor, id, values):
	q = """
		update
			voucher
		set
			discount=%(discount)s,
			claimed=%(claimed)s,
			claimed_at=%(claimed_at)s,
			comments=%(comments)s,
			reason=%(reason)s
		where
			id=%(id)s;
		"""
	qd = copy.deepcopy(values)
	qd['id'] = id
	cursor.execute(q, qd)

def voucher_create(cursor, values):
	q = """
		insert into
			voucher (
				code,
				discount,
				claimed,
				claimed_at,
				comments,
				reason
			)
		values (
			%(code)s,
			%(discount)s,
			%(claimed)s,
			%(claimed_at)s,
			%(comments)s,
			%(reason)s
		);
		"""
	code = random_voucher()
	qd = copy.deepcopy(values)
	qd['code'] = code
	cursor.execute(q, qd)
	return code

def reservation_find(cursor, email):
	"""
	find any unclaimed reservation with this email, if none is found we return
	the default reservation

	the timezone stuff is ugly, but mysql happily returns
	"""
	q = "SET @@session.time_zone='+00:00';"
	cursor.execute(q)
	q = """
		select
			id,
			email,
			unix_timestamp(available_from) as available_from_unix,
			available_from
		from
			reservation
		where
			email = %(email)s
			and claimed = 0;
		"""
	qd = { 'email' : email }
	
	cursor.execute(q, qd)
	rs = cursor.fetchall()

	if len(rs) != 1 and email != 'default':
		return reservation_find(cursor, 'default')

	return rs[0]

def reservation_claim(cursor, email):
	res = reservation_find(cursor, email)

	q = """
		update
			reservation
		set
			claimed = 1,
			claimed_at = utc_timestamp()
		where
			email = %(email)s
			AND claimed = 0
			AND available_from <= utc_timestamp();
		"""
	qd = {
		'email' : email,
	}

	cursor.execute(q, qd)

	return res

def reservation_get(cursor, id=None):
	f = ""
	if id:
		f = " where id=%(id)s"
	q = """
		select
			id,
			email,
			available_from,
			claimed,
			claimed_at,
			comments
		from
			reservation
		""" + f + ";"
	cursor.execute(q, { 'id' : id })
	return cursor.fetchall()

def reservation_delete(cursor, id):
	q = """
		delete from
			reservation
		where
			id=%(id)s
			AND email != 'default';
		"""
	cursor.execute(q, { 'id' : id })

def reservation_update(cursor, id, values):
	q = """
		update
			reservation
		set
			email=%(email)s,
			available_from=%(available_from)s,
			claimed=%(claimed)s,
			claimed_at=%(claimed_at)s,
			comments=%(comments)s
		where
			id=%(id)s;
		"""
	qd = copy.deepcopy(values)
	qd['id'] = id
	cursor.execute(q, qd)

def reservation_create(cursor, values):
	q = """
		insert into
			reservation (
				email,
				available_from,
				claimed,
				claimed_at,
				comments
			)
		values (
			%(email)s,
			%(available_from)s,
			%(claimed)s,
			%(claimed_at)s,
			%(comments)s
		);
		"""
	cursor.execute(q, values)

def generate_payment_code(date):
	"""
	generate a payment code "mDDxxxxxxxcc", prettyfied as
	"+++WWx/xxxx/xxxcc+++", with;
		WW = week in year
		xxxxxxxx = random
		cc = checksum
	"gestructureerde mededeling"-compliant
	"""
	first = date.isocalendar()[1] * 10
	first *= 1000000000

	last = random.randint(0, 99999999) * 100
	
	total = first + last
	check = (total / 100) % 97
	check = check if check else 97
	total += check
	return "{0:012d}".format(total)

def purchase_create(cursor, email, voucher_codes, products, billing_info, general_ticket_info, queued):
	"""
	"""
	now = datetime.datetime.utcnow()
	nonce = random_string(16)

	# get the reservation for this email
	reservation = reservation_claim(cursor, email)

	payment_code = generate_payment_code(now)

	# the purchase proper
	q = """
		insert into purchase (
			email, nonce, reservation_id, created_at, queued,
			business_name, business_address, business_vat,
			payment_code, special_accomodation_needs)
		values
			(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
		"""
	n_tries = 20

	while True:
		"""
		we have randomness in the payment code, should it ever clash, retry
		up to n_tries before finally bugging out (could be another issue)
		"""
		try:
			payment_code = generate_payment_code(now)
			cursor.execute(q, (email, nonce, reservation['id'], now, queued,
				billing_info['name'], billing_info['address'], billing_info['vat'],
				payment_code, general_ticket_info['special_accomodation_needs']))
		except MySQLdb.IntegrityError as e:
			print e
			n_tries -= 1
			if n_tries == 0:
				raise e
			else:
				continue
		finally:
			break

	purchase_id = cursor.lastrowid

	# add the products
	q = """
		insert into purchase_items (
			purchase_id, product_id, n, person_name, person_dob,
			person_volunteers_before, person_volunteers_during, person_volunteers_after,
			person_food_vegitarian)
		values
			(%(purchase_id)s, %(product_id)s, %(n)s, %(person_name)s, %(person_dob)s,
			%(person_volunteers_before)s, %(person_volunteers_during)s, %(person_volunteers_after)s,
			%(person_food_vegitarian)s);
		"""
	for p in products:
		p['purchase_id'] = purchase_id
		cursor.execute(q, p)

	# and claim the vouchers
	for c in voucher_codes:
		voucher_claim(cursor, c, purchase_id)

	out = {}
	out['nonce'] = nonce
	out['payment_code'] = payment_code
	out['id'] = purchase_id

	return out

def purchase_get(cursor, nonce=None, id=None, email=None):
	qf = []
	if nonce:
		qf.append("nonce=%(nonce)s")
	if id:
		qf.append("id=%(id)s")
	if email:
		qf.append("email=%(email)s")

	q = """
		select
			id,
			email,
			special_accomodation_needs,
			reservation_id,
			created_at,
			dequeued_at,
			billed_at,
			queued,
			once_queued,
			business_name,
			business_address,
			business_vat,
			payment_code,
			nonce
		from
			purchase
		where
			""" + " AND ".join(qf) + """;
		"""
	cursor.execute(q, { 'nonce' : nonce, 'id' : id, 'email' : email })
	return cursor.fetchone()

def purchase_items_get(cursor, id):
	q = """
		select
			pr.name as product_name,
			pr.display as product,
			pr.billable as billable,
			pui.n as n,
			round(case
				when
					pui.person_volunteers_during
				then
					pr.volunteering_price
				else
					pr.price
			end, 2) as price_single,
			round(pui.n * (case
				when
					pui.person_volunteers_during
				then
					pr.volunteering_price
				else
					pr.price
			end), 2) as price_total,
			round(pui.n * (case
				when
					pui.person_volunteers_during
				then
					pr.volunteering_price_net
				else
					pr.price_net
			end), 2) as price_net_total,
			round(pui.n * (case
				when
					pui.person_volunteers_during
				then
					pr.volunteering_part_vat_21
				else
					pr.part_vat_21
			end), 2) as part_vat_21_total,
			round(pui.n * pr.part_vat_12, 2) as part_vat_12_total,
			round(pui.n * pr.part_vat_6, 2) as part_vat_6_total,
			round(pui.n * pr.part_vat_0, 2) as part_vat_0_total,
			pui.person_volunteers_before as volunteers_before,
			pui.person_volunteers_during as volunteers_during,
			pui.person_volunteers_after as volunteers_after,
			pui.person_name as person_name,
			pui.person_dob as person_dob,
			pui.person_food_vegitarian as person_vegitarian
		from
			purchase_items pui
			inner join product pr on pui.product_id = pr.id
		where
			pui.purchase_id = %s
		order by
			pr.id;
		"""
	cursor.execute(q, (id,))
	return cursor.fetchall()

def purchase_history_append(cursor, id, creator='SYSTEM', msg=None):
	q = """
		insert into purchase_history (
			purchase_id,
			created_at,
			creator,
			event
		)
		values (
			%(purchase_id)s,
			%(created_at)s,
			%(creator)s,
			%(event)s
		);
		"""
	qd = {
		'purchase_id' : id,
		'created_at' : datetime.datetime.utcnow(),
		'creator' : creator,
		'event' : msg,
	}
	cursor.execute(q, qd)

def purchase_history_get(cursor, id):
	q = """
		select
			created_at,
			creator,
			event
		from
			purchase_history
		where
			purchase_id=%s;
		"""
	cursor.execute(q, (id,))
	return cursor.fetchall()

def products_get(cursor):
	q = """
		select
			id,
			genus,
			species,
			name,
			display,
			price,
			volunteering_price,
			price_net,
			volunteering_price_net,
			part_vat_21,
			volunteering_part_vat_21,
			part_vat_12,
			part_vat_6,
			part_vat_0,
			max_dob,
			billable
		from
			product;
		"""
	cursor.execute(q)
	return cursor.fetchall()

def get_purchase_discount(cursor, nonce):
	q = """
		select
			sum(voucher.discount) as discount
		from
			voucher
			inner join purchase on voucher.purchase_id = purchase.id
		where
			purchase.nonce = %(nonce)s;
		"""
	qd = { 'nonce' : nonce }
	cursor.execute(q, qd)
	rs = cursor.fetchone()
	return float(rs['discount'] or 0)

def get_purchase_total(cursor, nonce, only_billable=False):
	"""
	get total cost of order id'd by nonce,
	per item we take volunteering_price if any volunteering is done
	(otherwise we take price), and we deduct any discounts
	"""

	f = ''
	if (only_billable):
		f = 'and product.billable = 1'

	q = """
		select
			round(sum(purchase_items.n * (case
				when
					purchase_items.person_volunteers_during
				then
					product.volunteering_price
				else
					product.price
				end)
			), 2)
			as total
		from
			purchase_items
			inner join product on purchase_items.product_id = product.id
			inner join purchase on purchase_items.purchase_id = purchase.id
		where
			purchase.nonce = %(nonce)s {0};
		""".format(f)
	qd = { 'nonce' : nonce }
	cursor.execute(q, qd)
	rs = cursor.fetchone()
	return rs['total'] or 0

def tickets_actual_total(cursor):
	"""
	get the number of tickets we actually expect to attend, meaning
	every ticket not removed or queued
	"""
	q = """
		select
			sum(n) as n_tickets
		from
			purchase_items
			inner join product on purchase_items.product_id = product.id
			inner join purchase on purchase_items.purchase_id = purchase.id
		where
			product.name like 'ticket%' AND
			purchase.removed = 0 and
			purchase.queued = 0;
		"""
	cursor.execute(q)
	rs = cursor.fetchone()
	return rs['n_tickets'] or 0

def get_prices(cursor):
	"""
	get all prices in [ { product_name : price } ]
	"""
	q = """select name, price from product;"""
	cursor.execute(q)
	return cursor.fetchall()

def purchases_get_all(cursor, strip_removed=True, strip_queued=True):
	q = """
		select
			pu.id as id,
			pu.email as email,
			pui.id as person_id,
			pui.person_name as name,
			pui.person_dob as dob,
			(case
				when pui.person_dob <= %(cutoff)s
				then pui.person_volunteers_during
				else 0 end) as volunteer_during,
			pui.person_volunteers_before as volunteer_before,
			pui.person_volunteers_after as volunteer_after,
			pui.person_food_vegitarian as veggy,
			pui.n as n,
			pr.display as what,
			pr.name as product
		from
			purchase pu
			inner join purchase_items pui on pu.id = pui.purchase_id
			inner join product pr on pui.product_id = pr.id
		where
			{0}
		order by
				pu.id, pr.id;
		"""
	qa = {
		'cutoff' : app.config['VOLUNTEERING_CUTOFF_DATE'],
	}
	opt = []
	if strip_removed:
		opt.append(" pu.removed = 0 ")
	if strip_queued:
		opt.append(" pu.queued = 0 ")

	emails = {}

	cursor.execute(q.format(" AND ".join(opt)), qa)

	for r in cursor.fetchall():
		if r['email'] not in emails:
			emails[r['email']] = []
		emails[r['email']].append(dict(r))

	return emails

def get_purchases(cursor, strip_removed=False):
	"""
	get total overview of all purchases in the system, including all types
	of items, optionally culling the removed ones
	"""
	q = """
		select
			pu.id as id,
			pu.nonce as nonce,
			pu.created_at as created_at,
			pu.email as email,
			pu.special_accomodation_needs as special_accomodation_needs,
			pu.payment_code as payment_code,
			pu.paid as paid,
			pu.removed as removed,
			pu.queued as queued,
			pu.once_queued as once_queued,
			pu.billed as billed,
			pu.dequeued_at as dequeued_at,
			pu.billed_at as billed_at,
			round(sum(pui.n * (
				case
				when (pui.person_volunteers_during)
				then pr.volunteering_price
				else pr.price
				end)
			), 2) - ifnull(v.total_discount, 0) as total_price,
			round(sum(
				case
				when pr.name like 'ticket%'
				then pui.n
				else 0
				end
			), 2) as n_tickets,
			round(sum(
				case
				when pr.name like 'token%'
				then pui.n
				else 0
				end
			), 2) as n_tokens,
			round(sum(
				case
				when pr.name like 'badge_accessory_a%'
				then pui.n
				else 0
				end
			), 2) as n_badge_accessory_a,
			round(sum(
				case
				when pr.name like 'badge_accessory_b%'
				then pui.n
				else 0
				end
			), 2) as n_badge_accessory_b,
			round(sum(
				case
				when pr.name like 'tshirt%'
				then pui.n
				else 0
				end
			), 2) as n_tshirts,
			round(sum(
				case
				when pr.name like 'hoodie%'
				then pui.n
				else 0
				end
			), 2) as n_hoodies,
			round(sum(
				case
				when pr.name like 'mug%'
				then pui.n
				else 0
				end
			), 2) as n_mugs,
			round(sum(
				case
				when pr.name like 'donation%'
				then pui.n
				else 0
				end
			), 2) as n_donations,
			round(sum(
				case
				when pr.name like 'camper_spot%'
				then pui.n
				else 0
				end
			), 2) as n_camper_spots,
			round(sum(
				case
				when pr.billable
				then 1
				else 0
				end
			), 2) as n_billable
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
			left outer join (select sum(discount) as total_discount, purchase_id from voucher group by purchase_id) as v on pui.purchase_id = v.purchase_id
		{0}
		group by
			pu.id, v.total_discount;
		"""
	if strip_removed:
		opt = "where pu.removed = 0"
	else:
		opt = ""
	cursor.execute(q.format(opt))
	rs = cursor.fetchall()
	return rs

def get_overview_something(cursor, what):
	"""
	get an overview of tickets/tshirts/... along with
	how many of them were purchased
	"""
	q = """
		select
			pr.name name,
			sum(pi.n) n
		from
			purchase_items pi
			inner join product pr on pi.product_id = pr.id
			inner join purchase pu on pi.purchase_id = pu.id
		where
			pr.name like '{0}%' and
			pu.removed = 0
		group by pr.name;"""
	cursor.execute(q.format(what))
	return cursor.fetchall()

def get_overview_tickets(cursor):
	return get_overview_something(cursor, 'ticket')

def get_overview_tshirts(cursor):
	return get_overview_something(cursor, 'tshirt')

def get_overview_tokens(cursor):
	return get_overview_something(cursor, 'token')

def get_timeline_something(cursor, what):
	"""
	get a timeline of tickets/tshirts/... on a timeline of
	{ 'at' : timestamp_of_order, 'n' : how_many_ordered }
	"""
	q = """
		select
			pu.created_at at,
			sum(pi.n) n
		from
			purchase pu
			inner join purchase_items pi on pu.id = pi.purchase_id
			inner join product pr on pi.product_id = pr.id
		where
			pu.removed=0 and
			pr.name like '{0}%'
		group by pu.created_at, pr.name
		order by pu.created_at, pr.name asc;"""
	cursor.execute(q.format(what))
	return cursor.fetchall()

def get_timeline_tickets(cursor):
	return get_timeline_something(cursor, 'ticket')

def get_timeline_tshirts(cursor):
	return get_timeline_something(cursor, 'tshirt')


def purchase_mark_paid(cursor, purchase_id, paid):
	"""mark a purchase as being paid"""
	q = "update purchase set paid = %(paid)s, paid_at = %(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow(), 'paid' : paid })

def purchase_mark_billed(cursor, purchase_id, billed):
	"""mark a purchase as being billed"""
	q = "update purchase set billed = %(billed)s, billed_at = %(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow(), 'billed' : billed })

def purchase_mark_removed(cursor, purchase_id, removed):
	"""mark a purchase as being removed"""
	q = "update purchase set removed=%(removed)s, removed_at=%(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow(), 'removed' : removed })

def purchase_mark_dequeued(cursor, purchase_id):
	"""mark a purchase as being removed"""
	q = "update purchase set queued=0, once_queued=1, dequeued_at=%(now)s where id = %(purchase_id)s;"
	cursor.execute(q, { 'purchase_id' : purchase_id, 'now' : datetime.datetime.utcnow() })

def get_volunteering_times(cursor):
	out = {}

	q = """
		select
			id,
			description as name,
			day as day
		from
			shift_time
		order by id;
		"""

	cursor.execute(q)
	for r in cursor.fetchall():
		out[r['id']] = { 'name' : r['name'], 'day' : r['day'], 'index' : r['id'] }
	return out

def get_volunteering_posts(cursor):
	out = {}

	q = """
		select
			id,
			what as name,
			description as `desc`
		from
			shift_post
		order by id;
		"""

	cursor.execute(q)
	for r in cursor.fetchall():
		out[r['id']] = { 'name' : r['name'], 'desc' : r['desc'] }
	return out

def get_volunteering_schedule(cursor):
	"""return the full volunteering schedule, with the number of needed persons per shift"""
	out = {}

	q = """
		select
			s.id as shift_id,
			st.id as shift_time_id,
			sp.id as shift_post_id,
			sp.what as what,
			s.persons as people_needed,
			sv.purchase_item_id people_present
		from
			shift s
			inner join shift_time st on s.shift_time_id = st.id
			inner join shift_post sp on s.shift_post_id = sp.id
			left outer join shift_volunteer sv on s.id = sv.shift_id
			left outer join purchase_items pui on sv.purchase_item_id = pui.id
			left outer join purchase pu on pui.purchase_id = pu.id
		group by s.id, st.id, sp.id, sv.purchase_item_id
		order by s.id, st.id, sp.id, sv.purchase_item_id;
		"""

	cursor.execute(q)
	ret = cursor.fetchall()

	for r in ret:
		st_id = r['shift_time_id']
		sp_id = r['shift_post_id']

		if st_id not in out:
			out[st_id] = {}
		if sp_id not in out[st_id]:
			out[st_id][sp_id] = {
				'people_needed' : r['people_needed'],
				'people_present' : 0,
				'people_list' : [],
				'shift_id' : r['shift_id']
			}
		if r['people_present']:
			out[st_id][sp_id]['people_list'].append(r['people_present'])
			out[st_id][sp_id]['people_present'] += 1

	return out

def set_volunteering_schedule(cursor, updates):
	"""
	update the shift schedule by registering the given { person_id : [ shift_ids ] }
	"""

	q = """
		insert into shift_volunteer
			( purchase_item_id, shift_id )
		values
			( %s, %s );
		"""

	for person_id in updates:
		for shift_id in updates[person_id]:
			cursor.execute(q, (person_id, shift_id))

def clear_volunteering_schedule(cursor, email):
	"""
	clear all volunteering schedule entries for tickets owned by this email
	"""

	q = """
		delete from
			shift_volunteer
		where
			purchase_item_id in (%s);
		"""
	ids = get_volunteers(cursor, email)
	q = q % ','.join(['%s'] * len(ids))
	cursor.execute(q, tuple(ids))

def get_stats_tickets(cursor, removed=0, queued=0):
	q = """
		select
			pr.name as type,
			pr.display as display,
			pr.price as price_premium,
			pr.volunteering_price as price_volunteering,
			sum(pui.n) as n_total,
			sum(case
				when pui.person_dob >= %(cutoff)s
				then 0
				else pui.person_volunteers_during
				end
			) as n_volunteers_during,
			sum(case
				when pui.person_dob >= %(cutoff)s
				then 1
				else
					case
					when pui.person_volunteers_during = 1
					then 0
					else 1
					end
				end
			) as n_premium,
			sum(case
				when pui.person_dob >= %(cutoff)s
				then 0
				else pui.person_volunteers_after
				end
			) as n_volunteers_after,
			sum(case
				when pui.person_dob >= %(cutoff)s
				then 0
				else pui.person_volunteers_before
				end
			) as n_volunteers_before,
			sum(case
				when pui.person_food_vegitarian
				then 1
				else 0
				end
			) as n_vegetarian
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
		where
			pr.name like 'ticket%%'
			and pu.removed = %(removed)s
			and pu.queued = %(queued)s
		group by
			pr.name, pr.display, pr.price, pr.volunteering_price;
		"""
	qd = {
		'removed' : removed,
		'queued' : queued,
		'cutoff' : app.config['VOLUNTEERING_CUTOFF_DATE'],
	}

	cursor.execute(q, qd)
	return cursor.fetchall()

def get_stats_generic(cursor, what, removed=0, queued=0):
	q = """
		select
			pr.name as type,
			sum(pui.n) as n_total
		from
			purchase_items pui
			inner join purchase pu on pui.purchase_id = pu.id
			inner join product pr on pui.product_id = pr.id
		where
			pr.name like '"""+what+"""%%'
			and pu.removed = %(removed)s
			and pu.queued = %(queued)s
		group by
			pr.name;
		"""
	qd = {
		'removed' : removed,
		'queued' : queued,
		'what' : what,
	}

	cursor.execute(q, qd)
	return cursor.fetchall()

def get_volunteers(cursor, email_filter=None):
	"""return all volunteering tickets bought by this email"""
	out = {}
	f = ''
	if email_filter is not None:
		f = 'pu.email = %(email)s and'

	q = """
		select
			pu.email as email,
			pui.person_name as volunteer_name,
			pui.id as volunteer_id
		from
			purchase pu
			inner join purchase_items pui on pu.id = pui.purchase_id
			inner join product pr on pui.product_id = pr.id
		where
			""" + f + """
			pu.removed = 0
			and pu.queued = 0
			and pui.person_volunteers_during = 1
			and pui.person_dob <= %(cutoff)s
			and pr.name like 'ticket%%';
		"""
	qd = {
		'email' : email_filter,
		'cutoff' : app.config['VOLUNTEERING_CUTOFF_DATE'],
	}

	cursor.execute(q, qd)

	for row in cursor.fetchall():
		out[row['volunteer_id']] = {
			'name' : row['volunteer_name'],
			'email' : row['email'],
		}

	return out

def get_volunteer_purchases(cursor):
	"""
	return an overview of users who bought volunteering tickets, and how
	many shifts they booked
	"""
	q = """
		select
			pu.email as email,
			count(sv.shift_id) as shifts_booked,
			count(distinct pui.id) as n_volunteers
		from
			purchase pu
			inner join purchase_items pui on pu.id = pui.purchase_id
			inner join product pr on pui.product_id = pr.id
			left outer join shift_volunteer sv on pui.id = sv.purchase_item_id
		where
			pu.removed = 0
			and pu.queued = 0
			and pui.person_volunteers_during = 1
			and pui.person_dob <= %(cutoff)s
			and pr.name like 'ticket%%'
		group by
			pu.email;
		"""
	qd = {
		'cutoff' : app.config['VOLUNTEERING_CUTOFF_DATE'],
	}
	cursor.execute(q, qd)
	return cursor.fetchall()

def products_sold(cursor, group_by=['name'], genus=None):
	q = """
		SELECT
			""" + ', '.join([ "pr.{} as {}".format(g, g) for g in group_by ]) + """,
			sum(pui.n) as n_sold,
			sum(pui.n*if(pui.person_volunteers_during=1, pr.volunteering_price, pr.price)) as n_eur_sold,
			sum(if(pu.paid = 1, pui.n, 0)) as n_paid,
			sum(if(pu.paid = 1, pui.n, 0) * if(pui.person_volunteers_during=1, pr.volunteering_price, pr.price)) as n_eur_paid,
			sum(if(pui.person_dob > %(cutoff)s, 1, 0)) as n_too_young,
			sum(if(pui.person_dob <= %(cutoff)s, pui.person_volunteers_during, 0)) as n_volunteers,
			sum(if(pui.person_dob <= %(cutoff)s, if(pui.person_volunteers_during = 1, 0, 1), 0)) as n_premium,
			sum(if(pui.person_dob <= %(cutoff)s, pui.person_volunteers_before, 0)) as n_volunteers_before,
			sum(if(pui.person_dob <= %(cutoff)s, pui.person_volunteers_after, 0)) as n_volunteers_after
		FROM
			product pr
			left outer join purchase_items pui on pr.id = pui.product_id
			left outer join purchase pu on pui.purchase_id = pu.id
		""" + ("WHERE genus='{}'".format(genus) if genus else '') + """
		GROUP BY """ + ', '.join([ "pr.{}".format(g) for g in group_by ]) + """
		ORDER BY """ + ', '.join([ "pr.{}".format(g) for g in group_by ]) + """;
		"""
	qd = {
		'cutoff' : app.config['VOLUNTEERING_CUTOFF_DATE'],
	}
	cursor.execute(q, qd)
	return cursor.fetchall()

def list_daemon_days(cursor):
	q = """
		SELECT
			code,
			display,
			day
		FROM
			daemon_day;
		"""

	cursor.execute(q)
	return cursor.fetchall()

def list_daemon_posts(cursor):
	q = """
		SELECT
			code,
			name,
			abstract,
			description
		FROM
			daemon_post;
		"""

	cursor.execute(q)
	return cursor.fetchall()

def list_daemon_slots(cursor, day_code):
	q = """
		SELECT
			ds.id as id,
			ds.daemon_day_code as day,
			ds.daemon_post_code as post,
			ds.slot_start as slot_start,
			ds.slot_end as slot_end,
			ds.n_needed as n_needed,
			COUNT(dc.purchase_items_id) as n_committed
		FROM
			daemon_slot ds
			LEFT OUTER JOIN daemon_commit dc ON ds.id = dc.daemon_slot_id
		WHERE
			ds.daemon_day_code = %(day_code)s
		GROUP BY
			ds.id;
		"""

	cursor.execute(q, {
		'day_code' : day_code,
	})
	return cursor.fetchall()

def get_daemon_slots_for_person(cursor, purchase_items_id):

	q = """
		SELECT DISTINCT
			daemon_slot_id as slot_id
		FROM
			daemon_commit
		WHERE
			purchase_items_id = %(purchase_items_id)s;
		"""

	cursor.execute(q, {
		'purchase_items_id' : purchase_items_id,
	})
	return [ r['slot_id'] for r in cursor.fetchall() ]

def clear_daemon_slots_for_person(cursor, purchase_items_id):

	q = """
		DELETE FROM
			daemon_commit
		WHERE
			purchase_items_id = %(purchase_items_id)s;
		"""
	cursor.execute(q, {
		'purchase_items_id' : purchase_items_id,
	})

def set_daemon_slot_for_person(cursor, purchase_items_id, daemon_slot_id):

	q = """
		INSERT INTO
			daemon_commit
			(daemon_slot_id, purchase_items_id)
		VALUES
			(%(daemon_slot_id)s, %(purchase_items_id)s);
		"""
	cursor.execute(q, {
		'purchase_items_id' : purchase_items_id,
		'daemon_slot_id' : daemon_slot_id,
	})

def get_daemon_overview(cursor):
	q = """
	SELECT
		ds.id as slot_id,
		ds.slot_start as slot_start,
		ds.slot_end as slot_end,	
		ds.daemon_day_code as day_code,
		ds.daemon_post_code as post_code,
		ds.n_needed as n_needed,
		people.person_name as person_name,
		people.order_email as order_email
	FROM
		daemon_slot ds
		LEFT OUTER JOIN (
			SELECT
				dc.daemon_slot_id as slot_id,
				pui.person_name as person_name,
				pu.email as order_email
			FROM 
				daemon_commit dc
				INNER JOIN purchase_items pui ON dc.purchase_items_id = pui.id
				INNER JOIN purchase pu ON pui.purchase_id = pu.id
		) people  ON ds.id = people.slot_id
	ORDER BY ds.slot_start, ds.daemon_post_code;
	"""

	cursor.execute(q)

	out = []
	for row in cursor.fetchall():
		print(row)
		if not len(out) or out[-1]['slot_id'] != row['slot_id']:
			out.append({
				'day_code' : row['day_code'],
				'post_code' : row['post_code'],
				'slot_id' : row['slot_id'],
				'n_needed' : row['n_needed'],
				'slot_start' : row['slot_start'],
				'slot_end' : row['slot_end'],
				'people' : [],
			})
		if row['person_name']:
			out[-1]['people'].append({
				'person_name' : row['person_name'],
				'order_email' : row['order_email'],
			})
	return out

