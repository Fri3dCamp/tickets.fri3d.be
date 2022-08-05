CREATE SCHEMA IF NOT EXISTS `fr1ckets` DEFAULT CHARACTER SET utf8mb4;
USE `fr1ckets`;

drop table if exists product;
create table product (
	id integer auto_increment not null,
	genus varchar(32) not null,
	species varchar(32) not null,
	name varchar(64) not null,
	display varchar(64) not null,
	price float not null,
	volunteering_price float not null,
	price_net float not null,
	volunteering_price_net float not null,
	part_vat_21 float not null,
	volunteering_part_vat_21 float not null,
	part_vat_12 float not null,
	part_vat_6 float not null,
	part_vat_0 float not null,
	max_dob datetime not null,
	billable integer not null,
	primary key (id)
);

insert into product (genus, species, name, display, price, volunteering_price, price_net, volunteering_price_net, part_vat_21, volunteering_part_vat_21, part_vat_12, part_vat_6, part_vat_0, max_dob, billable) values
	( 'ticket', 'normal', 'ticket_3bit',     'Ticket 0-3 jaar',                  12,   12,  11.32,  11.32,   0,   0,  0, 12, 0, '2019-08-11 13:37:00', 0),
	( 'ticket', 'normal', 'ticket_4bit',     'Ticket 3-6 jaar',                  22,   22,  20.25,  20.25,   0,   0, 10, 12, 0, '2016-08-11 13:37:00', 0),
	( 'ticket', 'normal', 'ticket_5bit',     'Ticket 6-12 jaar',                 40,   40,  35.79,  35.79,   8,   8, 20, 12, 0, '2010-08-11 13:37:00', 0),
	( 'ticket', 'normal', 'ticket_6bit',     'Ticket 12-24 jaar',                82,   82,  73.11,  73.11,  19,  19, 40, 23, 0, '1998-08-11 13:37:00', 0),
	( 'ticket', 'normal', 'ticket_7bit',     'Ticket +24 jaar',                  174, 149, 155.23, 134.57,  59,  34, 40, 75, 0, '1900-01-01 00:00:00', 0),
	( 'ticket', 'normal', 'ticket_8bit',     'Ticket zakelijk',                  348, 348, 299.03, 299.03, 233, 233, 40, 75, 0, '1900-01-01 00:00:00', 1),
	( 'garment', 'tshirt_m', 'tshirt_m__xxs',  'Volwassenen mannen t-shirt XXS',       20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__xs',  'Volwassenen mannen t-shirt XS',         20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__s',  'Volwassenen mannen t-shirt S',           20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__m',  'Volwassenen mannen t-shirt M',           20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__l',  'Volwassenen mannen t-shirt L',           20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__xl',  'Volwassenen mannen t-shirt XL',         20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__xxl',  'Volwassenen mannen t-shirt XXL',       20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__3xl',  'Volwassenen mannen t-shirt 3XL',       20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__4xl',  'Volwassenen mannen t-shirt 4XL',       20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_m', 'tshirt_m__5xl',  'Volwassenen mannen t-shirt 5XL',       20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_f', 'tshirt_f__xs',  'Volwassenen vrouwen t-shirt XS',        20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_f', 'tshirt_f__s',  'Volwassenen vrouwen t-shirt S',          20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_f', 'tshirt_f__m',  'Volwassenen vrouwen t-shirt M',          20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_f', 'tshirt_f__l',  'Volwassenen vrouwen t-shirt L',          20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_f', 'tshirt_f__xl',  'Volwassenen vrouwen t-shirt XL',        20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_teal', 'tshirt_kids_teal__xs', 'Kinderen 3-4 jaar t-shirt',    20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_teal', 'tshirt_kids_teal__s', 'Kinderen 5-6 jaar t-shirt',     20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_teal', 'tshirt_kids_teal__m', 'Kinderen 7-8 jaar t-shirt',     20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_teal', 'tshirt_kids_teal__l', 'Kinderen 9-11 jaar t-shirt',    20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_teal', 'tshirt_kids_teal__xl', 'Kinderen 12-14 jaar t-shirt',  20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_black', 'tshirt_kids_black__xs', 'Kinderen 3-4 jaar t-shirt',  20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_black', 'tshirt_kids_black__s', 'Kinderen 5-6 jaar t-shirt',   20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_black', 'tshirt_kids_black__m', 'Kinderen 7-8 jaar t-shirt',   20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_black', 'tshirt_kids_black__l', 'Kinderen 9-11 jaar t-shirt',  20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'tshirt_kids_black', 'tshirt_kids_black__xl', 'Kinderen 12-14 jaar t-shirt',20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_kids', 'hoodie_kids__xs', 'Kinderen 3-4 jaar hoodie',               40, 40, 33.06, 33.06, 40, 40, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_kids', 'hoodie_kids__s', 'Kinderen 5-6 jaar hoodie',                40, 40, 33.06, 33.06, 40, 40, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_kids', 'hoodie_kids__m', 'Kinderen 7-8 jaar hoodie',                40, 40, 33.06, 33.06, 40, 40, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_kids', 'hoodie_kids__l', 'Kinderen 9-11 jaar hoodie',               40, 40, 33.06, 33.06, 40, 40, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_kids', 'hoodie_kids__xl', 'Kinderen 12-14 jaar hoodie',             40, 40, 33.06, 33.06, 40, 40, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__xxs',  'Volwassenen unisex hoodie XXS',        45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__xs',  'Volwassenen unisex hoodie XS',          45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__s',  'Volwassenen unisex hoodie S',            45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__m',  'Volwassenen unisex hoodie M',            45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__l',  'Volwassenen unisex hoodie L',            45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__xl',  'Volwassenen unisex hoodie XL',          45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__xxl',  'Volwassenen unisex hoodie XXL',        45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__3xl',  'Volwassenen unisex hoodie 3XL',        45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__4xl',  'Volwassenen unisex hoodie 4XL',        45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'hoodie_uni', 'hoodie_uni__5xl',  'Volwassenen unisex hoodie 5XL',        45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__xxs',  'Volwassenen unisex sweater XXS',     45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__xs',  'Volwassenen unisex sweater XS',       45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__s',  'Volwassenen unisex sweater S',         45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__m',  'Volwassenen unisex sweater M',         45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__l',  'Volwassenen unisex sweater L',         45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__xl',  'Volwassenen unisex sweater XL',       45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__xxl',  'Volwassenen unisex sweater XXL',     45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'garment', 'sweater_uni', 'sweater_uni__3xl',  'Volwassenen unisex sweater 3XL',     45, 45, 37.19, 37.19, 45, 45, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'simple', 'token', 'token', 'Dranktoken',                    1.8, 1.8, 1.49, 1.49, 1.8, 1.8, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'simple', 'mug', 'mug', 'Emaille mok',                    10, 10, 8.26, 8.26, 10, 10, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'donation', 'monetary', 'donation', 'Donatie',                    10, 10, 10, 10, 0, 0, 0, 0, 10, '1900-01-01 00:00:00', 0),
	( 'ticket', 'vip_all', 'ticket_vip_all', 'VIP ticket voor alle dagen', 0, 0, 0, 0, 0, 0, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket', 'vip_friday', 'ticket_vip_friday', 'VIP ticket voor vrijdag', 0, 0, 0, 0, 0, 0, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket', 'vip_saturday', 'ticket_vip_saturday', 'VIP ticket voor zaterdag', 0, 0, 0, 0, 0, 0, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket', 'vip_sunday', 'ticket_vip_sunday', 'VIP ticket voor zondag', 0, 0, 0, 0, 0, 0, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket', 'vip_monday', 'ticket_vip_monday', 'VIP ticket voor maandag', 0, 0, 0, 0, 0, 0, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'badge', 'accessory', 'badge_accessory_a', 'Time Blaster', 20, 20, 16.53, 16.53, 20, 20, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'badge', 'accessory', 'badge_accessory_b', 'GameOn', 12, 12, 9.92, 9.92, 12, 12, 0, 0, 0, '1900-01-01 00:00:00', 0),
	( 'infrastructure', 'spot', 'camper_spot', 'Camper/caravan plaatsje', 25, 25, 23.58, 23.58, 0, 0, 0, 25, 0, '1900-01-01 00:00:00', 0),
	( 'infrastructure', 'spot', 'hotel_spot', 'Hotel-kamer', 160, 160, 150.94, 150.94, 0, 0, 0, 160, 0, '1900-01-01 00:00:00', 0),
	( 'infrastructure', 'spot', 'room_spot', 'Bed in gedeelde kamer', 30, 30, 28.30, 28.30, 0, 0, 0, 30, 0, '1900-01-01 00:00:00', 0);

drop table if exists reservation;
create table reservation (
	id integer auto_increment not null,
	email varchar(128) not null unique,
	available_from datetime not null,
	claimed integer default 0,
	claimed_at datetime default null,
	comments text,
	primary key (id),
	index reservation_email_index (email asc)
);
insert into reservation (email, available_from) values
	('default', '2022-02-02 19:00:00'),
	('someone@who.reserved', '2022-01-19 19:00:00');

drop table if exists purchase;
create table purchase (
	id integer auto_increment not null,
	email varchar(128) not null,
	nonce varchar(128) not null,
	payment_code varchar(128) not null unique,
	reservation_id integer,
	special_accomodation_needs integer default 0,
	queued integer default 0,
	once_queued integer default 0,
	paid integer default 0,
	removed integer default 0,
	billed integer default 0,
	created_at datetime not null,
	removed_at datetime default null,
	paid_at datetime default null,
	billed_at datetime default null,
	dequeued_at datetime default null,
	comments text,
	business_name text,
	business_address text,
	business_vat text,
	primary key (id),
	index purchase_nonce_index (nonce asc),
	constraint purchase_reservation_id_fk foreign key (reservation_id) references reservation (id) on delete restrict on update cascade
);

drop table if exists voucher;
create table voucher (
	id integer auto_increment not null,
	code varchar(128) not null unique,
	discount integer default 0,
	claimed integer default 0,
	claimed_at datetime default null,
	reason text,
	comments text,
	purchase_id integer,
	primary key (id),
	index voucher_code_index (code asc),
	constraint voucher_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete set null on update cascade
);


drop table if exists purchase_voucher;
create table purchase_voucher (
	id integer auto_increment not null,
	purchase_id integer,
	voucher_id integer,
	primary key (id),
	constraint purchase_voucher_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update cascade,
	constraint purchase_voucher_voucher_id_fk foreign key (voucher_id) references voucher (id) on delete cascade on update cascade
);

drop table if exists purchase_history;
create table purchase_history (
	id integer auto_increment not null,
	purchase_id integer,
	created_at datetime not null,
	creator varchar(128) not null,
	event text,
	primary key (id),
	index purchase_history_purchase_id_index (purchase_id asc),
	constraint purchase_history_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update set null
);

drop table if exists purchase_items;
create table purchase_items (
	id integer auto_increment not null,
	purchase_id integer,
	product_id integer,
	n integer not null,
	person_name text null,
	person_dob date null,
	person_volunteers_before integer not null,
	person_volunteers_during integer not null,
	person_volunteers_after integer not null,
	person_food_vegitarian integer not null,
	primary key (id),
	constraint purchase_items_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update cascade,
	constraint purchase_items_product_id_fk foreign key (product_id) references product (id) on delete set null on update cascade
);

drop table if exists daemon_day;
create table daemon_day (
	code varchar(64) unique not null,
	display varchar(64) not null,
	day datetime,
	primary key (code)
);
insert into daemon_day (code, display, day) values
	( 'DONDERDAG', 'Donderdag', '2022-08-11T00:00:00' ),
	( 'VRIJDAG', 'Vrijdag', '2022-08-12T00:00:00' ),
	( 'ZATERDAG', 'Zaterdag', '2022-08-13T00:00:00' ),
	( 'ZONDAG', 'Zondag', '2022-08-14T00:00:00' );

drop table if exists daemon_post;
create table daemon_post (
	code varchar(64) not null,
	name varchar(64) not null,
	abstract varchar(128),
	description text,
	primary key (code)
);
insert into daemon_post (code, name, abstract, description) values
( 'CONTENT_KAPEL', 'AV Support', 'Mengtafel kennis gevraagd!', 'In de kapel zoeken we audio/video hulp.' ),
( 'CONTENT_NORMAL', 'Content Support', 'Talk/workshop begeleiding.', 'Helpen verzorgen van content.' ),
( 'KEEPER', 'Vliegende Keeper', 'Kampioen der willekeur.', 'Blussen van eenderwelk brandje, veel rondlopen!' ),
( 'FOOD', 'Food', 'Avondmaal-chefs.', 'Meehelpen met de keuken voor het avondeten.' ),
( 'INFODESK', 'Infodesk', 'Mensen helpen.', 'Infobalie bemannen, vragen beantwoorden.' ),
( 'BADGEDESK', 'EHBBO', 'Badge-problemen fixen.', 'Eerste hulp bij badge ongevallen.' ),
( 'BAR', 'De bar', 'Niet enkel tappen!', 'Meehelpen met de bar, die laatste shift kan even duren!' ),
( 'PARKING', 'Parkeerwacht', 'Wijs anderen de weg.', 'Voertuigen begeleiden, parkeerplaatsen organiseren.' ),
( 'NIGHTWATCH', 'Nachtwacht', 'Stilte-zoekers.', 'Snachts een oogje in het zeil houden.' ),
( 'BARFOOD', 'Eten voor de bar', 'Expert broodsmeerders.', 'De croques prepareren voor de bar.'),
( 'SANI', 'Sanitair', 'Grove borstels!', "The real deal. Ieder's held." );

drop table if exists daemon_slot;
create table daemon_slot (
	id integer auto_increment not null,
	daemon_day_code varchar(64),
	daemon_post_code varchar(64),
	slot_start datetime,
	slot_end datetime,
	n_needed integer default 0,
	primary key (id),
	constraint daemon_slot_daemon_day_code_fk foreign key (daemon_day_code) references daemon_day (code) on delete cascade on update cascade,
	constraint daemon_slot_daemon_post_code_fk foreign key (daemon_post_code) references daemon_post (code) on delete cascade on update cascade
);
insert into daemon_slot (daemon_day_code, daemon_post_code, slot_start, slot_end, n_needed) values
( 'VRIJDAG', 'CONTENT_KAPEL', '2022-08-12T13:30:00', '2022-08-12T15:30:00', 1 ),
( 'VRIJDAG', 'CONTENT_KAPEL', '2022-08-12T20:00:00', '2022-08-12T22:00:00', 1 ),
( 'ZATERDAG', 'CONTENT_KAPEL', '2022-08-13T10:30:00', '2022-08-13T12:30:00', 1 ),
( 'ZATERDAG', 'CONTENT_KAPEL', '2022-08-13T13:00:00', '2022-08-13T15:00:00', 1 ),
( 'ZATERDAG', 'CONTENT_KAPEL', '2022-08-13T20:00:00', '2022-08-13T22:00:00', 1 ),
( 'ZONDAG', 'CONTENT_KAPEL', '2022-08-14T10:30:00', '2022-08-14T12:30:00', 1 ),
( 'ZONDAG', 'CONTENT_KAPEL', '2022-08-14T13:00:00', '2022-08-14T15:00:00', 1 ),

( 'VRIJDAG', 'CONTENT_NORMAL', '2022-08-12T11:00:00', '2022-08-12T13:00:00', 6 ),
( 'VRIJDAG', 'CONTENT_NORMAL', '2022-08-12T13:30:00', '2022-08-12T15:30:00', 5 ),
( 'VRIJDAG', 'CONTENT_NORMAL', '2022-08-12T16:00:00', '2022-08-12T18:00:00', 6 ),
( 'ZATERDAG', 'CONTENT_NORMAL', '2022-08-13T10:30:00', '2022-08-13T12:30:00', 6 ),
( 'ZATERDAG', 'CONTENT_NORMAL', '2022-08-13T13:00:00', '2022-08-13T15:00:00', 6 ),
( 'ZATERDAG', 'CONTENT_NORMAL', '2022-08-13T15:00:00', '2022-08-13T17:00:00', 6 ),
( 'ZONDAG', 'CONTENT_NORMAL', '2022-08-14T10:30:00', '2022-08-14T12:30:00', 6 ),
( 'ZONDAG', 'CONTENT_NORMAL', '2022-08-14T13:00:00', '2022-08-14T15:00:00', 4 ),

( 'DONDERDAG', 'KEEPER', '2022-08-11T18:00:00', '2022-08-11T20:00:00', 3 ),
( 'DONDERDAG', 'KEEPER', '2022-08-11T20:00:00', '2022-08-11T22:00:00', 2 ),
( 'VRIJDAG', 'KEEPER', '2022-08-12T09:00:00', '2022-08-12T11:00:00', 2 ),
( 'VRIJDAG', 'KEEPER', '2022-08-12T11:00:00', '2022-08-12T13:00:00', 2 ),
( 'VRIJDAG', 'KEEPER', '2022-08-12T13:00:00', '2022-08-12T15:00:00', 2 ),
( 'VRIJDAG', 'KEEPER', '2022-08-12T15:00:00', '2022-08-12T17:00:00', 2 ),
( 'VRIJDAG', 'KEEPER', '2022-08-12T17:00:00', '2022-08-12T19:00:00', 2 ),
( 'ZATERDAG', 'KEEPER', '2022-08-13T09:00:00', '2022-08-13T11:00:00', 2 ),
( 'ZATERDAG', 'KEEPER', '2022-08-13T11:00:00', '2022-08-13T13:00:00', 2 ),
( 'ZATERDAG', 'KEEPER', '2022-08-13T13:00:00', '2022-08-13T15:00:00', 2 ),
( 'ZATERDAG', 'KEEPER', '2022-08-13T15:00:00', '2022-08-13T17:00:00', 2 ),
( 'ZATERDAG', 'KEEPER', '2022-08-13T17:00:00', '2022-08-13T19:00:00', 2 ),
( 'ZONDAG', 'KEEPER', '2022-08-14T09:00:00', '2022-08-14T11:00:00', 2 ),
( 'ZONDAG', 'KEEPER', '2022-08-14T11:00:00', '2022-08-14T13:00:00', 2 ),
( 'ZONDAG', 'KEEPER', '2022-08-14T13:00:00', '2022-08-14T15:00:00', 2 ),

( 'VRIJDAG', 'FOOD', '2022-08-12T15:00:00', '2022-08-12T17:00:00', 3 ),
( 'VRIJDAG', 'FOOD', '2022-08-12T17:00:00', '2022-08-12T19:00:00', 8 ),
( 'VRIJDAG', 'FOOD', '2022-08-12T19:00:00', '2022-08-12T21:00:00', 8 ),
( 'ZATERDAG', 'FOOD', '2022-08-13T13:00:00', '2022-08-13T15:00:00', 10 ),
( 'ZATERDAG', 'FOOD', '2022-08-13T15:00:00', '2022-08-13T17:00:00', 10 ),
( 'ZATERDAG', 'FOOD', '2022-08-13T17:00:00', '2022-08-13T19:00:00', 10 ),
( 'ZATERDAG', 'FOOD', '2022-08-13T19:00:00', '2022-08-13T21:00:00', 10 ),

( 'DONDERDAG', 'INFODESK', '2022-08-11T17:00:00', '2022-08-11T19:00:00', 4),
( 'DONDERDAG', 'INFODESK', '2022-08-11T19:00:00', '2022-08-11T21:00:00', 3),
( 'VRIJDAG', 'INFODESK', '2022-08-12T08:00:00', '2022-08-12T10:00:00', 3),
( 'VRIJDAG', 'INFODESK', '2022-08-12T10:00:00', '2022-08-12T12:00:00', 2),
( 'VRIJDAG', 'INFODESK', '2022-08-12T12:00:00', '2022-08-12T14:00:00', 2),
( 'VRIJDAG', 'INFODESK', '2022-08-12T14:00:00', '2022-08-12T16:00:00', 2),
( 'VRIJDAG', 'INFODESK', '2022-08-12T16:00:00', '2022-08-12T18:00:00', 2),
( 'VRIJDAG', 'INFODESK', '2022-08-12T18:00:00', '2022-08-12T20:00:00', 1),
( 'VRIJDAG', 'INFODESK', '2022-08-12T20:00:00', '2022-08-12T22:00:00', 1),
( 'ZATERDAG', 'INFODESK', '2022-08-13T08:00:00', '2022-08-13T10:00:00', 1),
( 'ZATERDAG', 'INFODESK', '2022-08-13T10:00:00', '2022-08-13T12:00:00', 2),
( 'ZATERDAG', 'INFODESK', '2022-08-13T12:00:00', '2022-08-13T14:00:00', 2),
( 'ZATERDAG', 'INFODESK', '2022-08-13T14:00:00', '2022-08-13T16:00:00', 2),
( 'ZATERDAG', 'INFODESK', '2022-08-13T16:00:00', '2022-08-13T18:00:00', 2),
( 'ZATERDAG', 'INFODESK', '2022-08-13T18:00:00', '2022-08-13T20:00:00', 1),
( 'ZATERDAG', 'INFODESK', '2022-08-13T20:00:00', '2022-08-13T22:00:00', 1),
( 'ZONDAG', 'INFODESK', '2022-08-14T08:00:00', '2022-08-14T10:00:00', 1),
( 'ZONDAG', 'INFODESK', '2022-08-14T10:00:00', '2022-08-14T12:00:00', 2),
( 'ZONDAG', 'INFODESK', '2022-08-14T12:00:00', '2022-08-14T14:00:00', 2),

( 'DONDERDAG', 'BADGEDESK', '2022-08-11T19:00:00', '2022-08-11T21:00:00', 2),
( 'VRIJDAG', 'BADGEDESK', '2022-08-12T10:00:00', '2022-08-12T12:00:00', 2),
( 'VRIJDAG', 'BADGEDESK', '2022-08-12T12:00:00', '2022-08-12T14:00:00', 2),
( 'VRIJDAG', 'BADGEDESK', '2022-08-12T14:00:00', '2022-08-12T16:00:00', 2),
( 'VRIJDAG', 'BADGEDESK', '2022-08-12T16:00:00', '2022-08-12T18:00:00', 2),
( 'ZATERDAG', 'BADGEDESK', '2022-08-13T10:00:00', '2022-08-13T12:00:00', 2),
( 'ZATERDAG', 'BADGEDESK', '2022-08-13T12:00:00', '2022-08-13T14:00:00', 2),
( 'ZATERDAG', 'BADGEDESK', '2022-08-13T14:00:00', '2022-08-13T16:00:00', 2),
( 'ZATERDAG', 'BADGEDESK', '2022-08-13T16:00:00', '2022-08-13T18:00:00', 2),
( 'ZONDAG', 'BADGEDESK', '2022-08-14T10:00:00', '2022-08-14T12:00:00', 2),
( 'ZONDAG', 'BADGEDESK', '2022-08-14T12:00:00', '2022-08-14T14:00:00', 2),

( 'DONDERDAG', 'BAR', '2022-08-11T18:00:00', '2022-08-11T20:00:00', 3),
( 'DONDERDAG', 'BAR', '2022-08-11T20:00:00', '2022-08-11T22:00:00', 3),
( 'DONDERDAG', 'BAR', '2022-08-11T22:00:00', '2022-08-11T23:59:59', 3),
( 'VRIJDAG', 'BAR', '2022-08-12T00:00:00', '2022-08-12T04:00:00', 2),
( 'VRIJDAG', 'BAR', '2022-08-12T08:00:00', '2022-08-12T10:00:00', 2),
( 'VRIJDAG', 'BAR', '2022-08-12T10:00:00', '2022-08-12T12:00:00', 3),
( 'VRIJDAG', 'BAR', '2022-08-12T12:00:00', '2022-08-12T14:00:00', 5),
( 'VRIJDAG', 'BAR', '2022-08-12T14:00:00', '2022-08-12T16:00:00', 3),
( 'VRIJDAG', 'BAR', '2022-08-12T16:00:00', '2022-08-12T18:00:00', 3),
( 'VRIJDAG', 'BAR', '2022-08-12T18:00:00', '2022-08-12T20:00:00', 3),
( 'VRIJDAG', 'BAR', '2022-08-12T20:00:00', '2022-08-12T22:00:00', 3),
( 'VRIJDAG', 'BAR', '2022-08-12T22:00:00', '2022-08-12T23:59:59', 3),
( 'ZATERDAG', 'BAR', '2022-08-13T00:00:00', '2022-08-13T04:00:00', 2),
( 'ZATERDAG', 'BAR', '2022-08-13T08:00:00', '2022-08-13T10:00:00', 2),
( 'ZATERDAG', 'BAR', '2022-08-13T10:00:00', '2022-08-13T12:00:00', 3),
( 'ZATERDAG', 'BAR', '2022-08-13T12:00:00', '2022-08-13T14:00:00', 5),
( 'ZATERDAG', 'BAR', '2022-08-13T14:00:00', '2022-08-13T16:00:00', 3),
( 'ZATERDAG', 'BAR', '2022-08-13T16:00:00', '2022-08-13T18:00:00', 3),
( 'ZATERDAG', 'BAR', '2022-08-13T18:00:00', '2022-08-13T20:00:00', 3),
( 'ZATERDAG', 'BAR', '2022-08-13T20:00:00', '2022-08-13T22:00:00', 3),
( 'ZATERDAG', 'BAR', '2022-08-13T22:00:00', '2022-08-13T23:59:59', 3),
( 'ZONDAG', 'BAR', '2022-08-14T00:00:00', '2022-08-14T04:00:00', 2),
( 'ZONDAG', 'BAR', '2022-08-14T08:00:00', '2022-08-14T10:00:00', 2),
( 'ZONDAG', 'BAR', '2022-08-14T10:00:00', '2022-08-14T12:00:00', 3),
( 'ZONDAG', 'BAR', '2022-08-14T12:00:00', '2022-08-14T14:00:00', 5),
( 'ZONDAG', 'BAR', '2022-08-14T14:00:00', '2022-08-14T16:00:00', 2),

( 'DONDERDAG', 'PARKING', '2022-08-11T17:00:00', '2022-08-11T19:00:00', 3),
( 'DONDERDAG', 'PARKING', '2022-08-11T19:00:00', '2022-08-11T21:00:00', 3),
( 'VRIJDAG', 'PARKING', '2022-08-12T08:00:00', '2022-08-12T10:00:00', 3),

( 'VRIJDAG', 'NIGHTWATCH', '2022-08-12T00:00:00', '2022-08-12T08:00:00', 2),
( 'ZATERDAG', 'NIGHTWATCH', '2022-08-13T00:00:00', '2022-08-13T08:00:00', 2),
( 'ZONDAG', 'NIGHTWATCH', '2022-08-14T00:00:00', '2022-08-14T08:00:00', 2),

( 'VRIJDAG', 'BARFOOD', '2022-08-12T10:00:00', '2022-08-12T12:00:00', 2),
( 'ZATERDAG', 'BARFOOD', '2022-08-13T10:00:00', '2022-08-13T12:00:00', 2),
( 'ZONDAG', 'BARFOOD', '2022-08-14T10:00:00', '2022-08-14T12:00:00', 2),

( 'VRIJDAG', 'SANI', '2022-08-12T10:00:00', '2022-08-12T12:00:00', 4),
( 'VRIJDAG', 'SANI', '2022-08-12T19:00:00', '2022-08-12T21:00:00', 4),
( 'ZATERDAG', 'SANI', '2022-08-13T10:00:00', '2022-08-13T12:00:00', 4),
( 'ZATERDAG', 'SANI', '2022-08-13T19:00:00', '2022-08-13T21:00:00', 4),
( 'ZONDAG', 'SANI', '2022-08-14T10:00:00', '2022-08-14T12:00:00', 4),
( 'ZONDAG', 'SANI', '2022-08-14T19:00:00', '2022-08-14T21:00:00', 4);


drop table if exists daemon_commit;
create table daemon_commit (
	id integer auto_increment not null,
	daemon_slot_id integer,
	purchase_items_id integer,
	primary key (id),
	constraint daemon_commit_daemon_slot_id_fk foreign key (daemon_slot_id) references daemon_slot (id) on delete cascade on update cascade,
	constraint daemon_commit_purchase_items_id_fk foreign key (purchase_items_id) references purchase_items (id) on delete cascade on update cascade
);

drop table if exists shift_time;
create table shift_time (
	id integer auto_increment not null,
	description varchar(64) not null,
	day integer not null,
	primary key (id)
);
drop table if exists shift_post;
create table shift_post (
	id integer auto_increment not null,
	what varchar(64) not null,
	description text,
	primary key (id)
);
drop table if exists `shift`;
create table `shift` (
	id integer auto_increment not null,
	shift_time_id integer,
	shift_post_id integer,
	persons integer,
	comments text,
	primary key (id),
	constraint shift_shift_time_id_fk foreign key (shift_time_id) references shift_time (id) on delete set null on update cascade,
	constraint shift_shift_post_id_fk foreign key (shift_post_id) references shift_post (id) on delete set null on update cascade
);

drop table if exists shift_volunteer;
create table shift_volunteer (
	id integer auto_increment not null,
	purchase_items_id integer,
	shift_id integer,
	primary key (id),
	constraint shift_volunteer_shift_id_fk foreign key (shift_id) references shift (id) on delete set null on update cascade,
	constraint shift_volunteer_purchase_items_id_fk foreign key (purchase_items_id) references purchase_items (id) on delete set null on update cascade
);

insert into shift_time (description, day) values
	( 'Vrijdag 15:00 - 18:00', 1),
	( 'Vrijdag 18:00 - 21:00', 1 ),
	( 'Vrijdag 21:00 - einde', 1 ),
	( 'Zaterdag 09:00 - 12:00', 2 ),
	( 'Zaterdag 12:00 - 15:00', 2 ),
	( 'Zaterdag 15:00 - 18:00', 2 ),
	( 'Zaterdag 18:00 - 21:00', 2 ),
	( 'Zaterdag 21:00 - einde', 2 ),
	( 'Zondag 09:00 - 12:00', 3 ),
	( 'Zondag 12:00 - 15:00', 3 ),
	( 'Zondag 15:00 - 18:00', 3 ),
	( 'Zondag 18:00 - 21:00', 3 ),
	( 'Zondag 21:00 - einde', 3 ),
	( 'Maandag 09:00 - 12:00', 4 ),
	( 'Maandag 12:00 - 15:00', 4 ),
	( 'Maandag 15:00 - 18:00', 4 );

insert into shift_post (what, description) values
	( 'Inkom', 'Toegangscontrole, mensen doorverwijzen naar infobalie.' ),
	( 'Parkeerwachter', 'Mensen naar parkingplaatsen gidsen.' ),
	( 'Vliegende keeper', 'Enkel de meest willekeurige taken zijn goed genoeg voor de vliegende keeper! Mensen zoeken, gasten doorverwijzen, last minute patches...' ),
	( 'Infodesk', 'Toekomers ontvangen, vragen beantwoorden, tokens verkopen, special guests en content bri      ngers van informatie voorzien, oogje op de meteo houden.'),
	( 'Nachtwacht', 'Oogje op de nachtelijke vrede houden.'),
	( 'EHB(R/B)O', 'Badge problemen helpen oplossen.'),
	( 'Bar Blokhut', 'De bar bemannen (blokhut)'),
	( 'Bar Mainstage', 'De bar bemannen (mainstage)'),
	( 'Bar Hoofdgebouw', 'De bar bemannen (hoofdgebouw)'),
	( 'Food', 'Frieten bakken!'),
	( 'Workshop support', 'Workshops bijstaan en gidsen.');

insert into `shift` (shift_time_id, shift_post_id, persons) values
	( 1, 1, 2 ),
	( 1, 2, 2 ),
	( 1, 6, 1 ),

	( 2, 1, 2 ),
	( 2, 2, 2 ),
	( 2, 6, 1 ),

	( 3, 1, 2 ),
	( 3, 2, 2 ),
	( 3, 3, 1 ),
	( 3, 6, 1 ),

	( 4, 1, 2 ),
	( 4, 2, 2 ),
	( 4, 3, 1 ),
	( 4, 5, 3 ),

	( 5, 1, 2 ),
	( 5, 2, 2 ),
	( 5, 3, 1 ),
	( 5, 4, 4 ),
	( 5, 5, 3 ),

	( 6, 1, 2 ),
	( 6, 2, 1 ),
	( 6, 3, 1 ),
	( 6, 4, 8 ),

	( 7, 1, 2 ),
	( 7, 2, 1 ),
	( 7, 3, 1 ),

	( 8, 1, 2 ),
	( 8, 2, 2 ),
	( 8, 3, 1 ),
	( 8, 5, 3 ),

	( 9, 1, 2 ),
	( 9, 2, 2 ),
	( 9, 3, 1 ),
	( 9, 5, 3 ),

	( 10, 1, 2 ),
	( 10, 2, 2 ),
	( 10, 3, 1 ),
	( 10, 4, 4 ),
	( 10, 5, 3 ),

	( 11, 1, 2 ),
	( 11, 2, 1 ),
	( 11, 3, 1 ),
	( 11, 4, 8 ),

	( 12, 1, 2 ),
	( 12, 2, 1 ),
	( 12, 3, 1 ),

	( 13, 1, 2 ),
	( 13, 2, 2 ),
	( 13, 3, 1 ),
	( 13, 5, 3 ),

	( 14, 1, 2 ),
	( 14, 2, 2 ),
	( 14, 3, 1 ),
	( 14, 5, 3 ),
	( 14, 6, 1 ),

	( 15, 1, 2 ),
	( 15, 2, 2 ),
	( 15, 3, 1 ),
	( 15, 6, 1 ),

	( 16, 1, 2 ),
	( 16, 2, 1 ),
	( 16, 3, 1 ),
	( 16, 6, 1 );


