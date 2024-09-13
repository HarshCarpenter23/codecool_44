const MedicineSupply = artifacts.require("MedicineSupply");

module.exports = async function(deployer) {
    await deployer.deploy(MedicineSupply);
    const instance = await MedicineSupply.deployed();
    console.log("Contract Address:", instance.address);
};
