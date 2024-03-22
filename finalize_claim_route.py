import logging
from typing import Optional
from cartesi import Rollup, RollupData

from model.bank_db import bank_db
from model.claims_db import claims_db, Status, Claim
from model.user_db import users_db
from helpers.setting import settings
from helpers.inputs import FinalizeInput

# Configure logging for this module.
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def finalize_claim(json_router):
    """
    Registers the claim finalization route and its handler in the provided JSON router.

    Args:
        json_router: The router object that manages JSON route handling.
    """

    @json_router.advance({"handle": "finalize"})
    def handle_finalize(rollup: Rollup, data: RollupData) -> bool:
        """
        Handles the finalization of a claim based on the provided Rollup data.
        This function is responsible for processing the claim finalization, updating user and claim databases,
        and handling collateral transfers based on the claim's status.

        Args:
            rollup (Rollup): The Rollup object managing blockchain state.
            data (RollupData): The data associated with the rollup event.

        Returns:
            bool: True if the claim is successfully finalized, False otherwise.
        """
        LOGGER.info(f"Handling Finalize: {data}")

        # Extracting claim ID and prep_CID from the payload
        payload = FinalizeInput.model_validate(data.json_payload())

        # Validate necessary parameters
        if not (payload.claimID or payload.prep_CID):
            error_message = "❌ Not enough parameters, you must provide 'claimID' and 'prep_CID'"
            rollup.report(error_message)
            raise ValueError(error_message)

        # Check if claim exists
        claim: Optional[Claim] = claims_db.get_claim(payload.claimID)
        if not claim:
            msg = "❌ Claim doesn't exist"
            rollup.report(msg)
            raise ValueError(msg)

        # Processing based on claim status
        if claim.status == Status.OPEN:
            # Handle open claims
            # Check if enough time has passed since the claim was last edited
            if data.metadata.timestamp < claim.last_edited + settings.CLAIM_EPOCH:
                seconds_to_accept = claim.last_edited + settings.CLAIM_EPOCH - data.metadata.timestamp
                msg = f"❌ Claim can't be finalized yet, {seconds_to_accept} more seconds to go"
                rollup.report(msg)
                raise ValueError(msg)

            # Finalize claim
            claims_db.finalize_claim(payload.claimID, Status.FINALIZED)

            # Update user's claim statistics
            user = users_db.get_user(claim.user_address)
            user.total_claims += 1
            user.correct_claims += 1
            user.open_claims.pop(payload.claimID, None)
            msg = f"✅ Claimer DB updated: {user}"
            LOGGER.info(msg)

            # Transfer collateral and incentive to the claimer
            bank_db.transfer(settings.LOCKED_ASSET_ADDRESS, claim.user_address, settings.COLLATERAL_AMOUNT + settings.CLAIM_INCENTIVE)
            msg = "✅ Collateral transferred to the claimer"
            LOGGER.info(msg)

        elif claim.status == Status.DISPUTING:
            # Handle disputing claims
            # Check if enough time has passed since the claim was last edited
            if data.metadata.timestamp < claim.last_edited + settings.DISPUTE_EPOCH:
                seconds_to_accept = claim.last_edited + settings.DISPUTE_EPOCH - data.metadata.timestamp
                msg = f"❌ Claim can't be finalized yet, {seconds_to_accept} more seconds to go"
                rollup.report(msg)
                raise ValueError(msg)

            # Finalize claim as disputed
            claims_db.finalize_claim(payload.claimID, Status.DISPUTED)

            # Update claimant and disputer's statistics
            claimant = users_db.get_user(claim.user_address)
            claimant.total_claims += 1
            claimant.total_disputes += 1
            claimant.open_disputes.pop(payload.claimID, None)

            disputer = users_db.get_user(claim.disputing_user_address)
            disputer.total_disputes += 1
            disputer.won_disputes += 1

            # Transfer collateral to the disputer
            bank_db.transfer(settings.LOCKED_ASSET_ADDRESS, claim.disputing_user_address, settings.COLLATERAL_AMOUNT)
            msg = "✅ Collateral transferred to the disputer"
            LOGGER.info(msg)

        else:
            # Handle invalid claim status
            msg = "❌ Can only finalize Open or Disputing claims"
            rollup.report(msg)
            raise ValueError(msg)

        # Generate a notice of finalization
        rollup.notice(f"Claim finalized! Claim ID: {payload.claimID}, Claim: {claims_db.get_claim(payload.claimID)}")
        return True
