# Helpers Directory Documentation

This directory, `helpers`, contains essential utility modules that support the main functionality of our project. Each file serves a specific role in assisting with data handling, configuration settings, and utility functions.

## Files Overview

### 1. `inputs.py`
This module defines various input classes that are used for handling different types of data inputs across the system. These classes include:
- `ClaimInput`: For handling claim creation inputs.
- `WithdrawInput`: For managing withdrawal action inputs.
- `FinalizeInput`: For finalizing claim inputs.
- `ValidateInput`: For validation of claims.
- `DisputeInput`: For inputs related to disputing claims.
Each class inherits from Pydantic's `BaseModel`, ensuring efficient data validation and error handling.

### 2. `settings.py`
The `settings.py` file contains the `Settings` class, which uses Pydantic's `BaseSettings` for application configuration. This class defines various settings such as ERC20 addresses, collateral amounts, epochs for claims and disputes, and staking values. These settings are crucial for the application's interaction with blockchain technologies and financial calculations.

### 3. `utils.py`
This utility file provides a collection of functions essential for data conversion and encoding specific to blockchain transactions. Key functions include:
- Conversion between string and hex formats.
- Encoding and decoding of ERC20 deposit data.
- Creation of ERC20 transfer vouchers.
These utilities play a critical role in handling and processing blockchain-related data throughout the application.

## Development and Usage

### Importing Modules
- Import these utility modules into other parts of the application as needed.
- Utilize the classes and functions to handle data inputs, read settings, and perform utility operations.

### Customization
- You can customize `settings.py` as per your project's specific configuration needs.
- Extend `inputs.py` and `utils.py` to include additional functionalities required by your application.

## Contributing
Your contributions to enhance or extend the functionalities of these helper modules are welcome. Please follow the standard pull request process and ensure adherence to the project's coding standards.

## Support
For any queries or issues related to these modules, please open an issue in the project repository or contact the project maintainers.
