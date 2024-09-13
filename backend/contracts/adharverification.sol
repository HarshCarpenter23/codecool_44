// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract adharverification {
    struct Shipment {
        string qrCode;
        string destination;
        string aadhaar;
        string otp;
        bool isDelivered;
        bool aadhaarVerified;
        bool otpVerified;
    }

    mapping(bytes32 => Shipment) public shipments;

    event AadhaarVerified(bytes32 qrCodeHash);

    function verifyAadhaar(string memory _qrCode, string memory _enteredAadhaar) public {
        bytes32 qrCodeHash = keccak256(abi.encodePacked(_qrCode));
        require(bytes(shipments[qrCodeHash].qrCode).length > 0, "Shipment does not exist for this QR code");
        require(keccak256(abi.encodePacked(shipments[qrCodeHash].aadhaar)) == keccak256(abi.encodePacked(_enteredAadhaar)), "Aadhaar is incorrect");

        shipments[qrCodeHash].aadhaarVerified = true;

        emit AadhaarVerified(qrCodeHash);
    }
}
