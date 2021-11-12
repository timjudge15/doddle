const Venus = require('@swipewallet/venus-js'); // in Node.js
const vBusdAddress = Venus.util.getAddress(Venus.vBUSD);

(async function() {

  let supplyRatePerBlock = await Venus.eth.read(
    vBusdAddress,
    'function supplyRatePerBlock() returns (uint)',
    [], // [optional] parameters
    {}  // [optional] call options, provider, network, ethers.js "overrides"
  );

  console.log('USDT supplyRatePerBlock:', supplyRatePerBlock.toString());

})().catch(console.error);
console.log('hello')