#!/bin/sh
':' //; exec "$(command -v nodejs || command -v node)" "$0" "$@"
"use strict";

const width = 30; //must be even
const height = 40;
const carrier = ['3'];

//Operation:

//Makes a width x height rectangle of full-cardigan knitting on the front bed with carrier carrier.
//Uses an alternating-tucks cast-on.


console.log(";!knitout-2")
console.log(";;Carriers: 1 2 3 4 5 6 7 8 9 10")
console.log(";;Position: Keep")


//Alternating tucks cast-on:

console.log("inhook " + carrier);

let min = 1;
let max = min + width - 1;

//the knit alternates between knit front and tuck back in the first line
//so when we cast on, we want to make sure our tuck cast-on alternates tuck front/tuck back in the same order
for (let n = max; n >= min; --n) {
	if ((max-n) % 2 == 0) {
		console.log("tuck - f" + n + " " + carrier);
	}
}
for (let n = min; n <= max; ++n) {
	if ((max-n)%2 == 1) {
		console.log("tuck + b" + n + " " + carrier);
	}
}

console.log("miss + f" + max + " " + carrier);

console.log("releasehook " + carrier);

//note: we might have to knit a row of plain knitting here between the cast-on tucks and the knit tucks

for (let r = 0; r < height; ++r) {
	if (r % 2 == 0) {
		//alternate between front knits and back tucks on alternating rows going towards the left
		for (let n = max; n >= min; --n) {
			if (n % 2 === 0){
				console.log("knit - f" + n + " " + carrier);
			} else {
				//knit rather than tuck on far edges to prevent error
				if (n == min){
					console.log("knit - b" + n + " " + carrier);
				} else {
					console.log("tuck - b" + n + " " + carrier);
				}
			}
		}
	} else {
		//alternate between back knits and front tucks on alternating rows going towards the right
		for (let n = min; n <= max; ++n) {
			if (n % 2 === 1){
				console.log("knit + b" + n + " " + carrier);
			} else {
				//knit rather than tuck on far edges to prevent error
				if (n == max){
					console.log("knit + f" + n + " " + carrier);
				} else {
					console.log("tuck + f" + n + " " + carrier);
				}
			}
		}
	}



}


console.log("outhook " + carrier);

