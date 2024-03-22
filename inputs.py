from pydantic import BaseModel
from .setting import settings

# This file defines various input classes used for handling different actions in the system.
# Each class inherits from BaseModel (from pydantic) for easy validation and data handling.

class ClaimInput(BaseModel):
    """
    A class representing the input for creating a claim.

    Attributes:
        handle (str): The type of action, defaulted to "claim".
        prep_CID (str): The preparation CID associated with the claim.
        comp_CID (str): The computation CID associated with the claim.
        collateral (int): The collateral amount for the claim.
        computation_proof (str): The computation proof for the claim.
    """
    handle: str = "claim"
    prep_CID: str
    comp_CID: str
    collateral: int
    computation_proof: str


class WithdrawInput(BaseModel):
    """
    A class representing the input for withdrawing funds.

    Attributes:
        action (str): The type of action, defaulted to "withdraw".
        amount (int): The amount to withdraw.
    """
    action: str = "withdraw"
    amount: int


class FinalizeInput(BaseModel):
    """
    A class representing the input for finalizing a claim.

    Attributes:
        handle (str): The type of action, defaulted to "finalize".
        claimID (int): The ID of the claim to be finalized.
        prep_CID (str): The preparation CID of the claim.
    """
    handle: str = "finalize"
    claimID: int
    prep_CID: str


class ValidateInput(BaseModel):
    """
    A class representing the input for validating a claim.

    Attributes:
        handle (str): The type of action, defaulted to "validate".
        claimID (int): The ID of the claim to be validated.
        preprocessed_data (str): The preprocessed data associated with the claim.
        computation_proof (str): The computation proof for the claim.
    """
    handle: str = "validate"
    claimID: int
    preprocessed_data: str
    computation_proof: str


class DisputeInput(BaseModel):
    """
    A class representing the input for disputing a claim.

    Attributes:
        handle (str): The type of action, defaulted to "dispute".
        claimID (int): The ID of the claim to be disputed.
        staking_amount (int): The staking amount for disputing, defaulted to the VALIDATOR_STAKING setting.
        prep_CID (str): The preparation CID of the claim.
    """
    handle: str = "dispute"
    claimID: int
    staking_amount: int = settings.VALIDATOR_STAKING
    prep_CID: str
