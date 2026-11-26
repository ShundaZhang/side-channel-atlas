'use strict';
const assert = require('node:assert/strict');
const {historyStates, HISTORY_SEQUENCE, rsbState, lookupState} = require('./training_models.js');
const states = historyStates(HISTORY_SEQUENCE);
assert.deepEqual(states.slice(0,9), [0,1,2,5,11,22,44,89,178]);
assert.equal(states[12], 47);
assert.throws(() => historyStates([2]));
assert.deepEqual(rsbState('normal', 2).rsb, ['R_main','R_f']);
assert.equal(rsbState('normal', 3).predicted, 'R_main');
for (let step = 0; step <= 6; step++) {
 const s=rsbState('underflow',step); assert.equal(s.stack.length,6-step); assert.equal(s.rsb.length, Math.max(0,4-step));
 assert.equal(s.shortage,step===4||step===5);
 if (step<4) assert.equal(s.predicted,s.actual);
}
assert.equal(rsbState('underflow',4).actual,'R2');
assert.equal(rsbState('underflow',4).predicted,'G');
assert.equal(rsbState('underflow',6).source,'none');
assert.throws(()=>rsbState('normal',5));
assert.equal(lookupState('bti','H_A',true,false).predicted,'NORMAL');
assert.equal(lookupState('bti','H_A',true,true).predicted,'G');
const a=lookupState('bhi','H_A',false,false), b=lookupState('bhi','H_G',false,false);
assert.deepEqual(a.targets,b.targets);assert.equal(a.predicted,'NORMAL');assert.equal(b.predicted,'G');assert.equal(b.actual,'NORMAL');
console.log('PASS: 8-bit history, extra-branch overwrite, RSB push/pop and underflow, BTI alias gate, BHI fixed-target selection');
