#!/bin/sh
':' //; exec "$(command -v nodejs || command -v node)" "$0" "$@"
"use strict";
//Parameters:

const width = 36;
const carrier = ["3"];

let rowsPerStep = 2; //how many rows knitted at each stepWidth. Pretty sure this has to be a multiple of 2
let stepWidth = 4; //how many rows we decrease per step
let numCurves = 6; //number of triangles we want to make
const height = Math.min(width/stepWidth) * rowsPerStep * numCurves; //calculate the height based on other parameters


//Operation:

//Makes a curving piece of joined fabric made of plain knitting on the front bed with carrier carrier.
//Uses an alternating-tucks cast-on.

/*
In DAT viewer appears as:

xxx
xxx
xxxx
xxxx
xxxxx
xxxxx
xxx
xxx
xxxx
xxxx
xxxxx
xxxxx
xxx
xxx
xxxx
xxxx
xxxxx
xxxxx

(repeated according to num curves)

*/


console.log(";!knitout-2")
console.log(";;Carriers: 1 2 3 4 5 6 7 8 9 10")
console.log(";;Position: Keep")

console.log("inhook " + carrier);

let min = 1;
let max = min + width - 1;

//alternating tucks cast-on
for (let column = max; column >= min; --column) {
	if ((max - column) % 2 == 0) {
		console.log("tuck - f" + column + " " + carrier);
	}
}
for (let column = min; column <= max; ++column) {
	if ((max - column)%2 == 1) {
		console.log("tuck + f" + column + " " + carrier);
	}
}

console.log("miss + f" + max + " " + carrier);

//release the hook from the carrier hook
console.log("releasehook " + carrier);


//direction is important, so let's start with a row knitting towards the left to put us in the correct direction
for (let column = max; column >= min; --column) {
	console.log("knit - f" + column + " " + carrier);
}

//for each curved segment...
for (let curve = 0; curve < numCurves; curve ++) {
	//calculate how many times we have to decrease the width by stepWidth
	let steps = Math.min(width/stepWidth);
	//for each change in width...
	for (let step = 0; step < steps; step ++){
		//calculate the width of the row based on how many "steps" we're at in the curve
		let rowWidth = max - step * stepWidth;
		//knit back and forth stepWidth times at each given width
		for (let row = 0; row < rowsPerStep; row ++){
			//direction is important, so we want to start our first row in the curve going right (+)
			if (row % 2 == 1) {
				for (let column = rowWidth; column >= min; --column) {
					console.log("knit - f" + column + " " + carrier);
				}
			} else {
				for (let column = min; column <= rowWidth; ++column) {
					console.log("knit + f" + column + " " + carrier);
				}
			}
		}
	}
}

//bring yarn carrier out of action
console.log("outhook " + carrier);
