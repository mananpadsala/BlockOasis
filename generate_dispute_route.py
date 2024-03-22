import logging
from helpers.utils import to_jsonhex
from cartesi import Rollup, RollupData

from model.bank_db import bank_db
from model.claims_db import claims_db, Status
from helpers.setting import settings
from helpers.inputs import DisputeInput
from model.user_db import users_db

# Configure logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def generate_dispute(json_router):
    """
    Registers the dispute generation route and its handler in the provided JSON router.

    Args:
        json_router: The router object that manages JSON route handling.
    """
    
    def check_validator_stake(address: str, staking_amount: int):
        """
        Verifies if the disputing validator has enough funds to cover the staking amount.
        
        Args:
            address (str): The wallet address of the validator.
            staking_amount (int): The staking amount for the dispute.

        Returns:
            (bool, str): A tuple with a boolean status and message.
        """
        
        try:
            current_balance = bank_db.balance(address)
            if current_balance < settings.VALIDATOR_STAKING:
                msg = "Insufficient funds for staking"
                LOGGER.error(
                    f"{msg}. Required: {settings.VALIDATOR_STAKING}, Available: {current_balance}"
                )
                return False, msg
            elif staking_amount != settings.VALIDATOR_STAKING:
                msg = "Staking Amount is not equal to the required Validator Staking Amount."
                LOGGER.error(
                    f"{msg} Required: {settings.VALIDATOR_STAKING}, Staking Amount: {staking_amount}"
                )
                return False, msg
            LOGGER.info(
                f"Sufficient funds for staking. Required: {settings.VALIDATOR_STAKING}, Available: {current_balance}"
            )
            return True, ""
        except Exception as e:
            LOGGER.error(f"Error checking validator stake: {e}")
            raise

    def check_claim_exists_and_verify_CID(claim_id: str, expected_prep_CID: str):
        """
        Verifies the existence of the claim and matches its prep_CID.

        Args:
            claim_id (str): The ID of the claim.
            expected_prep_CID (str): The expected preparation CID for the claim.

        Returns:
            (bool, str): A tuple with a boolean status and message.
        """
        
        try:
            claim = claims_db.get_claim(claim_id)
            if claim is None:
                msg = f"No claim found with ID: {claim_id}"
                LOGGER.info(msg)
                return False, msg
            if claim.prep_CID != expected_prep_CID:
                msg = f"Claim with ID: {claim_id} found, but prep_CID does not match. Expected: {expected_prep_CID}, Found: {claim.prep_CID}"
                LOGGER.info(msg)
                return False, msg
            LOGGER.info(
                f"Claim found with ID: {claim_id} and matching prep_CID: {expected_prep_CID}"
            )
            return True, ""
        except Exception as e:
            LOGGER.error(f"Error checking if claim exists and verifying prep_CID: {e}")
            # Depending on your error handling strategy, you might raise the exception or return False
            raise

    def check_claim_eligible_for_dispute(claim_id: str, disputing_party_address: str):
        """
        Checks if the claim is eligible for dispute based on its status and the disputing party.

        Args:
            claim_id (str): The ID of the claim.
            disputing_party_address (str): The wallet address of the disputing party.

        Returns:
            (bool, str): A tuple with a boolean status and message.
        """
        
        try:
            claim = claims_db.get_claim(claim_id)
            # Check if Status is Open
            if claim.status != Status.OPEN:
                msg = f"Claim with ID: {claim_id} found, but status '{claim.status}' is not eligible for dispute."
                LOGGER.info(msg)
                return False, msg
            # Verify not a self dispute
            if claim.user_address == disputing_party_address:
                msg = "Cannot dispute own claim"
                LOGGER.info(msg)
                return False, msg
            LOGGER.info(
                f"Claim with ID: {claim_id} is in an eligible status ('OPEN') for dispute."
            )
            return True
        except Exception as e:
            LOGGER.error(f"Error checking claim status: {e}")
            raise

    def transfer_stake_to_locked_account(user_wallet_address: str, stake_amount: int):
        """
        Transfers the staking amount from the user's wallet to a locked account.

        Args:
            user_wallet_address (str): The wallet address of the user.
            stake_amount (int): The staking amount to be transferred.

        Returns:
            (bool, str): A tuple with a boolean status and message.
        """
        
        try:
            if bank_db.balance(user_wallet_address) < stake_amount:
                msg = f"Insufficient funds for staking in user's wallet. Required: {stake_amount}, Available: {bank_db.balance(user_wallet_address)}"
                LOGGER.error(msg)
                return False, msg

            bank_db.transfer(
                user_wallet_address, settings.LOCKED_ASSET_ADDRESS, stake_amount
            )
            LOGGER.info(
                f"Transferred {stake_amount} from {user_wallet_address} to locked account {settings.LOCKED_ASSET_ADDRESS}"
            )
            return True, ""
        except Exception as e:
            LOGGER.error(f"Failed to transfer stake to locked account: {e}")
            return False

    @json_router.advance({"handle": "dispute"})
    def handle_dispute(rollup: Rollup, data: RollupData):
        """
        Handles a dispute request based on the Rollup data.

        Args:
            rollup (Rollup): The Rollup context.
            data (RollupData): Data related to the dispute request.

        Returns:
            bool: True if the dispute handling is successful, False otherwise.
        """

        LOGGER.debug(f"Handling Dispute: {data}")

        # Extract and validate dispute input
        payload = DisputeInput.model_validate(data.json_payload())

        # 1. Check Validator Stake
        disputing_party_address = data.metadata.msg_sender
        valid, message = check_validator_stake(disputing_party_address, payload.staking_amount)
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
            return False
        LOGGER.info("✅ Staking Amount Check")

        # 2. Check Claim Exists and Verify CID
        valid, message = check_claim_exists_and_verify_CID(payload.claimID, payload.prep_CID)
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
            return False
        LOGGER.info("✅ Claim and Preprocced CID Check")

        # 3. Check Claim Eligibility for Dispute
        valid, message = check_claim_eligible_for_dispute(
            payload.claimID, disputing_party_address
        )
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
        LOGGER.info("✅ Claim Status Check")

        # 4. Transfer Stake to Locked Account
        valid, message = transfer_stake_to_locked_account(
            disputing_party_address, payload.staking_amount
        )
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
        LOGGER.info("✅ Amount Stake Check")

        # 5. Initiate Dispute on Claim
        updated_claim = claims_db.initiate_dispute(payload.claimID, disputing_party_address)
        if updated_claim is None:
            rollup.report(to_jsonhex({"error": "Failed to initiate dispute on claim"}))
            return False
        LOGGER.info("✅ Update Claim Check")
        
        # 6. Update user db
        update_user = users_db.get_user(claims_db.get_claim(payload.claimID).user_address)
        update_user.open_disputes[payload.claimID] = None
        del update_user.open_claims[payload.claimID]
        LOGGER.info("✅ Update User DB Check")

        rollup.report(
            f"Dispute initiated on claim ID {payload.claimID} by user {disputing_party_address}\nTime Left to resolve dispute: {settings.DISPUTE_EPOCH}"
        )

        return True
