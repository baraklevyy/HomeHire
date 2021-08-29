pragma solidity ^0.6.0;


contract HomeHire {

	address public deployer;

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

	mapping (address => bool) public Landlords;
	mapping (address => Home) public Homes;

	event HomeRentChanged(
	    address renter,
	    uint256 newHomeRent
	    );

	event RenterChanged(
	    address oldRenter,
	    address newRenter
	    );

	constructor() public {
        deployer = msg.sender;
    }

	function addLandlord(address _landlord) public {
	    require(msg.sender == deployer, "Only admin can call this function.");
	    Landlords[_landlord] = true;
	}

	function addHome(uint256 _homeRent, uint256 _monthsToPay, address _renter, string memory _dateOfStart, string memory _dateOfEnd, string _elevator, string _garage, uint256 _roomNum) public {
	    require(Landlords[msg.sender] == true, "Only approved landlords can list homes.");
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

	function changeRenter(address _oldRenter, address _newRenter, string memory _dateOfStart, string memory _dateOfEnd, uint256 _monthsToPay) public {
	    require(Homes[_oldRenter].owner == msg.sender, "Only the owner of this property can change the renter.");
	    Homes[_oldRenter].monthsToPay = _monthsToPay;
	    Homes[_oldRenter].dateOfStart = _dateOfStart;
	    Homes[_oldRenter].dateOfEnd = _dateOfEnd;
	    Homes[_oldRenter].renter = _newRenter;
	    Homes[_newRenter] = Homes[_oldRenter];
	    delete Homes[_oldRenter];

	    emit RenterChanged(_oldRenter, _newRenter);
	}

	function changeHomeRent(address _renter, uint256 _newHomeRent) public {
	    require(Homes[_renter].owner == msg.sender, "Only the owner of this property can update the home rent.");
	    Homes[_renter].homeRent = _newHomeRent;

	    emit HomeRentChanged(_renter, _newHomeRent);
	}


    function payRent(address payable _to) public payable {
        require(Landlords[_to] == true, "Rent must be sent to an approved landlord.");
        require(Homes[msg.sender].owner == _to, "Rent must be paid to the owner of the home.");
        require(Homes[msg.sender].homeRent == msg.value, "Rent must be equal to the home rent.");
        require(Homes[msg.sender].monthsToPay > 0, "Months to pay need to be more then 0");

        _to.transfer(msg.value);
        Homes[msg.sender].monthsToPay -= 1;

    }

    
    function getHome(address _renter) public view returns(address, address, uint256, uint256, uint256, string memory, string memory, string memory, string memory) {
        Home storage home = Homes[_renter];
        return (home.renter, home.owner, home.homeRent, home.roomNum, home.monthsToPay, home.dateOfStart, home.dateOfEnd, home.garage, home.elevator);
    }
}