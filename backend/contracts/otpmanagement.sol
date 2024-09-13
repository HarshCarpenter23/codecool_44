// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract otpmanagement {
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

    event OTPSet(bytes32 qrCodeHash);
    event ShipmentDelivered(bytes32 qrCodeHash, bool isDelivered, bool aadhaarVerified, bool otpVerified);

    function setOTP(string memory _qrCode, string memory _otp) public {
        bytes32 qrCodeHash = keccak256(abi.encodePacked(_qrCode));
        require(bytes(shipments[qrCodeHash].qrCode).length > 0, "Shipment does not exist for this QR code");

        shipments[qrCodeHash].otp = _otp;
        emit OTPSet(qrCodeHash);
    }

    function verifyOTP(string memory _qrCode, string memory _enteredOtp) public {
        bytes32 qrCodeHash = keccak256(abi.encodePacked(_qrCode));
        require(bytes(shipments[qrCodeHash].qrCode).length > 0, "Shipment does not exist for this QR code");
        require(keccak256(abi.encodePacked(shipments[qrCodeHash].otp)) == keccak256(abi.encodePacked(_enteredOtp)), "OTP is incorrect");

        shipments[qrCodeHash].isDelivered = true;
        shipments[qrCodeHash].otpVerified = true;

        emit ShipmentDelivered(qrCodeHash, shipments[qrCodeHash].isDelivered, shipments[qrCodeHash].aadhaarVerified, shipments[qrCodeHash].otpVerified);
    }
}
