# BlockOasisDappBackend Documentation

BlockOasisDappBackend is a decentralized application (DApp) backend, designed to manage blockchain-based operations like handling claims, disputes, deposits, and withdrawals.

## Overview

The backend is centered around a DApp controller which integrates various routing functionalities for different aspects of user interaction and data processing. These functionalities are defined in separate scripts within the `routes` directory.

## Main Components

### 1. `DApp Controller`
The central controller script initializes the DApp and sets up routers (JSONRouter and URLRouter). It integrates route handlers for various operations and serves as the entry point for the application.

### 2. `Routes Directory`
This directory contains scripts for handling different routes:
- `hello_route.py`: Manages basic greeting routes.
- `register_deposit_route.py`: Handles ERC20 token deposit processes.
- `generate_claim_route.py`: Responsible for creating new claims.
- `withdraw_route.py`: Processes user withdrawal requests.
- `finalize_claim_route.py`: Manages finalization of claims.
- `generate_dispute_route.py`: Handles the creation and processing of disputes.
- `validate_claim_route.py`: Validates and finalizes claims.

### 3. `Helpers Directory`
Contains essential utility modules that support the main functionality of the project:
- `inputs.py`: Defines various input classes for handling different types of data inputs.
- `settings.py`: Contains the `Settings` class for application configuration.
- `utils.py`: Provides functions essential for data conversion and encoding specific to blockchain transactions.

### 4. `Model Directory`
Includes core modules of the financial and claims management system:
- `bank_db.py`: Manages all banking-related operations.
- `claims_db.py`: Handles the storage, creation, and management of claims.
- `model.py`: Central to the system, defining the data models used across the application.
- `user_db.py`: Focuses on user management.

## Running the DApp with Sunodo

### Prerequisites
Ensure that Sunodo is installed on your system. Follow the installation guide here: [Installing Sunodo](https://docs.sunodo.io/guide/introduction/installing)

### Project Setup
Ensure your project structure and configuration files are set up as per Sunodo's requirements.

### Configuration
Create a `.sunodo.env` configuration file in the project's root directory. Define your application's build and run commands here.

Example `.sunodo.env`:
```makefile
SM_DEADLINE_ADVANCE_STATE=360000
SM_DEADLINE_MACHINE=300000
S6_CMD_WAIT_FOR_SERVICES_MAXTIME=60000
S6_CMD_WAIT_FOR_SERVICES=60
```

### Build and Run Commands
- To build your project:
  ```bash
  sunodo build
  ```

- To run your project:
  ```bash
  sunodo run
  ```

These commands will execute the build and start scripts defined in your configuration file.

## Contributing

Contributions to enhance or extend the functionalities are welcome. Follow the standard pull request process and adhere to the project's coding standards.

## Support

For queries or issues related to the DApp backend, open an issue in the project repository or contact the project maintainers.

---
