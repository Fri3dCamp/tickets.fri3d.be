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
import ho.pisa as pisa
from pprint import pprint as D

try:
	app.config.from_pyfile('fr1ckets_priv.conf')
	app.debug = True
	app.secret_key = app.config['SECRET_KEY']
except IOError:
	for i in range(5):
		print "YOU ARE RUNNING THE STOCK CONFIG, which is not in git, smtp passwords and so on, ask jef for fr1ckets_priv.conf"
	app.config.from_pyfile('fr1ckets.conf')


t = """
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
</head>
<style>
@page {
	margin: 2cm;
	margin-bottom: 2.5cm;
	@frame footer {
		-pdf-frame-content: footerContent;
		bottom: 2cm;
		margin-left: 1cm;
		margin-right: 1cm;
		height: 2cm;
	}
}
table, th, td {
	border-bottom: 1px solid #ddd;
	padding-top: 5px;
	font-size: 115%%;
}
.halign {
	text-align: center;
}
.header {
	font-style: italic;
}
.center {
	text-align: center;
}
.biggy {
	font-size: bigger;
}
</style>
<body>
%(entries)s
</body>
</html>
"""

def mk_page(email, d, volunteering):
	o = """
			<meta http-equiv="content-type" content="text/html; charset=utf-8">
			<div style="text-align: center; font-size: 275%%">
				<h1><b>%(email)s %(npers)sp/%(nkids)sk</b></h1>
			</div>
			<div class="halign">
				<h1>Welkom op Fri3dcamp!</h1>
				<h3>Dit is een overzicht van je bestelling.</h3>
			</div>
			%(tickets)s
			<br>
			%(others)s
			<br>
			%(vol)s
			<br>
			<div class="footer">
			%(tips)s
			</div>
			<div><pdf:nextpage /></div>
		"""
	tips_html = ""
	if True:
		tips_html = """
			<p>Nuttige tips:</p>
			<ul>
			<li>Alle praktische info vind je op www.fri3d.be</li>
			<li>Last-minute updates worden verspreid via @fri3dcamp op Twitter, de groep 'Fri3d Camp Deelnemers' op Facebook en het #fri3dcamp IRC-kanaal op freenode</li>
			<li>Vragen? Kom gerust langs de infodesk</li>
			</ul>
		"""
	tickets = [ p for p in d if 'ticket' in p['product'] ]
	others = [ p for p in d if 'ticket' not in p['product'] ]
	volunteers = [ p for p in tickets if p['person_id'] in volunteering ]

	if len(volunteers):
		vol_html = """
		<div id="volunteering">
			<p><b>Volunteering</b> (op {0} UTC):</p>
			<table>
				<tr class="header">
					<td>Naam</td>
					<td>Wanneer</td>
					<td>Wat</td>
				</tr>""".format(str(datetime.datetime.utcnow()).split('.')[0])
		for v in volunteers:
			i = v['person_id']
			for e in volunteering[i]:
				vol_html += """
					<tr>
						<td>{0}</td>
						<td>{1}</td>
						<td>{2}</td>
					</tr>""".format(v['name'].encode('utf-8'), e['when']['name'], e['what']['name'])
		vol_html += "</table></div>"
	else:
		vol_html = ""

	tickets_html = """
	<div id="tickets">
		<p><b>Tickets</b>:</p>
		<table>
			<tr class="header">
				<td>Naam</td>
				<td>Ticket</td>
				<td>Vrijwilliger</td>
			</tr>"""
	for t in tickets:
		volunteer_status = ""
		if t['volunteer_during']:
			if t['person_id'] not in volunteering:
				volunteer_status = '<b><h2>JA MAAR NOG KIEZEN</h2></b>'
			else:
				volunteer_status = "ja"
		tickets_html += """
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
			</tr>""".format(t['name'].encode('utf-8'), t['what'], volunteer_status)
	tickets_html += "</table></div>"
	if len(others):
		others_html = """
		<div id="andere">
			<p><b>Andere</b>:</p>
			<table>
				<tr class="header">
					<td>Item</td>
					<td>Aantal</td>
				</tr>"""
		for t in others:
			if t['what'] == 'dranktoken':
				w = {
					'what' : 'drankkaarten',
					'n' : t['n'] / 10,
				}
			else:
				w = t
			others_html += """
				<tr>
					<td>{0}</td>
					<td>{1}</td>
				</tr>""".format(w['what'], w['n'])
		others_html += "</table></div>"
	else:
		others_html = ""

	return o % {
		'email' : str(email),
		'npers' : len(tickets),
		'nkids' : len([ t for t in tickets if datetime.date(2006, 8, 16) <= t['dob'] ]),
		'tickets' : tickets_html,
		'others' : others_html,
		'vol' : vol_html,
		'tips' : tips_html,
	}

with app.app_context():
	setup.setup_db()
	purchases_all = model.purchases_get_all(g.db_cursor, strip_queued=False)
	when = model.get_volunteering_times(g.db_cursor)
	what = model.get_volunteering_posts(g.db_cursor)
	sched = model.get_volunteering_schedule(g.db_cursor)
	sched_by_person = {}
	for time in sched:
		for post in sched[time]:
			s = sched[time][post]
			for person in s['people_list']:
				if person not in sched_by_person:
					sched_by_person[person] = []
				sched_by_person[person].append({ 'when' : when[time], 'what' : what[post] })

	entries = []
	for email in sorted([ str(e) for e in purchases_all.keys()], key=str.lower):
		for p in purchases_all[email]:
			for k, v in p.iteritems():
				if type(v) == unicode:
					pass
					#p[k] = unicodedata.normalize('NFKD', v).encode('ascii', 'replace')
				#if type(v) in [ unicode, str ]:
				#	p[k] = v.encode('ascii', 'replace')
		entries.append(mk_page(email, purchases_all[email], sched_by_person))
	pdf = pisa.CreatePDF(t % { 'entries' : "".join(entries) }, file('purchases.pdf', 'wb'))
	g.db_commit = True
	setup.wrapup_db(None)
