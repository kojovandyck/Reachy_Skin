#!/bin/sh
':' //; exec "$(command -v nodejs || command -v node)" "$0" "$@"
"use strict";

//Parameters:

const startingWidth = 40;
const endingWidth = 40 - 4;
const height = 40;
const carrier = ['3'];

//Operation:

//Makes a swatch of plain knitting that gradually decreases on an angle on the left side on the front bed with carrier carrier.
//Uses an alternating-tucks cast-on.
/*
    x
    x
    x
   xx
  xxx
 xxxx
xxxxx  

*/


console.log(";!knitout-2")
console.log(";;Carriers: 1 2 3 4 5 6 7 8 9 10")
console.log(";;Position: Keep")


//Alternating tucks cast-on:

console.log("inhook " + carrier);

let min = 1;
let max = min + startingWidth - 1;
let actingWidth = min;

for (let n = max; n >= min; --n) {
	if ((max-n) % 2 == 0) {
		console.log("tuck - f" + n + " " + carrier);
	}
}
for (let n = min; n <= max; ++n) {
	if ((max-n)%2 == 1) {
		console.log("tuck + f" + n + " " + carrier);
	}
}

console.log("miss + f" + max + " " + carrier);

//release the yarn from the carrier hook
console.log("releasehook " + carrier);


for (let r = 0; r < height; ++r) {

	//if we should decrease the width
	if (actingWidth < endingWidth){
		//and we're going towards the right, we're going to attempt to secure some stitches
		if (r % 2 == 1){
			//first, transfer them to the back bed
			console.log("xfer f" + actingWidth + " b" + actingWidth + "\n");
			//then move the back bed right one space
			console.log("rack 1" + "\n");
			//then transfer the stitch back to the front
			console.log("xfer b" + actingWidth + " f" + (actingWidth + 1) + "\n");
			//and return the back bed to its starting position
			console.log("rack 0" + "\n");
			actingWidth++;
		}
	}

	//knit normally, alternating between back and front
	if (r % 2 == 0) {
		for (let n = max; n >= actingWidth; --n) {
			console.log("knit - f" + n + " " + carrier + "\n");
		}
	} else {
		for (let n = actingWidth; n <= max; ++n) {
			console.log("knit + f" + n + " " + carrier + "\n");
		}
	}
}

console.log("outhook " + carrier);
