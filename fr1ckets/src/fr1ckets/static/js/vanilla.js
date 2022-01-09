// this is correct, month is 0-indexed
const volunteering_cutoff = new Date(2006, 7, 12).getTime();

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
	document.querySelectorAll('.product--image').forEach(item => {
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
		document.querySelector("#order_overview").classList.remove("hidden");
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
// if new_id is set, this'll be the templated instance's new id
function template_add(template_id, dest_parent_id, switcheroo, new_id)
{

	let template = document.querySelector(template_id);
	let dest = document.querySelector(dest_parent_id);
	let instance = template.content.cloneNode(true);

	if (switcheroo) {
		Object.keys(switcheroo).forEach(s => {
			instance.querySelectorAll(s).forEach(e => {
				Object.keys(switcheroo[s]).forEach(k => {
					e.setAttribute(k, switcheroo[s][k]);
				});
			});
		});
	}

	if (new_id)
		instance.id = new_id;

	dest.appendChild(instance);

}

// remove all of an element's children
function element_clear_children(selector) {
	let parent = document.querySelector(selector);
	while (parent.firstChild) {
		parent.lastChild.remove();
	}
}

document.addEventListener('DOMContentLoaded', event => {
	
	// check reservations
	let email_input = document.querySelector('#email');
	email_input.addEventListener('input', event => {
		// fixme; debounce
		let val = email_input.value;
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

		element_clear_children('#template_dest_participants');

		// a closure which updates meta for this ticket (options depending on date
		// and billability)
		let update_cb = function(ticket) {
			return function(event) {
				let h = 'ticket_' + ticket;
				let billable = document.querySelector('#' + h + '_billable').checked;
				let dob_year = document.querySelector('#' + h + '_dob_year').value;
				let dob_month = document.querySelector('#' + h + '_dob_month').value;
				let dob_day = document.querySelector('#' + h + '_dob_day').value;
				let dob = new Date(dob_year, dob_month + 1, dob_day).getTime();

				let can_volunteer = dob < volunteering_cutoff;

				element_clear_children('#' + h + '_meta');

				if (!dob_year.length || !dob_month.length || !dob_day.length) {
					template_add('#template_participant_meta_is_not_human', '#' + h + '_meta');
					return;
				}

				if (can_volunteer) {
					template_add('#template_participant_meta_is_volunteerable', '#' + h + '_meta');
				}
				if (billable) {
					template_add('#template_participant_meta_is_billable', '#' + h + '_meta');
				}

			};
		};


		for (let i = 0; i < n; i++) {
			let new_id = 'ticket_' + i;
			let cb = update_cb(i);

			// throw up a form for this ticket
			template_add('#template_participant', '#template_dest_participants', {
				'[for=ticket_CNT_name]' : { for : new_id + '_name' },
				'[for=ticket_CNT_dob_year]' : { for : new_id + '_dob_year' },
				'[for=ticket_CNT_dob_month]' : { for : new_id + '_dob_month' },
				'[for=ticket_CNT_dob_day]' : { for : new_id + '_dob_day' },
				'[for=ticket_CNT_billable]' : { for : new_id + '_billable' },
				'#ticket_CNT_name' : { id : new_id + '_name', name : new_id + '_name' },
				'#ticket_CNT_dob_year' : { id : new_id + '_dob_year', name : new_id + '_dob_year' },
				'#ticket_CNT_dob_month' : { id : new_id + '_dob_month', name : new_id + '_dob_month' },
				'#ticket_CNT_dob_day' : { id : new_id + '_dob_day', name : new_id + '_dob_day' },
				'#ticket_CNT_billable' : { id : new_id + '_billable', name : new_id + '_billable' },
				'#ticket_CNT_meta' : { id : new_id + '_meta' },
			}, new_id);

			// hook in the update_cb to respond to any changes
			document.querySelector('#' + new_id + '_dob_year').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_dob_month').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_dob_day').addEventListener('change', cb);
			document.querySelector('#' + new_id + '_billable').addEventListener('change', cb);
		}

	});

});
