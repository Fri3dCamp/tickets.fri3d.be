// vim: set ts=4 sw=4 noexpandtab :
// please be kind, written short-notice and under covid, jvdb

// events need to be this close to each other in time to be considered
// part of the same cluster, so we can skip inter-cluster (empty) timelines (grid view)
const clustering_window = luxon.Duration.fromISOTime('00:30');
// every minute is this much rem (grid view)
const minute_to_height_ratio = 0.125;

let url_base = '/api/';
let url_schedule = `${url_base}get_daemon_overview`;
let url_mine_get = `${url_base}get_daemon_mine`;
let url_mine_set = `${url_base}set_daemon_mine`;

// api-filled, list of our known volunteers
let daemons_available = [];
// api-filled, list of known volunteering posts
let posts_available = [];
// api-filled, the main schedule
let schedule = {
	days : [],
	start : undefined,
	end : undefined,
};

document.querySelector('#js_warning').hidden = true;

addEventListener('resize', (e) => {
	schedule_blit(schedule);
});

schedule_load();

/*
                      _ _ 
  ___ _ __ ___   __ _(_) |
 / _ \ '_ ` _ \ / _` | | |
|  __/ | | | | | (_| | | |
 \___|_| |_| |_|\__,_|_|_|
                          
upon form entry, populate global daemons_available and re-blit the schedule
*/

document.querySelector('#identification_entry').addEventListener('submit', (event) => {
	event.preventDefault();

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
		schedule_blit(schedule);
	});
});

/*
                     _       _ 
 _ __ ___   ___   __| | __ _| |
| '_ ` _ \ / _ \ / _` |/ _` | |
| | | | | | (_) | (_| | (_| | |
|_| |_| |_|\___/ \__,_|\__,_|_|
                               

there is a single <dialog> showing the assigned/available daemons (volunteers)
for a given slot

daemon_select_show() shows it by:
	* stuffing in the daemons it finds in global daemons_available (marking them as
	  already commited if they are already committed to this slot
	* saving meta in the modal's dataset

the close event is called by the runtime when a button is clicked on the modal, and:
	* fetches the meta from the dataset
	* extracts the selected daemons
	* if there's too many daemons selected (more than the slot can hold), _show()s the modal again
	* if all succeeds, saves changes to global daemons_available
	* calls daemons_push

daemons_push() pushes what's in global daemons_available and blanketly reloads the sched
*/
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
		schedule_load();
	});
}

document.querySelector('#commit_daemons').addEventListener('close', (event) => {
	let modal = event.target;

	if (modal.returnValue == 'rollback') {
		return;
	}

	let slot_id = parseInt(modal.dataset.slotId);
	let slot_room = parseInt(modal.dataset.slotRoom);
	let daemon_ids = [];

	modal.querySelectorAll('.daemon_name_select').forEach((s) => {
		if (s.checked) {
			daemon_ids.push(parseInt(s.dataset.daemonId));
		}
	});

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

/*
          _              _       _      
 ___  ___| |__   ___  __| |_   _| | ___ 
/ __|/ __| '_ \ / _ \/ _` | | | | |/ _ \
\__ \ (__| | | |  __/ (_| | |_| | |  __/
|___/\___|_| |_|\___|\__,_|\__,_|_|\___|
                                        

_load() loads it all up, calls _process() and saves the processed in global schedule
_process() does a pass over the input data and basically just internalizes timestamps
_blit() shows the current schedule in global schedule, either with
	_show_list() for the list (smaller screens) or
	_show_grid() for the grid
_inflate_event() helps this by stuffing an event (id est, slot) into a html node
*/

function schedule_load() {

	fetch(url_schedule).then((resp) => resp.json()).then(sched => {
		posts_available = sched.overview.posts;
		schedule = schedule_process(sched.overview);
		schedule_blit(schedule);
	});

}

function schedule_process(sched) {

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

	return o;

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

// show the main schedule, in list/grid for depending on screen real estate
function schedule_blit(schedule) {
	let needed = 50 + (posts_available.length * 158);

	let blit = (window.innerWidth < needed) ? schedule_show_list : schedule_show_grid;

	blit(schedule);
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
	});

}

/*
       _   _ _ 
 _   _| |_(_) |
| | | | __| | |
| |_| | |_| | |
 \__,_|\__|_|_|
               
*/

// instantiate a <template> id'd by the selector, optionally assigning
// the instance the specified id (technically, a <div id="whatyouwant"></div> around it)
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
