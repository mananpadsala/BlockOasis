from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    A class for configuring and storing application settings using Pydantic BaseSettings.

    Attributes:
        PORTAL_ERC20_ADDRESS (str): ERC20 address for the portal, a predefined address.
        TOKEN_ERC20_ADDRESS (str): ERC20 token address used in the application. 
            It can be updated as per requirement.
        ERC20_TRANSFER_FUNCTION_SELECTOR (bytes): A byte sequence representing the 
            ERC20 transfer function selector.
        LOCKED_ASSET_ADDRESS (str): Address used to represent locked assets in the system.
        COLLATERAL_AMOUNT (int): The amount set as collateral for certain operations, 
            such as claims.
        CLAIM_EPOCH (int): The epoch duration for claims, in seconds.
        DISPUTE_EPOCH (int): The epoch duration for disputes, in seconds.
        VALIDATOR_STAKING (int): The amount of staking required for a validator, 
            represented in smallest units.
        CLAIM_INCENTIVE (int): The incentive amount for making a claim, calculated as 
            a fraction of a unit.
    """
    # ERC20 addresses and related settings
    PORTAL_ERC20_ADDRESS: str = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB"
    TOKEN_ERC20_ADDRESS: str = "0xc6e7DF5E7b4f2A278906862b61205850344D4e7d"  # "0x4A679253410272dd5232B3Ff7cF5dbB88f295319"
    ERC20_TRANSFER_FUNCTION_SELECTOR = b'\xa9\x05\x9c\xbb'

    # Addresses for locked assets and collateral requirements
    LOCKED_ASSET_ADDRESS: str = "0x0000000000000000000000000000000000000001"
    COLLATERAL_AMOUNT: int = 1000000000000000000

    # Time-related settings for claims and disputes
    CLAIM_EPOCH: int = 30
    DISPUTE_EPOCH: int = 60

    # Validator staking and incentives
    VALIDATOR_STAKING: int = 4 * 1000000000000000000
    CLAIM_INCENTIVE: int = int(0.0005 * 1000000000000000000)


# Instantiating the Settings object for application-wide use.
settings = Settings()
