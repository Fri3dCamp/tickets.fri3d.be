# -*- coding: utf-8 -*-

clothing_sizes = {
	"kids" : [
		["3_4","3-4j"],
		["5_6","5-6j"],
		["7_8","7-8j"],
		["9_11","9-11j"],
		["12_14","12-14j"]
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
	"sweater" : [
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
products = {
	"simple" : [
		{
			"name" : "badge_accessory_a",
			"label" : "Time Blaster",
			"price" : 20,
			"images" : [
				"badge_accessory_a.jpg"
			],
			"description" : "<p>Altijd al jouw eigen lasertag willen maken? Het kan nu op fri3d camp! Als uitbreiding op de badge, maar ook als standalone, heeft het badge team een blaster ontwikkeld als soldeerkit. Deze volledige Arduino compatibele kit is opgebouwd uit makkelijk te solderen componenten. Voor de durvers zijn er uitbreidingen met RGB LEDs en een USB interface voorzien in de kit waar toch enige vorm van geduld en een vast hand vereist zijn.</p>"
		},
		{
			"name" : "mug",
			"label" : "Emaille mok",
			"price" : 15,
			"max_n" : 5,
			"images" : [
				"mug.jpg"
			],
			"description" : "Drink op Fri3d Camp je ochtendkoffie in stijl met deze ge&euml;mailleerde mok. Staat nadien ook prachtig als souvenir op je bureau!"
		}
	],
	"clothing" : [
		{
			"name": "hoodie_kids_teal",
			"label" : "Hoodie kinderen (vos)",
			"price" : 40,
			"images" : [
				"hoodie_kids_teal.jpg"
			],
			"description" : "<p>Deze topkwaliteit hoodie is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp hoodie is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Geborstelde molton, 85&#37; Gesponnen en gekamd biologisch katoen, 15&#37; Gerecycled polyester, Gewassen stof, Zachte stof, 300 g/m&sup2; </p>",
			"sizes" : "kids"
		},
		{
			"name": "tee_kids_teal",
			"label" : "T-shirt kinderen (vos)",
			"price" : 20,
			"images" : [
				"tee_kids_teal.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp hoodie is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen stof, 155 g/&sup2; </p>",
			"sizes" : "kids"
		},
		{
			"name": "tee_kids_zwart",
			"label" : "T-shirt kinderen (zwart)",
			"price" : 20,
			"images" : [
				"tee_kids_zwart.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp T-shirt is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen stof, 155 g/m&sup2; </p>",
			"sizes" : "kids"
		},
		{
			"name": "tee_f",
			"label" : "T-shirt vrouwenmodel",
			"price" : 20,
			"images" : [
				"tee_f.jpg"
			],
			"description" : "<p>Dit topkwaliteit T-shirt is van het Belgische Stanley & Stella, een merk met veel aandacht voor duurzaamheid en een transparant productieproces. Je Fri3d Camp T-shirt is geen promo-wear, maar gemaakt om lang van te genieten en &eacute;cht te gebruiken.</p><p>Shell: Enkelvoudige jersey, 100&#37; Gesponnen en gekamd biologisch katoen, Gewassen stof, 155 g/m&sup2; </p>",
			"sizes" : "default"
		}
	]
}