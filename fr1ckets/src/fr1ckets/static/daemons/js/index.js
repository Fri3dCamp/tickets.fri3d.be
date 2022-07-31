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
const minute_to_height_ratio = 0.05;
let url_schedule = 'https://nogal.slechte.info/api/get_daemon_overview'; //'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json';
let url_mine_get = 'https://nogal.slechte.info/api/get_daemon_mine'; //'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json';
let url_mine_set = 'https://nogal.slechte.info/api/set_daemon_mine'; //'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json';
let schedule_complete = {};
let daemons_available = [];

function load_schedule() {
	console.log("loading schedule");
	fetch(url_schedule).then((resp) => resp.json()).then(sched => {
		schedule_install(sched.overview);
	});
}

load_schedule();

// XXX debug
let debug_show_grid = false;
document.querySelector('#debug_toggle_grid').addEventListener('change', (event) => {
	debug_show_grid = event.target.checked;
	console.log(event.target.value);
	schedule_show();
});

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
	let daemon_ids = [];
	console.log(typeof slot_id);

	modal.querySelectorAll('.daemon_name_select').forEach((s) => {
		if (s.checked) {
			daemon_ids.push(parseInt(s.dataset.daemonId));
		}
	});

	console.log(`slot_id=${slot_id} daemon_ids=${daemon_ids}`);

	if (!slot_id)
		return;

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
function daemon_select_show(slot_id) {
	
	let modal = document.querySelector('#commit_daemons');
	let list_output = document.querySelector('#commit_daemons_list');

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

				let start = luxon.DateTime.fromISO(event.start);
				let end = luxon.DateTime.fromISO(event.end);
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
	
		let day_interval = luxon.Interval.fromDateTimes(
			day.start, day.end);
		
		// cull days not in our filtering time range
		if (!filter_interval.overlaps(day_interval))
			return;

		let d = {
			tracks : [],
			timespan : day_interval,
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
	if (debug_show_grid)
		schedule_show_grid();
	else
		schedule_show_list();
}

function schedule_show_list() {

	let output = document.querySelector('#times');
	while (output.hasChildNodes()) {
		output.removeChild(output.lastChild);
	}

	my_current_slots = [];
	daemons_available.forEach((d) => {
		my_current_slots = my_current_slots.concat(d.slots);
	});

	schedule_filtered.days.forEach((day, day_index) => {

		let day_output = template_spin('#list_day', `day_${day_index}`);
		day_output.querySelector('.list_day_header').textContent = 
			day.timespan.start.toFormat('ccc yyyy-LL-dd');

		let all_events = [];

		// all tracks go into this list
		day.tracks.forEach((track, track_index) => {
			all_events = all_events.concat(track.events);
		});
		
		console.log(all_events);
		all_events.sort((l, r) => l.timespan.start - r.timespan.start);

		all_events.forEach((event, event_index) => {
			let event_output = template_spin('#list_day_entry', `entry_${event_index}`);

			event_output.querySelector('.list_day_entry_time').textContent =
				event.timespan.start.toFormat('HH:mm');
			event_output.querySelector('.list_day_entry_length').textContent =
				event.timespan.toDuration(['hours', 'minutes']).toHuman({
					unitDisplay : 'short',
				});
			event_output.querySelector('.list_day_entry_title').textContent = event.meta.title;
			event_output.querySelector('.list_day_entry_room').textContent = `${event.post} ${event.meta.n_needed}/${event.meta.n_committed}`;
			event_output.querySelector('.list_day_entry_add_button').textContent = my_current_slots.includes(event.meta.id) ? 'change' : 'add';
			event_output.querySelector('.list_day_entry_add_button').dataset.slotId = event.meta.id;
			event_output.querySelector('.list_day_entry_add_button').dataset.slotRoom = event.meta.n_needed - event.meta.n_committed;
			event_output.querySelector('.list_day_entry_add_button').addEventListener('click', (event) => {
				daemon_select_show(parseInt(event.target.dataset.slotId));
			});

			day_output.appendChild(event_output);
		});

		output.append(day_output);
	
	});

}

function schedule_show_grid() {

	let output = document.querySelector('#times');
	while (output.hasChildNodes()) {
		output.removeChild(output.lastChild);
	}

	function dur_to_offset(dur) {
		let o = dur.as('minutes') * minute_to_height_ratio;
		return `${o}rem`;
	}

	schedule_filtered.days.forEach((day) => {

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

				let event_output = document.createElement('div');
				event_output.classList.add('event');
				event_output.appendChild(document.createTextNode(event.post));

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
					event_output.style = `top: ${dur_to_offset(event.timespan.start.diff(time_clusters[cluster_index].start))};\nheight: ${dur_to_offset(event.timespan.toDuration())}`
				}

				track_outputs[cluster_index].appendChild(event_output);
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

		output.appendChild(day_output);
	});
}
