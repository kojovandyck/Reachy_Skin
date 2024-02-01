#!/bin/sh
':' //; exec "$(command -v nodejs || command -v node)" "$0" "$@"
"use strict";


const carrier = ['3'];


//Parameters:
const width = 16;
const height = 80;

console.log(";!knitout-2")
console.log(";;Carriers: 1 2 3 4 5 6 7 8 9 10")
console.log(";;Position: Keep")

let min = 1;
let max = min + width - 1;


console.log("inhook " + carrier);

//cast-on on the front bed first...
for (let n = max; n >= min; --n) {
	if ((max-n) % 4 == 0) {
        console.log("tuck - f" + n + " " + carrier);
	}
}

for (let n = min; n <= max; ++n) {
	if ((max-n)%4 == 2) {
        console.log("tuck + f" + n + " " + carrier);
    }
}


//and then on the back bed
for (let n = max; n >= min; --n) {
	if ((max-n) % 4 == 0) {
        console.log("tuck - b" + n + " " + carrier);
    }
}
for (let n = min; n <= max; ++n) {
	if ((max-n)%4 == 2) {
        console.log("tuck + b" + n + " " + carrier);
    }
}

console.log("miss + f" + max + " " + carrier);

console.log("releasehook " + carrier);



for (let n = max; n >= min; --n) {
	if (n % 2 == 0){
		console.log("knit - f" + n + " " + carrier);
	}
}




for (let r = 0; r < height; ++r) {

	//essentially, knit going in only one way on each bed, so they only meet on the edges
	if (r % 2 == 1) {
		for (let n = max; n >= min; --n) {
			if (n % 2 == 0){
				console.log("knit - f" + n + " " + carrier + "\n");
			}
		}
	} else {
		for (let n = min; n <= max; ++n) {
			if (n % 2 == 0){
				console.log("knit + b" + n + " " + carrier + "\n");
			}
		}
	}

	if (r % 4 == 3){
		//transfer needles to a new position on the front bed
		console.log("rack [f" + min + " f" + max + "] +");
		//transfer needles to a new position on the back bed
		console.log("rack [b" + min + " b" + max + "] +");
		min += 2;
		max += 2;
	} 
}



//simple function to move a range of needles in a direction by transfering them to the opposing bed
function rack(needles, bed, direction){
	let secondBed = bed === "f" ? "b" : "f";

	let code = "";

	if (bed === "f"){
		console.log("rack " + (direction === "+" ? "-1" : "1") + "\n");
	} else {
		console.log("rack " + (direction === "+" ? "1" : "-1") + "\n");
	}

	for (var n = 0; n < needles.length; n++){
		console.log("xfer " + bed + needles[n] + " "  + secondBed + (needles[n] + (direction == "+" ? 1 : -1)) + "\n");
	}

	if (bed === "f"){
		console.log("rack " + (direction === "+" ? "1" : "-1") + "\n");
	} else {
		console.log("rack " + (direction === "+" ? "-1" : "1") + "\n");
	}

	for (let n = 0; n < needles.length; n++){
		console.log("xfer "  + secondBed + (needles[n] + (direction == "+" ? 1 : -1)) + " " + bed + (needles[n] + (direction == "+" ? 2 : -2)) + "\n");
	}

	console.log("rack 0" + "\n");

	return code;
}


console.log("outhook " + carrier);
//console.log("outhook " + carrier2);

