# from pydantic import BaseModel, Field
from typing import Dict, List, Optional

import time

from .model import Claim, Status


class ClaimsDatabase:
    """
    A database class to manage and store insurance claims.

    Attributes:
        claims (Dict[int, Claim]): A dictionary mapping claim IDs to Claim objects.
        next_claim_id (int): An integer to keep track of the next claim ID.
    """

    def __init__(self):
        # Initializes an empty dictionary for storing claims and sets the initial claim ID.
        self.claims: Dict[int, Claim] = {}
        self.next_claim_id: int = 1  # Start with 1, increment for each new claim

    def create_claim(
        self,
        prep_CID: str,
        user_address: str,
        timestamp_of_claim: str,
        comp_proof: str,
        comp_CID: str,
        value: int,
    ) -> Claim:
        """
        Creates a new claim with the provided details and adds it to the claims dictionary.

        Parameters:
            prep_CID (str): The preparation CID of the claim.
            user_address (str): The address of the user filing the claim.
            timestamp_of_claim (str): The timestamp when the claim was made.
            comp_proof (str): The computation proof of the claim.
            comp_CID (str): The computation CID associated with the claim.
            value (int): The value or amount of the claim.

        Returns:
            Claim: The newly created claim object.
        """
        claim_id = self.next_claim_id
        self.next_claim_id += 1

        new_claim = Claim(
            user_address=user_address,
            disputing_user_address=None,
            timestamp_of_claim=timestamp_of_claim,
            status=Status.OPEN,
            collateral=value,
            compProof=comp_proof,
            compCID=comp_CID,
            prepCID=prep_CID,
            lastUpdated=int(time.time()),
        )
        self.claims[claim_id] = new_claim  # Using numerical ID
        return new_claim

    def get_next_claim_id(self) -> int:
        """
        Gets the next available claim ID.

        Returns:
            int: The next claim ID.
        """
        return self.next_claim_id

    def initiate_dispute(
        self, claim_id: int, disputing_user_address: str
    ) -> Optional[Claim]:
        """
        Initiates a dispute on the claim with the given ID.

        Parameters:
            claim_id (int): The ID of the claim to dispute.
            disputing_user_address (str): The address of the user disputing the claim.

        Returns:
            Optional[Claim]: The updated claim object if found, else None.
        """
        claim = self.claims.get(claim_id)
        if claim:
            claim.disputing_user_address = disputing_user_address
            claim.status = Status.DISPUTING
            claim.lastUpdated = int(time.time())
            return claim
        return None

    def finalize_claim(self, claim_id: int, final_status: Status) -> Optional[Claim]:
        """
        Finalizes a claim with the given status.

        Parameters:
            claim_id (int): The ID of the claim to finalize.
            final_status (Status): The final status to set for the claim.

        Returns:
            Optional[Claim]: The updated claim object if found, else None.
        """
        claim = self.claims.get(claim_id)
        if claim:
            claim.status = final_status
            claim.lastUpdated = int(time.time())
            return claim
        return None

    def validate_or_contradict_claim(
        self, claim_id: int, claim_status: Status
    ) -> Optional[Claim]:
        """
        Validates or contradicts a claim based on the given status.

        Parameters:
            claim_id (int): The ID of the claim to validate or contradict.
            claim_status (Status): The status to update the claim with.

        Returns:
            Optional[Claim]: The updated claim object if found, else None.
        """
        claim = self.claims.get(claim_id)
        if claim:
            claim.status = claim_status
            claim.lastUpdated = int(time.time())
            return claim
        return None

    def get_claim(self, claim_id: int) -> Optional[Claim]:
        """
        Retrieves a claim by its ID.

        Parameters:
            claim_id (int): The ID of the claim to retrieve.

        Returns:
            Optional[Claim]: The claim object if found, else None.
        """
        return self.claims.get(claim_id)

    def get_claim_by_prep_CID(self, prep_CID: str) -> Optional[Claim]:
        """
        Retrieves a claim by its preparation CID.

        Parameters:
            prep_CID (str): The preparation CID of the claim to retrieve.

        Returns:
            Optional[Claim]: The claim object if found, else None.
        """
        for claim in self.claims.values():
            if claim.prepCID == prep_CID:
                return claim
        return None

    def get_all_claims(self) -> List[Claim]:
        """
        Retrieves all claims in the database.

        Returns:
            List[Claim]: A list of all claim objects.
        """
        return list(self.claims.values())

    # Additional methods can be added as needed for your application


# Instantiate a ClaimsDatabase object for use.
claims_db = ClaimsDatabase()
