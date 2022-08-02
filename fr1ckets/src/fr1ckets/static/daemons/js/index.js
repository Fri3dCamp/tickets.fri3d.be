// vim: set ts=4 sw=4 noexpandtab :

// load up the service worker (if a newer version is there)
/*
if ('serviceWorker' in navigator) {
	navigator.serviceWorker.register('/sw.js').then(() => {
		console.log("installed service worker");
	});
}
*/

const clustering_window = luxon.Duration.fromISOTime('00:30');
const minute_to_height_ratio = 0.125;
let url_base = 'http://localhost:8070/api/'; //'https://nogal.slechte.info/api/';
let url_schedule = `${url_base}get_daemon_overview`; //'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json';
let url_mine_get = `${url_base}get_daemon_mine`; //'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json';
let url_mine_set = `${url_base}set_daemon_mine`; //'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json';
let schedule_complete = {};
let daemons_available = [];
let posts_available = [];
let display_list = true;

document.querySelector('#js_warning').hidden = true;

function load_schedule() {
	console.log("loading schedule");
	fetch(url_schedule).then((resp) => resp.json()).then(sched => {
		// save posts
		posts_available = sched.overview.posts;
		recalc_display_method();
		schedule_install(sched.overview);
	});
}

addEventListener('resize', (e) => {
	console.log('resize!');
	recalc_display_method();
	schedule_show();
});

load_schedule();


function recalc_display_method() {
	let needed = 50 + (posts_available.length * 158);
	console.log('needed='+needed);
	console.log("have="+window.innerWidth);

	display_list = (window.innerWidth < needed);
}

// identification
document.querySelector('#identification_launch').addEventListener('click', (event) => {
	let email = document.querySelector('#identification_email').value;

	fetch(url_mine_get, {
		method : 'POST',
		headers : {
			'Content-Type' : 'application/json',
		},
		body : JSON.stringify({
			'email' : email,
		}),
	}).then((resp) => resp.json()).then(mine => {
		daemons_available = mine.daemons;
		if (daemons_available.length) {
			document.querySelector('#output_daemons').textContent = daemons_available.map((d) => d.name).join(', ');
			document.querySelector('#notify_email_ok').hidden = false;
			document.querySelector('#notify_email_error').hidden = true;
		} else {
			document.querySelector('#notify_email_ok').hidden = true;
			document.querySelector('#notify_email_error').hidden = false;
		}
		// redraw the schedule
		schedule_show();
	});
});

function daemons_push() {

	let email = document.querySelector('#identification_email').value;
	let out = [];

	daemons_available.forEach((d) => {
		out.push({
			id : d.id,
			slot_ids : d.slots,
		});
	});

	fetch(url_mine_set, {
		method : 'POST',
		headers : {
			'Content-Type' : 'application/json',
		},
		body : JSON.stringify({
			daemons : out,
			email : email,
		}),
	}).then(resp => resp.json()).then(ret => {
		daemons_available = ret.daemons;
		load_schedule();
	});
}

document.querySelector('#commit_daemons').addEventListener('close', (event) => {
	let modal = event.target;
	console.log(modal.returnValue);

	if (modal.returnValue == 'rollback') {
		return;
	}

	let slot_id = parseInt(modal.dataset.slotId);
	let slot_room = parseInt(modal.dataset.slotRoom);
	let daemon_ids = [];
	console.log(typeof slot_id);

	modal.querySelectorAll('.daemon_name_select').forEach((s) => {
		if (s.checked) {
			daemon_ids.push(parseInt(s.dataset.daemonId));
		}
	});

	console.log(`slot_id=${slot_id} slot_room=${slot_room} daemon_ids=${daemon_ids}`);

	if (!slot_id)
		return;

	if (daemon_ids.length > slot_room) {
		daemon_select_show(slot_id, slot_room, message=`Je koos teveel mensen!`);
		return;
	}

	// walk over our known daemons, to remove or add this slot
	daemons_available.forEach((d) => {
		// remove in all cases
		d.slots = d.slots.filter((s_id) => s_id != slot_id);
		// add conditionally
		if (daemon_ids.includes(d.id))
			d.slots.push(slot_id);
	});

	daemons_push();
});
function daemon_select_show(slot_id, slot_room, message=undefined) {
	
	let modal = document.querySelector('#commit_daemons');
	let list_output = document.querySelector('#commit_daemons_list');
	let message_output = document.querySelector('#commit_daemons_message');

	if (message) {
		message_output.textContent = message;
		message_output.hidden = false;
	} else {
		message_output.hidden = true;
	}

	while (list_output.hasChildNodes()) {
		list_output.removeChild(list_output.lastChild);
	}

	daemons_available.forEach((d) => {
		let d_entry = template_spin('#commit_daemons_list_entry', `daemon_${d.id}`);
		d_entry.querySelector('.daemon_name_select').dataset.daemonId = d.id;
		d_entry.querySelector('.daemon_name_select').checked = d.slots.includes(slot_id);
		d_entry.querySelector('.daemon_name_label').textContent = d.name;
		list_output.appendChild(d_entry);
	});

	modal.dataset.slotId = slot_id;
	modal.dataset.slotRoom = slot_room;

	modal.showModal();
}

let schedule = {
	days : [],
	start : undefined,
	end : undefined,
};
let filter = {
	tracks : {
		available : new Set(),
		selected : new Set(),
	},
	time : {
		min : undefined,
		max : undefined,
		selected : {
			start : undefined,
			end : undefined,
		},
	},
	search : '',
};
function schedule_install(sched) {

	// output
	let o = {
		days : [],
		start : luxon.DateTime.fromISO('9999-01-01'),
		end : luxon.DateTime.fromISO('1000-01-01'),
	};

	// keep track of this to build a filter widget
	let available_tracks = new Set();

	o.days = [];
	sched.days.forEach((day) => {
		// for each day, remember when is starts/ends, and assemble
		// a list of tracks
		let d = {};

		d.start = luxon.DateTime.fromISO(day.day).startOf('day');
		d.end = luxon.DateTime.fromISO(day.day).endOf('day');
		d.timespan = luxon.Interval.fromDateTimes(d.start, d.end);
	
		// assuming the days are not in order, adjust entire schedule time
		o.start = (d.start < o.start) ? d.start : o.start;
		o.end = (d.end > o.end) ? d.end : o.end;

		d.tracks = [];
		for (post in day.posts) {
			// for each track (or "post"), remember it's name and
			// assemble a list of events happening in this track on this
			// day
			let t = {};

			t.post = post;
			t.events = [];

			// filter stuff
			available_tracks.add(post);

			day.posts[post].forEach((event) => {
				// for each event, remember when it happens and link
				// to the original struct
				let e = {};

				let start = round_datetime(luxon.DateTime.fromISO(event.start));
				let end = round_datetime(luxon.DateTime.fromISO(event.end));
				e.timespan = luxon.Interval.fromDateTimes(
					start,
					end
				);
				e.post = post;
				e.meta = event;

				t.events.push(e);
			});

			d.tracks.push(t);
		}

		// they arrive out of order
		d.tracks.sort((l, r) => l.start - r.start);

		o.days.push(d);
	});

	// install the main schedule
	schedule = o;

	// update the filtering widget
	filter.tracks.available = available_tracks;
	filter.tracks.selected = new Set(available_tracks.values());
	filter.time.min = o.start;
	filter.time.selected.start = o.start;
	filter.time.max = o.end;
	filter.time.selected.end = o.end;
	
	console.log(schedule);
	console.log(filter);

	filter_update();
	filter_apply();

	schedule_show();
}

function filter_update() {

	let output = document.querySelector('#filter');

	while (output.hasChildNodes()) {
		output.removeChild(output.lastChild);
	}

	for (const t of filter.tracks.available.values()) {
		console.log(t);
		let b = document.createElement('input');

		b.type = 'checkbox';
		b.value = t;
		b.name = `filter_track_selector_${t}`;
		b.id = `filter_track_selector_${t}`;
		b.checked = (filter.tracks.selected.has(t)) ? true : false;

		b.onclick = (e) => {
			let t = e.target.value;
			if (e.target.checked) {
				filter.tracks.selected.add(t);
			} else {
				filter.tracks.selected.delete(t);
			}
			filter_apply();
		};

		let l = document.createElement('label');
		l.htmlFor = b.id;
		l.appendChild(document.createTextNode(t));

		output.appendChild(b);
		output.appendChild(l);
	}

	let time_start = document.querySelector('#filter_time_start');
	let time_end = document.querySelector('#filter_time_end');

	function mangle_for_html(a_datetime) {
		return a_datetime.toISO().slice(0, 16);
	}
	/*
	 * the html datetime-local is given YYYY-MM-DDTHH:MM times and assumes them
	 * to be local and shows them as such (also upon change event), so we
	 * - set: convert internal to normal ISO local+-offset, strip :SS.sss & offset,
	 *   insert that
	 * - get: add :SS.sss, feed it to luxon.DateTime.fromISO() which assumes it to
	 *   be in local time and adds the relevant offset again
	 */
	let t = document.createElement('input');
	t.type = 'datetime-local';
	t.name = 'filter_time_start';
	t.id = 'filter_time_start';
	t.min = mangle_for_html(filter.time.min);
	t.max = mangle_for_html(filter.time.max);
	t.value = mangle_for_html(filter.time.selected.start);
	t.onchange = (e) => {
		filter.time.selected.start = luxon.DateTime.fromISO(e.target.value + ':00.000');
		filter_apply();
	};
	let l = document.createElement('label');
	l.htmlFor = t.id;
	l.appendChild(document.createTextNode('from'));
	output.appendChild(l);
	output.appendChild(t);

	t = document.createElement('input');
	t.type = 'datetime-local';
	t.name = 'filter_time_start';
	t.id = 'filter_time_start';
	t.min = mangle_for_html(filter.time.min);
	t.max = mangle_for_html(filter.time.max);
	t.value = mangle_for_html(filter.time.selected.end);
	t.onchange = (e) => {
		filter.time.selected.end = luxon.DateTime.fromISO(e.target.value + ':59.999');
		filter_apply();
	};
	l = document.createElement('label');
	l.htmlFor = t.id;
	l.appendChild(document.createTextNode('to'));
	output.appendChild(l);
	output.appendChild(t);

	t = document.createElement('input');
	t.type = 'text';
	t.name = 'filter_text';
	t.id = 'filter_text';
	t.onchange = (e) => {
		filter.search = e.target.value;
		filter_apply();
	};
	l = document.createElement('label');
	l.htmlFor = t.id;
	l.appendChild(document.createTextNode('search'));
	output.appendChild(l);
	output.appendChild(t);

}

let schedule_filtered = {
	days : [],
};

function filter_apply() {
	
	let o = {
		days : [],
	};

	let filter_interval = luxon.Interval.fromDateTimes(
		filter.time.selected.start,
		filter.time.selected.end
	);

	function event_contains_string(event, search) {
		function check(haystack, needle) {
			return haystack && haystack.toLowerCase().indexOf(needle.toLowerCase()) > -1;
		}
		return [ 'abstract', 'description', 'title' ].filter(x => check(event[x], search)).length > 0;
	}

	schedule.days.forEach((day) => {
	
		// cull days not in our filtering time range
		if (!filter_interval.overlaps(day.timespan))
			return;

		let d = {
			tracks : [],
			timespan : day.timespan,
		};

		day.tracks.forEach((track) => {

			// cull unselected tracks
			if (!filter.tracks.selected.has(track.post))
				return;

			let t = {
				post: track.post,
				events : [],
			};

			track.events.forEach((event) => {
				// cull out not within filtering time range
				if (!filter_interval.overlaps(event.timespan))
					return;

				// cull out not matching search text, if set
				if (filter.search.length && !event_contains_string(event.meta, filter.search))
					return;

				t.events.push(event);

			});

			d.tracks.push(t);

		});

		o.days.push(d);

	});

	schedule_filtered = o;

	schedule_show();

}

function template_spin(template_selector, id=undefined) {

	let template = document.querySelector(template_selector);
	let instance = template.content.cloneNode(true);

	if (id) {
		// if we need to set an id, we need a wrapper to contain whatever
		// the template contains, and assign the id to that wrapper
		let wrapper = document.createElement('div');
		wrapper.id = id;
		wrapper.appendChild(instance);
		instance = wrapper;
	}

	return instance;

}

function schedule_show() {
	if (display_list)
		schedule_show_list(schedule_filtered);
	else
		schedule_show_grid(schedule_filtered);
}

// round a luxon datetime to 30mins
function round_datetime(dt) {
	let hour = dt.hour;
	let min = dt.minute;

	if (dt.minute < 15) {
		min = 0;
	} else if (dt.minute < 45) {
		min = 30;
	} else {
		min = 0;
		hour += 1;
	}

	return dt.set({ hour : hour, minute : min, second : 0 });

}

// given an html node, stuff the event's details into it, if the event's id
// is in slots_committed we show this visually too
function schedule_inflate_event(node, event, slots_committed) {

	let post = posts_available.find((p) => event.post == p.code);

	node.querySelector('.time_start').textContent = event.timespan.start.toFormat('HH:mm');
	node.querySelector('.time_length').textContent = event.timespan.toDuration(['hours']).toHuman({
		unitDisplay : 'short',
	});

	let n_people_needed = Math.max(event.meta.n_needed - event.meta.n_committed, 0);

	node.querySelector('.title').textContent = post.name;
	node.querySelector('.abstract').textContent = post.abstract;
	node.querySelector('.people_needed').textContent = n_people_needed ? `Nog ${n_people_needed} plaats${n_people_needed == 1 ? '' : 'en'}!` : 'Volzet';

	let button = node.querySelector('.commit_button');

	// if we have people to commit, show a button which allows this
	if (daemons_available.length == 0) {
		// no we don't
		button.hidden = true;
	} else {
		// if the user has already committed, that takes precedence
		if (slots_committed.includes(event.meta.id)) {
			button.classList.add('button_change');
			button.textContent = "verander keuze";
		} else {
			// user hasn't committed to this, allow to commit if there's room
			if (n_people_needed) {
				button.classList.add('button_add');
				button.textContent = "schrijf mij op!";
			} else {
				button.hidden = true;
				/*
				button.classList.add('full');
				button.textContent = "volzet";
				button.active = false;
				*/
			}
		}

		button.dataset.slotId = event.meta.id;
		button.dataset.slotRoom = n_people_needed + slots_committed.filter(e => e == event.meta.id).length;
		button.addEventListener('click', (event) => {
			daemon_select_show(parseInt(event.target.dataset.slotId), parseInt(event.target.dataset.slotRoom));
		});
	}

}

function schedule_show_list(schedule) {

	let output = document.querySelector('#times');
	while (output.hasChildNodes()) {
		output.removeChild(output.lastChild);
	}

	let my_current_slots = [];
	daemons_available.forEach((d) => {
		my_current_slots = my_current_slots.concat(d.slots);
	});

	schedule.days.forEach((day, day_index) => {

		let day_output = template_spin('#list_day', `day_${day_index}`);
		day_output.querySelector('.list_day_header').textContent = 
			day.timespan.start.toFormat('ccc yyyy-LL-dd');

		let all_events = [];

		// all tracks go into this list
		day.tracks.forEach((track, track_index) => {
			all_events = all_events.concat(track.events);
		});
	
		// make sure they're in starting-time order
		all_events.sort((l, r) => l.timespan.start - r.timespan.start);

		// now just loop over the events for this day and blit them
		all_events.forEach((event, event_index) => {
			let event_output = template_spin('#list_entry', `entry_${event_index}`);

			schedule_inflate_event(event_output, event, my_current_slots);

			day_output.appendChild(event_output);
		});

		output.append(day_output);
	
	});

}

function schedule_show_grid(schedule) {

	let output = document.querySelector('#times');
	while (output.hasChildNodes()) {
		output.removeChild(output.lastChild);
	}

	let my_current_slots = [];
	daemons_available.forEach((d) => {
		my_current_slots = my_current_slots.concat(d.slots);
	});


	function dur_to_offset(dur) {
		let o = dur.as('minutes') * minute_to_height_ratio;
		return `${o}rem`;
	}

	schedule.days.forEach((day) => {
		let day_header = template_spin('#list_day');
		day_header.querySelector('.list_day_header').textContent = 
			day.timespan.start.toFormat('ccc yyyy-LL-dd');


		let day_output = document.createElement('div');
		day_output.classList.add('day');
		let ruler_lane_output = document.createElement('div');
		ruler_lane_output.classList.add('ruler-lane');

		let time_clusters = [];

		day.tracks.forEach((track) => {
			time_clusters = luxon.Interval.merge(
				time_clusters.concat(
					track.events.map((e) => 
						luxon.Interval.fromDateTimes(
							e.timespan.start,
							e.timespan.end.plus(clustering_window)
						)
					)
				)
			);
		});

		time_clusters.sort((l, r) => l.start - r.start);

		console.log("clusters:");
		time_clusters.forEach((cluster) => {
			let ruler = document.createElement('div');
			ruler.classList.add('ruler');

			ruler.style = `height: ${dur_to_offset(cluster.toDuration())};`;

			let tick_increment = luxon.Duration.fromISOTime('00:30');
			let tick_pos = cluster.start;

			while (cluster.contains(tick_pos)) {
				let tick = document.createElement('div');
				tick.classList.add('tick');
				tick.style = `top: ${dur_to_offset(tick_pos.diff(cluster.start))}`;
				tick.appendChild(document.createTextNode(tick_pos.toFormat('HH:mm')));
				ruler.appendChild(tick);
				tick_pos = tick_pos.plus(tick_increment);
			};

			ruler_lane_output.appendChild(ruler);

			if (cluster != time_clusters[time_clusters.length-1]) {
				let ruler_break = document.createElement('div');
				ruler_break.classList.add('ruler-break');
				ruler_lane_output.appendChild(ruler_break);
			}
		});

		day_output.appendChild(ruler_lane_output);

		day.tracks.forEach((track) => {
			let track_lane_output = document.createElement('div');
			track_lane_output.classList.add('track-lane');

			track_outputs = [];
			time_clusters.forEach((cluster) => {
				let o = document.createElement('div');
				o.classList.add('track');

				o.style = `height: ${dur_to_offset(cluster.toDuration())}`;

				track_outputs.push(o);

			});

			track.events.forEach((event) => {

				let event_rect = document.createElement('div');
				event_rect.classList.add('event');

				let event_output = template_spin('#grid_entry');
				schedule_inflate_event(event_output, event, my_current_slots);

				event_rect.appendChild(event_output);

				let cluster_index = undefined;
				for (let i = 0; i < time_clusters.length; i++) {
					if (time_clusters[i].contains(event.timespan.start)) {
						cluster_index = i;
						break;
					}
				}
				if (cluster_index == undefined) {
					console.log(`ERROR; could not find a cluster for this event=${event}`);
				} else {
					event_rect.style = `top: ${dur_to_offset(event.timespan.start.diff(time_clusters[cluster_index].start))};\nheight: ${dur_to_offset(event.timespan.toDuration())}`
				}

				track_outputs[cluster_index].appendChild(event_rect);
			});

			track_outputs.forEach((o) => {
				track_lane_output.appendChild(o);
				if (o != track_outputs[track_outputs.length-1]) {
					let track_break = document.createElement('div');
					track_break.classList.add('track-break');
					track_lane_output.appendChild(track_break);
				}
			});

			day_output.appendChild(track_lane_output);

		});

		day_header.querySelector('.list_day_content').appendChild(day_output);
		output.appendChild(day_header);
		//output.appendChild(day_output);
	});
}
