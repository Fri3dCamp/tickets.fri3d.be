// vim: set ts=4 sw=4 noexpandtab :

self.addEventListener('install', (event) => {
	event.waitUntil(
		caches.open('fry_store').then((cache) =>
			cache.addAll([
				/*
				'/data/meme.jpg',
				'/ext/css/hack-subset.css',
				'/ext/js/luxon.min.js',
				'/css/index.css',
				'/ext/fonts/hack-regular-subset.woff2',
				'https://pretalx.fri3d.be/fri3dcamp2022/schedule/export/schedule.json',
				*/
			])
		)
	);
});

self.addEventListener('fetch', (event) => {
	console.log("hijacked fetch:");
	console.log(event.request.url);
	event.respondWith(caches.match(event.request).then((resp) =>
		resp || fetch(event.request)
	));
});
