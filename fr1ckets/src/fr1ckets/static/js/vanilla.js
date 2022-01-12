// this is correct, month is 0-indexed
const volunteering_cutoff = new Date(2006, 7, 12).getTime();
const voucher_cap = 10;
let available_product_descs = [];
let vouchers_current = [];
let n_business_tickets = 0;

/*
                              _          __  __
 _ __   __ _  __ _  ___   ___| |_ _   _ / _|/ _|
| '_ \ / _` |/ _` |/ _ \ / __| __| | | | |_| |_
| |_) | (_| | (_| |  __/ \__ \ |_| |_| |  _|  _|
| .__/ \__,_|\__, |\___| |___/\__|\__,_|_| |_|
|_|          |___/
*/
document.addEventListener('DOMContentLoaded', function(event) {
	var sitebody = document.querySelector("#js_container");
	var warning = document.querySelector("#js_warning");
	sitebody.classList.remove("hidden");
	warning.classList.add("hidden");

	// Open descriptions in modal
	document.querySelectorAll('.js_desclink').forEach(item => {
		item.addEventListener('click', event => {
			event.preventDefault();
			let myhref = event.target.href.split("#");
			let toshow = document.querySelector("#"+myhref[1])
			toshow.classList.remove("visuallyhidden");
			document.querySelector("body").classList.add("noscroll");
		})
	});

	// Open images in modal
	document.querySelectorAll('.js_magnify_image').forEach(item => {
		item.addEventListener('click', event => {
			event.preventDefault();

			let mysrc = event.target.src;
			let myalt = event.target.alt;

			let modal = document.querySelector("#large_image");
			hideclass = modal.getAttribute("data-hideclass");

			modal.querySelector(".image").src = mysrc;
			modal.querySelector(".image").alt = myalt;

			modal.classList.remove(hideclass);
			document.querySelector("body").classList.add("noscroll");
		})
	});

	// Close modal and re-enable scrolling
	document.querySelectorAll('.js_modalclose').forEach(item => {
		item.addEventListener('click', event => { 
			 document.querySelectorAll('.modalwrapper').forEach(wrapper => {
				hideclass = wrapper.getAttribute("data-hideclass");
				wrapper.classList.add(hideclass);
			});
			document.querySelector("body").classList.remove("noscroll");
		});
	});

	// Bestelling nakijken
	document.querySelector("#check_button").addEventListener('click', event => {
		event.preventDefault();

		let validation_errors = [];

		// validation
		if (!document.querySelector('#email').checkValidity())
			validation_errors.push('Het email adres is niet correct ingevuld.');
		if (!document.querySelector('#terms_excellent').checkValidity() ||
			!document.querySelector('#terms_payment').checkValidity() ||
			!document.querySelector('#terms_supervision').checkValidity())
			validation_errors.push('Je bent nog niet akkoord met alle termen.');
		for (let i = 0; i < document.querySelector('#n_tickets').value; i++) {
			let t = resolve_ticket(i);
			if (!t.ok) {
				validation_errors('De ticketgegevens zijn nog niet compleet.');
				break;
			}
		}
		if (validation_errors.length > 0) {
			element_clear_children('#template_dest_baddata');
			validation_errors.forEach((err) => {
				template_add('#template_baddata_item', '#template_dest_baddata', {
					'.error_string' : { textContent : err },
				});
			});
			document.querySelector("#order_baddata").classList.remove("hidden");
			return;
		}

		element_clear_children('#template_dest_overview');
		let items = itemize();
		let total = totalize(items);
		items.forEach(item => {
			template_add('#template_overview_item', '#template_dest_overview', {
				'.item_display' : { textContent : item.display },
				'.item_price' : { textContent : item.price },
				'.item_n' : { textContent : item.n },
				'.item_total' : { textContent : item.total },
			});
		});
		template_add('#template_overview_total', '#template_dest_overview', {
			'.item_total' : { textContent : total },
		});
		document.querySelector("#order_overview").classList.remove("hidden");
	});

	document.querySelector("#overview_order").addEventListener('click', event => {
		event.preventDefault();


		// let's submit this thing. first we serialize the existing form with FormData(),
		// which will fail to notice templated-in inputs, so we add those below
		let form_data = new FormData(document.querySelector('#fr1ckets_form'));

		// loop over tickets, pull in needed bits
		let n_tickets = document.querySelector('#n_tickets').value;
		for (let i = 0; i < n_tickets; i++) {
			let h = 'tickets_' + i;
			[ 'name', 'dob_year', 'dob_month', 'dob_day' ].forEach(k => {
				form_data.append(h + '_' + k, document.querySelector('#' + h + '_' + k).value);
			});
			[ 'billable', 'options_vegitarian', 'options_volunteers_before', 'options_volunteers_after', 'options_not_volunteering_during' ].forEach(k => {
				if (document.querySelector('#' + h + '_' + k).checked)
					form_data.append(h + '_' + k, 'on');
			});
		}

		// business info, if present
		if (n_business_tickets > 0) {
			[ 'name', 'address', 'vat' ].forEach(k => {
				form_data.append('business_' + k, document.querySelector('#business_' + k).value);
			});
		}

		// and all the vouchers
		for (let i = 0; i < vouchers_current.length; i++) {
			form_data.append('voucher_code_' + i, vouchers_current[i].code);
		}

		window.fetch('/api/tickets_register', {
			method : 'POST',
			body : form_data,
		})
		.then(data => data.json())
		.then(res => {
			if (res.status == 'SUCCESS') {
				if (res.redirect) {
					window.location.href = res.redirect;
				}
			} else if (res.status == 'FAIL') {
				element_clear_children('#template_dest_baddata');
				template_add('#template_baddata_item', '#template_dest_baddata', {
					'.error_string' : { textContent : res.message },
				});
				document.querySelector("#order_baddata").classList.remove("hidden");
			}
		})
		.catch(e => {
			let msg = 'Er is een fout opgetreden, waarschijnlijk overbelasting, probeer nog eens.';
			element_clear_children('#template_dest_baddata');
			template_add('#template_baddata_item', '#template_dest_baddata', {
				'.error_string' : { textContent : msg },
			});
			document.querySelector("#order_baddata").classList.remove("hidden");
		});
	});

});


// spin up template #template_id and add it to #dest_parent_id,
// switcheroo is a dict {
//   selector : {
//     prop_name : prop_value,
//     ...
//   },
//   ...
// }
// we'll look for elements with selector within the template,
// and set any prop_name to prop_value
// if new_id is set, we'll set this as id of any element of
// class "template_top"
function template_add(template_id, dest_parent_id, switcheroo, new_id)
{

	let template = document.querySelector(template_id);
	let dest = document.querySelector(dest_parent_id);
	let instance = template.content.cloneNode(true);

	if (switcheroo) {
		Object.keys(switcheroo).forEach(s => {
			instance.querySelectorAll(s).forEach(e => {
				Object.keys(switcheroo[s]).forEach(k => {
                    if ( 'textContent' == k ) {
					    e[k] = switcheroo[s][k];
                    } else {
					    e.setAttribute(k, switcheroo[s][k]);
                    }
					//e[k] = switcheroo[s][k];
				});
			});
		});
	}

	if (new_id) {
		// just setting instance.id doesn't seem to survive the
		// appending, also as appended dest.lastChild, so this
		// ugly hack exists
		instance.querySelector('.template_top').id = new_id;
	}

	dest.appendChild(instance);

}

// remove all of an element's children
function element_clear_children(selector) {
	let parent = document.querySelector(selector);
	while (parent.firstChild) {
		parent.lastChild.remove();
	}
}

// look for the lowest (in age bracket) ticket for this dob
// and billability in the available_product_descs
function ticket_find_for_dob(dob, billable) {

	const ticket_descs = available_product_descs.filter(p => {
		return p.genus == 'ticket' && p.species == 'normal' && p.billable == billable;
	}).sort((left, right) => {
		return right.max_dob - left.max_dob;
	}).filter(t => dob >= t.max_dob);

	return ticket_descs.length ? ticket_descs[0] : null;

}

/* parse the details for the i'th ticket ([0:n_tickets[) and return the
 * cheapest ticket's name and price.
 * assumes there's enough inputs present to get started (name/billable/dob),
 * will calculate premium if that exists too
 * returns {
 * 	'ok' : bool,	// parsed correctly
 * 	'price' : price,
 * 	'display' : prettystring,
 * } */
function resolve_ticket(i) {

	let h = 'tickets_' + i;
	let name = document.querySelector('#' + h + '_name').value;
	let billable = document.querySelector('#' + h + '_billable').checked;
	let dob_year = document.querySelector('#' + h + '_dob_year').value;
	let dob_month = document.querySelector('#' + h + '_dob_month').value;
	let dob_day = document.querySelector('#' + h + '_dob_day').value;

	if (!name.length || !dob_year.length || !dob_month.length || !dob_day.length) {
		return {
			'ok' : false,
			'display' : 'onvolledige ingave',
			'price' : null,
			'can_volunteer' : false,
			'wants_premium' : false,
		};
	}

	// find the relevant ticket for the input entered so far
	let dob = new Date(dob_year, dob_month + 1, dob_day).getTime();
	let ticket_desc = ticket_find_for_dob(dob, billable);
	if (!ticket_desc) {
		return {
			'ok' : false,
			'display' : 'onvolledige ingave',
			'price' : null,
			'can_volunteer' : false,
			'wants_premium' : false,
		};
	}

	// only old enough people can want premium
	let can_volunteer = dob < volunteering_cutoff;
	let wants_premium = false;
	try {
		// input doesn't necessarily exist at this point
		wants_premium = can_volunteer && document.querySelector('#' + h + '_options_not_volunteering_during').checked;
	} catch (e) {
		;
	}

	return {
		'ok' : true,
		'display' : wants_premium ? ticket_desc.display + ' (premium)' : ticket_desc.display,
		'price' : wants_premium ? ticket_desc.price : ticket_desc.volunteering_price,
		'can_volunteer' : can_volunteer,
		'wants_premium' : wants_premium,
	};

}

/*
 _   _      _        _       
| |_(_) ___| | _____| |_ ___ 
| __| |/ __| |/ / _ \ __/ __|
| |_| | (__|   <  __/ |_\__ \
 \__|_|\___|_|\_\___|\__|___/
*/
document.addEventListener('DOMContentLoaded', event => {

	document.querySelector('#n_tickets').value = 0;

	// pull in all products
	window.fetch('/api/get_products')
	.then(data => data.json())
	.then(products => {
		products.forEach(p => {
			p.max_dob *= 1000;
		});
		available_product_descs = products;

		// wire in a total recalculator for every relevant input
		document.querySelectorAll('.fri3d-product').forEach(e => {
			e.value = 0;
			e.addEventListener('change', recalc);
		});

		// and run it once to get a starting total
		recalc();
	});
	
	// check reservations
	let email_input = document.querySelector('#email');
	email_input.addEventListener('input', event => {
		// fixme; debounce
		let val = email_input.value;

		if (!val.length) {
			return;
		}

		window.fetch('/api/get_reservation/' + email_input.value)
		.then(data => data.json())
		.then(reservation => {
			element_clear_children('#reservation_result');
			if (Date.now() < (reservation.available_from*1000)) {
				// this reservation is not yet available
				let s = moment(reservation.available_from*1000).format('YYYY-MM-DD HH:mm:ss');
				template_add('#reservation_result_too_soon', '#reservation_result', {
					'#from_when' : { textContent : s },
				});
			} else if (!reservation.is_default) {
				// it's not the default one, meaning we should inform user of their Special Status
				template_add('#reservation_result_ok_special', '#email_input');
			}
		});
	});

	// show ticket entry upon number choice
	let ticket_chooser = document.querySelector('#n_tickets');
	ticket_chooser.addEventListener('click', event => {
		let n = parseInt(ticket_chooser.value);

        console.log(n);

        if ( 0==1 ) {
            document.querySelector('#js_participants').classList.add('hidden');
        } else {
            document.querySelector('#js_participants').classList.remove('hidden');
        }

		element_clear_children('#template_dest_participants');

		buying_tickets = Array.apply(null, Array(n)).map(() => '');

		// a closure which updates meta for this ticket (options depending on date
		// and billability)
		let update_cb = function(ticket) {
			return function(event) {
				let h = 'tickets_' + ticket;
				let ticket_details = resolve_ticket(ticket);

				element_clear_children('#' + h + '_meta');

				// if the date's empty, we're not happy
				if (!ticket_details.ok) {

					template_add('#template_participant_meta_is_not_human', '#' + h + '_meta');
					return;

				} else {

					// if we actually found a ticket based on date/billability, show the available
					// options

					// add a pricing display block
					template_add('#template_participant_meta_pricing', '#' + h + '_meta', {
						'#tickets_CNT_display_name' : {
							textContent : ticket_details.display,
							id : h + '_display_name',
						},
						'#tickets_CNT_display_price' : {
							textContent : ticket_details.price,
							id : h + '_display_price',
						},
					});
					// and a food questions block
					template_add('#template_participant_meta_food', '#' + h + '_meta', {
                        '[for=tickets_CNT_options_vegitarian]' : { for : h + '_options_vegitarian' },
						'#tickets_CNT_options_vegitarian' : {
							id : h + '_options_vegitarian',
							name : h + '_options_vegitarian',
						}
					});
					// if this person's old enough to volunteer, show the volunteering block
					if (ticket_details.can_volunteer) {
						template_add('#template_participant_meta_is_volunteerable', '#' + h + '_meta', {
                            '[for=tickets_CNT_options_volunteers_before]' : { for : h + '_options_volunteers_before' },
							'#tickets_CNT_options_volunteers_before' : {
								id : h + '_options_volunteers_before',
								name : h + '_options_volunteers_before',
							},
                            '[for=tickets_CNT_options_volunteers_after]' : { for : h + '_options_volunteers_after' },
							'#tickets_CNT_options_volunteers_after' : {
								id : h + '_options_volunteers_after',
								name : h + '_options_volunteers_after',
							},
                            '[for=tickets_CNT_options_not_volunteering_during]' : { for : h + '_options_not_volunteering_during' },
							'#tickets_CNT_options_not_volunteering_during' : {
								id : h + '_options_not_volunteering_during',
								name : h + '_options_not_volunteering_during',
							},
						});

						// another closure which updates this ticket's price to premium/normal,
						// depending on whether they want to help during camp
						let update_pricing_cb = function(ticket) {
							return function(event) {
								let h = 'tickets_' + ticket;
								let el_ticket_price = document.querySelector('#' + h + '_display_price');
								let el_ticket_name = document.querySelector('#' + h + '_display_name');

								// see what this means for pricing, the found details
								// will have premium considered in
								let ticket_details = resolve_ticket(ticket);

								el_ticket_price.textContent = ticket_details.price;
								el_ticket_name.textContent = ticket_details.display;

								recalc();
							};
						};

						// wire in that last one, now that we have the checkbox in DOM
						document.querySelector('#' + h + '_options_not_volunteering_during').addEventListener('change', update_pricing_cb(ticket));
					}

				}

				recalc();

			};
		};


		for (let i = 0; i < n; i++) {
			let new_id = 'tickets_' + i;
			let cb = update_cb(i);

			// throw up a form for this ticket
			template_add('#template_participant', '#template_dest_participants', {
				'[for=tickets_CNT_name]' : { for : new_id + '_name' },
				'[for=tickets_CNT_dob_year]' : { for : new_id + '_dob_year' },
				'[for=tickets_CNT_dob_month]' : { for : new_id + '_dob_month' },
				'[for=tickets_CNT_dob_day]' : { for : new_id + '_dob_day' },
				'[for=tickets_CNT_billable]' : { for : new_id + '_billable' },
				'#tickets_CNT_name' : { id : new_id + '_name', name : new_id + '_name' },
				'#tickets_CNT_dob_year' : { id : new_id + '_dob_year', name : new_id + '_dob_year' },
				'#tickets_CNT_dob_month' : { id : new_id + '_dob_month', name : new_id + '_dob_month' },
				'#tickets_CNT_dob_day' : { id : new_id + '_dob_day', name : new_id + '_dob_day' },
				'#tickets_CNT_billable' : { id : new_id + '_billable', name : new_id + '_billable' },
				'#tickets_CNT_meta' : { id : new_id + '_meta' },
			}, new_id);

			// hook in the update_cb to respond to any changes
			document.querySelector('#' + new_id + '_dob_year').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_dob_month').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_dob_day').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_billable').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_billable').addEventListener('change', (event) => {
				let state = document.querySelector('#' + new_id + '_billable').checked;

				if (state) {
					n_business_tickets++;
					if (n_business_tickets == 1) {
						// first one, show the business entry
						template_add('#template_business', '#template_dest_business');
					}
				} else {
					n_business_tickets--;
					if (n_business_tickets == 0) {
						element_clear_children('#template_dest_business');
					}
				}
			});
		}

	});

});

/*
                       _                   
__   _____  _   _  ___| |__   ___ _ __ ___ 
\ \ / / _ \| | | |/ __| '_ \ / _ \ '__/ __|
 \ V / (_) | |_| | (__| | | |  __/ |  \__ \
  \_/ \___/ \__,_|\___|_| |_|\___|_|  |___/
*/
document.addEventListener('DOMContentLoaded', event => {

	document.querySelector('#have_voucher').checked = false;

	document.querySelector('#have_voucher').addEventListener('change', function(event) {
		let checked = document.querySelector('#have_voucher').checked;

		if (!checked) {
			// disabled, clear everything
			element_clear_children('#voucher_entries');
			vouchers_current = [];
			return;
		}

		// enabled

		// update voucher entry visibility, we show one empty entry after the last
		// filled-in one, up to voucher_cap
		let voucher_peekaboo = function() {

			let last = 0;

			for (last = vouchers_current.length; last > 0; last--)
				if (vouchers_current[last - 1].code != '')
					break;

			for (var i = 0; i < voucher_cap; i++) {
				document.querySelector('#voucher_entry_'+i).hidden = (i < (last + 1)) ? false : true;
			}
		};

		// a voucher had an update, save it for later and check if it's valid, show
		// the relevant outcome too
		let voucher_updates = function(voucher) {
			return function(event) {
				let h = '#voucher_code_' + voucher;
				let v = document.querySelector(h).value;

				vouchers_current[voucher].code = v;

				voucher_peekaboo();

				if (v != '') {
					window.fetch('/api/get_voucher/' + v)
					.then(data => data.json())
					.then(result => {
						// make sure no old messages linger
						element_clear_children('#voucher_entry_' + voucher + '_result');

						if (result.code == 'none') {
							// if it's 'none', server doesn't know it (any more)
							vouchers_current[voucher].reason = 'not found';
							vouchers_current[voucher].discount = 0;

							template_add('#voucher_result_fail', '#voucher_entry_' + voucher + '_result');
						} else if (result.discount > 0) {
							// this one it knows, remember it, show it
							vouchers_current[voucher].reason = result.reason;
							vouchers_current[voucher].discount = result.discount;

							template_add('#voucher_result_ok', '#voucher_entry_' + voucher + '_result', {
								'.display_reason' : { textContent : result.reason },
								'.display_amount' : { textContent : result.discount },
							});
						}

						recalc();
					});
				}
			};
		};

		// load up voucher entries
		for (var i = 0; i < voucher_cap; i++) {
			// save an empty string for now
			vouchers_current.push({
				'code' : '',
				'reason' : '',
				'discount' : 0,
			});

			template_add('#voucher_entry', '#voucher_entries', {
				'#voucher_code_CNT' : { 
					id : 'voucher_code_' + i,
					name : 'voucher_code_' + i,
				},
				'#voucher_entry_CNT_result' : {
					id : 'voucher_entry_' + i + '_result',
				},
			}, 'voucher_entry_' + i);

			// wire in for pasting too
			document.querySelector('#voucher_code_' + i).addEventListener('change', voucher_updates(i));
			document.querySelector('#voucher_code_' + i).addEventListener('keyup', voucher_updates(i));
			document.querySelector('#voucher_code_' + i).addEventListener('paste', voucher_updates(i));
		}

		// update the visibility
		voucher_peekaboo();
	});

});

function orderize() {

	let items = [];

	// products
	available_product_descs.filter(p => p.genus != 'ticket').forEach(prod => {
		let n = 0;
		try {
			n = document.querySelector('#' + prod.name).value;
		} catch (error) {
		}
		if (n > 0) {
			items.push({
				'value' : n,
				'total' : prod.price * n,
			});
		}
	});

	// tickets
	let n_tickets = document.querySelector('#n_tickets').value;
	for (let i = 0; i < n_tickets; i++) {
		let ticket = resolve_ticket(i);
		items.push({
			'display' : ticket.display,
			'price' : ticket.price,
			'n' : 1,
			'total' : ticket.price,
		});
	}

	// vouchers
	for (let i = 0; i < vouchers_current.length; i++) {
		let v = vouchers_current[i];

		if (!v.code.length)
			continue;
		items.push({
			'display' : 'Voucher ' + v.code,
			'price' : v.discount * -1,
			'n' : 1,
			'total' : v.discount * -1,
		});
	}

	return items;

}
function itemize() {

	let items = [];

	// products
	available_product_descs.filter(p => p.genus != 'ticket').forEach(prod => {
		let n = 0;
		try {
			n = document.querySelector('#' + prod.name).value;
		} catch (error) {
		}
		if (n > 0) {
			items.push({
				'display' : prod.display,
				'price' : prod.price,
				'n' : n,
				'total' : prod.price * n,
			});
		}
	});

	// tickets
	let n_tickets = document.querySelector('#n_tickets').value;
	for (let i = 0; i < n_tickets; i++) {
		let ticket = resolve_ticket(i);
		items.push({
			'display' : ticket.display,
			'price' : ticket.price,
			'n' : 1,
			'total' : ticket.price,
		});
	}

	// vouchers
	for (let i = 0; i < vouchers_current.length; i++) {
		let v = vouchers_current[i];

		if (!v.code.length)
			continue;
		items.push({
			'display' : 'Voucher ' + v.code,
			'price' : v.discount * -1,
			'n' : 1,
			'total' : v.discount * -1,
		});
	}

	return items;

}

function totalize(items) {

	let total = items.reduce((total, item) => total + item.total, 0);
	// oh no you don't
	total = total < 0 ? 0 : total;

	return total;

}

function recalc() {

	let items = itemize();
	let total = totalize(items);

	document.querySelector('#price_total').textContent = total;

}
