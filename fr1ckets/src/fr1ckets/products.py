# -*- coding: utf-8 -*-

clothing_sizes = {
	"kids" : [
		["xs","3-4j"],
		["s","5-6j"],
		["m","7-8j"],
		["l","9-11j"],
		["xl","12-14j"]
	],
	"default" : [
		["xs","XS"],
		["s","S"],
		["m","M"],
		["l","L"],
		["xl","XL"]
	],
	"full_m" : [
		["xxs","XXS"],
		["xs","XS"],
		["s","S"],
		["m","M"],
		["l","L"],
		["xl","XL"],
		["xxl","XXL"],
		["3xl","XXXL"],
		["4xl","4XL"],
		["5xl","5XL"]
	],
	"sweater_uni" : [
		["xxs","XXS"],
		["xs","XS"],
		["s","S"],
		["m","M"],
		["l","L"],
		["xl","XL"],
		["xxl","XXL"],
		["3xl","XXXL"]
	]
}

size_tables = {
	"hoodie_kids" : {
		"image" : "size_hoodie_kids.png",
		"sizes" : [
			{
				"label" : "3-4",
				"A" : 35,
				"B" : 42,
				"C" : 36.5
			},
			{
				"label" : "5-6",
				"A" : 37,
				"B" : 46,
				"C" : 42
			},
			{
				"label" : "7-8",
				"A" : 39,
				"B" : 51.5,
				"C" : 48
			},
			{
				"label" : "9-11",
				"A" : 43,
				"B" : 57.5,
				"C" : 54
			},
			{
				"label" : "12-14",
				"A" : 46,
				"B" : 62.5,
				"C" : 59
			}
		]
	},
	"tshirt_kids" : {
		"image" : "size_tshirt_kids.png",
		"sizes" : [
			{
				"label" : "3-4",
				"A" : 33,
				"B" : 42,
				"C" : 11.5
			},
			{
				"label" : "5-6",
				"A" : 35,
				"B" : 46,
				"C" : 12.5
			},
			{
				"label" : "7-8",
				"A" : 37,
				"B" : 51.5,
				"C" : 14.5
			},
			{
				"label" : "9-11",
				"A" : 41,
				"B" : 57.5,
				"C" : 16.5
			},
			{
				"label" : "12-14",
				"A" : 44,
				"B" : 62.5,
				"C" : 18.5
			}
		]
	},
	"tshirt_m" : {
		"image" : "size_tshirt_m.png",
		"sizes" : [
			{
				"label" : "XXS",
				"A" : 43.5,
				"B" : 64,
				"C" : 19
			},
			{
				"label" : "XS",
				"A" : 46,
				"B" : 66,
				"C" : 19.5
			},
			{
				"label" : "S",
				"A" : 49,
				"B" : 69,
				"C" : 20.5
			},
			{
				"label" : "M",
				"A" : 52,
				"B" : 72,
				"C" : 21.5
			},
			{
				"label" : "L",
				"A" : 55,
				"B" : 74,
				"C" : 22.5
			},
			{
				"label" : "XL",
				"A" : 58,
				"B" : 76,
				"C" : 22.5
			},
			{
				"label" : "XXL",
				"A" : 61,
				"B" : 78,
				"C" : 23.5
			},
			{
				"label" : "3XL",
				"A" : 64,
				"B" : 80,
				"C" : 24.5
			},
			{
				"label" : "4XL",
				"A" : 69,
				"B" : 82,
				"C" : 24.5
			},
			{
				"label" : "5XL",
				"A" : 74,
				"B" : 84,
				"C" : 25
			}
		]
	},
	"hoodie_uni" : {
		"image" : "size_hoodie_uni.png",
		"sizes" : [
			{
				"label" : "XXS",
				"A" : 46.5,
				"B" : 63,
				"C" : 60.5
			},
			{
				"label" : "XS",
				"A" : 49,
				"B" : 65,
				"C" : 61.5
			},
			{
				"label" : "S",
				"A" : 51.5,
				"B" : 68,
				"C" : 64
			},
			{
				"label" : "M",
				"A" : 54,
				"B" : 72,
				"C" : 65.5
			},
			{
				"label" : "L",
				"A" : 57,
				"B" : 74,
				"C" : 67
			},
			{
				"label" : "XL",
				"A" : 60,
				"B" : 76,
				"C" : 68.5
			},
			{
				"label" : "XXL",
				"A" : 63,
				"B" : 78,
				"C" : 70
			},
			{
				"label" : "3XL",
				"A" : 66,
				"B" : 80,
				"C" : 70
			},
			{
				"label" : "4XL",
				"A" : 71,
				"B" : 82,
				"C" : 70
			},
			{
				"label" : "5XL",
				"A" : 76,
				"B" : 83,
				"C" : 70
			}
		]
	},
	"sweater_uni" : {
		"image" : "size_sweater_uni.png",
		"sizes" : [
			{
				"label" : "XXS",
				"A" : 51.5,
				"B" : 62,
				"C" : 57.5
			},
			{
				"label" : "XS",
				"A" : 54,
				"B" : 63,
				"C" : 58.5
			},
			{
				"label" : "S",
				"A" : 56.5,
				"B" : 66,
				"C" : 61.5
			},
			{
				"label" : "M",
				"A" : 59,
				"B" : 70,
				"C" : 64
			},
			{
				"label" : "L",
				"A" : 62,
				"B" : 72,
				"C" : 65.5
			},
			{
				"label" : "XL",
				"A" : 65,
				"B" : 74,
				"C" : 67
			},
			{
				"label" : "XXL",
				"A" : 68,
				"B" : 76,
				"C" : 68.5
			},
			{
				"label" : "3XL",
				"A" : 71,
				"B" : 79,
				"C" : 68.5
			}
		]
	},
	"tshirt_f" : {
		"image" : "size_tshirt_f.png",
		"sizes" : [
			{
				"label" : "XS",
				"A" : 45.5,
				"B" : 62,
				"C" : 19.5
			},
			{
				"label" : "S",
				"A" : 48,
				"B" : 64,
				"C" : 20
			},
			{
				"label" : "M",
				"A" : 51,
				"B" : 66,
				"C" : 21
			},
			{
				"label" : "L",
				"A" : 54,
				"B" : 68,
				"C" : 21.5
			},
			{
				"label" : "XL",
				"A" : 57,
				"B" : 69,
				"C" : 22
			}
		]
	}
}

products = {
	"simple" : [
		{
			"name" : "badge_accessory_a",
			"label" : "Time Blaster",
			"price" : 20,
			"images" : [
				"badge_accessory_a.png"
			],
			"description" : "<p>Altijd al jouw eigen lasertag willen maken? Het kan nu op Fri3d camp! Als uitbreiding op de badge, maar ook als standalone, heeft het badge team een blaster ontwikkeld als soldeerkit. Deze volledige Arduino compatibele kit is opgebouwd uit makkelijk zelf te solderen componenten. Voor de durvers zijn er uitbreidingen met RGB LEDs en een USB interface voorzien in de kit waar toch enige vorm van geduld en een vast hand vereist zijn.</p><p>Zelf te solderen!</p>"
		},
		{
			"name" : "badge_accessory_b",
			"label" : "GameOn",
			"price" : 12,
			"images" : [
				"badge_accessory_b.jpg"
			],
			"description" : "<p>Get your game on met deze gaming add-on voor de badge. Door zijn iconische layout met een joystick en 4 druktoesten kan je heel makkelijk games ontwikkelen en spelen op de Fri3d badge! Tevens voorzien we deze add-on van Micro-SD kaart slot zodat er plaats genoeg is om alle games op te slaan. Some assembly required, maar anders zou het niet plezant zijn h&eacute;!</p><p>Zelf te solderen!</p>"
		},
		{
			"name" : "mug",
			"label" : "Emaille mok",
			"price" : 10,
			"max_n" : 5,
			"images" : [
				"mug.jpg"
			],
			"description" : "Drink op Fri3d Camp je ochtendkoffie in stijl met deze ge&euml;mailleerde mok. Staat nadien ook prachtig als souvenir op je bureau!"
		}
	],
	"clothing" : [
		{
			"name": "hoodie_kids",
			"label" : "Hoodie kinderen (vos)",
			"price" : 40,
			"images" : [
				"hoodie_kids.jpg"
			],
			"description" : "<p>Deze topkwaliteit hoodie is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp hoodie is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Geborstelde molton, 85&#37; Gesponnen en gekamd biologisch katoen, 15&#37; Gerecycled polyester, Gewassen stof, Zachte stof, 300 g/m&sup2; </p>",
			"sizes" : "kids",
			"size_table_ref" : "hoodie_kids"
		},
		{
			"name": "tshirt_kids_teal",
			"label" : "T-shirt kinderen (vos)",
			"price" : 20,
			"images" : [
				"tshirt_kids_teal.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp hoodie is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen stof, 155 g/&sup2; </p>",
			"sizes" : "kids",
			"size_table_ref" : "tshirt_kids"
		},
		{
			"name": "tshirt_kids_black",
			"label" : "T-shirt kinderen (zwart)",
			"price" : 20,
			"images" : [
				"tshirt_kids_black.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp T-shirt is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen stof, 155 g/m&sup2; </p>",
			"sizes" : "kids",
			"size_table_ref" : "tshirt_kids"
		},
		{
			"name": "tshirt_f",
			"label" : "T-shirt vrouwenmodel",
			"price" : 20,
			"images" : [
				"tshirt_f.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp T-shirt is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Gevlamde, enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen panelen, 130 g/m&sup2; </p>",
			"sizes" : "default",
			"size_table_ref" : "tshirt_f"
		},
		{
			"name": "tshirt_m",
			"label" : "T-shirt",
			"price" : 20,
			"images" : [
				"tshirt_m.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp T-shirt is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen stof, 180 g/m&sup2; </p>",
			"sizes" : "full_m",
			"size_table_ref" : "tshirt_m"
		},
		{
			"name": "hoodie_uni",
			"label" : "Unisex hoodie",
			"price" : 45,
			"images" : [
				"hoodie_uni.jpg"
			],
			"description" : "<p>Deze topkwaliteit hoodie is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp hoodie is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Geborstelde molton, 85&#37; Gesponnen en gekamd biologisch katoen, 15&#37; Gerecycled polyester, Gewassen stof, Zachte stof, 350 g/m&sup2; </p>",
			"sizes" : "full_m",
			"size_table_ref" : "hoodie_uni"
		},
		{
			"name": "sweater_uni",
			"label" : "Unisex sweater",
			"price" : 45,
			"images" : [
				"sweater_uni.jpg"
			],
			"description" : "<p>Deze topkwaliteit sweater is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp sweater is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Geborstelde molton, 85&#37; Gesponnen en gekamd biologisch katoen, 15&#37; Gerecycled polyester, Gewassen stof, Zachte stof, 350 g/m&sup2; </p>",
			"sizes" : "sweater_uni",
			"size_table_ref" : "sweater_uni"
		}
	]
}
