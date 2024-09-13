// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract MedicineSupply {
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

    event ShipmentCreated(bytes32 qrCodeHash, string destination, string aadhaar);
    event OTPSet(bytes32 qrCodeHash);
    event ShipmentDelivered(bytes32 qrCodeHash, bool isDelivered, bool aadhaarVerified, bool otpVerified);

    function createShipment(string memory _qrCode, string memory _destination, string memory _aadhaar) public {
        bytes32 qrCodeHash = keccak256(abi.encodePacked(_qrCode));
        require(bytes(shipments[qrCodeHash].qrCode).length == 0, "Shipment already exists for this QR code");

        shipments[qrCodeHash] = Shipment({
            qrCode: _qrCode,
            destination: _destination,
            aadhaar: _aadhaar,
            otp: "",
            isDelivered: false,
            aadhaarVerified: false,
            otpVerified: false
        });

        emit ShipmentCreated(qrCodeHash, _destination, _aadhaar);
    }

    function verifyAadhaar(string memory _qrCode, string memory _enteredAadhaar) public {
        bytes32 qrCodeHash = keccak256(abi.encodePacked(_qrCode));
        require(bytes(shipments[qrCodeHash].qrCode).length > 0, "Shipment does not exist for this QR code");
        require(keccak256(abi.encodePacked(shipments[qrCodeHash].aadhaar)) == keccak256(abi.encodePacked(_enteredAadhaar)), "Aadhaar is incorrect");

        shipments[qrCodeHash].aadhaarVerified = true;
    }

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

    function getShipmentStatus(string memory _qrCode) public view returns (bool isDelivered, bool aadhaarVerified, bool otpVerified) {
        bytes32 qrCodeHash = keccak256(abi.encodePacked(_qrCode));
        require(bytes(shipments[qrCodeHash].qrCode).length > 0, "Shipment does not exist for this QR code");

        Shipment memory shipment = shipments[qrCodeHash];
        return (shipment.isDelivered, shipment.aadhaarVerified, shipment.otpVerified);
    }
}