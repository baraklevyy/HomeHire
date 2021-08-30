pragma solidity ^0.6.0;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v3.0.0/contracts/math/SafeMath.sol";



/*
HomeHire smart-contract	
*/
contract HomeHire {

	//safe-math package usage
    using SafeMath for uint256;

	//Contract deployer address
	address public deployer;

	//Property data-structure
    struct Home {
        address renter;
        address owner;
        uint256 homeRent;
        uint256 roomNum;
        uint256 monthsToPay;
        string dateOfStart;
        string dateOfEnd;
        string garage;
        string elevator;
        
    }

	// Mapping used to track relationship between users and approved Landlords.
	mapping (address => bool) public Landlords;

	// Mapping used to track relationship between tenant to the exclussive property he rents. 
	mapping (address => Home) public Homes;

	//Only the deployer of the contract can add approved Landlords.
	constructor() public {
        deployer = msg.sender;
    }

	//Function used to add Landlord - Only the contract deployer can perfrom this action.
	function addLandlord(address _landlord) public {
	    require(msg.sender == deployer, "Only admin can call this function.");
	    Landlords[_landlord] = true;
	}

	//Function used to add home for rental. Each property is tenant-exclussive and only approved landlord can add home.
	function addHome(uint256 _homeRent, uint256 _monthsToPay, address _renter, string memory _dateOfStart, string memory _dateOfEnd, string memory _elevator, string memory _garage, uint256 _roomNum) public {
	    require(Landlords[msg.sender] == true, "Only approved landlords can list homes.");
	    require(Homes[_renter].renter != _renter, "Renter can hire only one property.");
	    Homes[_renter] = Home({
	        renter: _renter,
	        owner: msg.sender,
	        dateOfStart: _dateOfStart,
	        dateOfEnd: _dateOfEnd,
	        homeRent: _homeRent,
	        monthsToPay: _monthsToPay,
	        roomNum: _roomNum,
	        garage: _garage,
	        elevator: _elevator
	    });
	}

	//Function used to update the property tenant. Each property is tenant-exclussive and only approved landlord can update home.
	function changeRenter(address _oldRenter, address _newRenter, string memory _dateOfStart, string memory _dateOfEnd, uint256 _monthsToPay) public {
	    require(Homes[_oldRenter].renter == _oldRenter, "Renter not have a home.");
	    require(Homes[_oldRenter].owner == msg.sender, "Only the owner of this property can change the renter.");
	    Homes[_oldRenter].monthsToPay = _monthsToPay;
	    Homes[_oldRenter].dateOfStart = _dateOfStart;
	    Homes[_oldRenter].dateOfEnd = _dateOfEnd;
	    Homes[_oldRenter].renter = _newRenter;
	    Homes[_newRenter] = Homes[_oldRenter];
	    delete Homes[_oldRenter];
	}

	//Function used to update the property rent-price. Each property is tenant-exclussive and only approved landlord can update rent-price.
	function changeHomeRent(address _renter, uint256 _newHomeRent) public {
	    require(Homes[_renter].renter == _renter, "Renter not have a home.");
	    require(Homes[_renter].owner == msg.sender, "Only the owner of this property can update the home rent.");
	    Homes[_renter].homeRent = _newHomeRent;
	}
	
	//Function used to delete property. Only the contract deployer can delete a property. Used to enforce unprotected tenancy.
	function deleteHome(address _renter) public {
	    require(Homes[_renter].renter == _renter, "Renter not have a home.");
	    require(msg.sender == deployer, "Only admin can call this function.");
	    delete Homes[_renter];

	}

	//Function used to pay a rent by the tenent to the appropriate landlord.
    function payRent(address payable _to) public payable {
        require(Landlords[_to] == true, "Rent must be sent to an approved landlord.");
        require(Homes[msg.sender].owner == _to, "Rent must be paid to the owner of the home.");
        require(Homes[msg.sender].homeRent == msg.value, "Rent must be equal to the home rent.");
        require(Homes[msg.sender].monthsToPay > 0, "Months to pay need to be more then 0");

        _to.transfer(msg.value);
        Homes[msg.sender].monthsToPay = Homes[msg.sender].monthsToPay.sub(1);

    }

    //Getter function used to retrieve a property given tenant address(one-to-one relation)
    function getHome(address _renter) public view returns(address, address, uint256, uint256, uint256, string memory, string memory, string memory, string memory) {
        Home storage home = Homes[_renter];
        return (home.renter, home.owner, home.homeRent, home.roomNum, home.monthsToPay, home.dateOfStart, home.dateOfEnd, home.garage, home.elevator);
    }
}
