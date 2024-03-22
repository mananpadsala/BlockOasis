import logging
from helpers.utils import to_jsonhex
from cartesi import Rollup, RollupData

from model.bank_db import bank_db
from model.user_db import users_db
from model.claims_db import claims_db
from helpers.setting import settings
from helpers.inputs import ClaimInput

# Configure logging for the module
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_claim(json_router):
    """
    Registers the claim generation route and its handler in the provided JSON router.

    Args:
        json_router: The router object that manages JSON route handling.
    """

    def validate_collateral(collateral: int):
        """
        Validates whether the provided collateral is correct.

        Args:
            collateral (int): The amount of collateral to be validated.

        Returns:
            (bool, str): Tuple of validation status and message.
        """
        if collateral is None or collateral != settings.COLLATERAL_AMOUNT:
            message = f"Collateral amount should be equal {settings.COLLATERAL_AMOUNT}"
            return False, message
        return True, ""

    def check_existing_claim(prep_CID: str):
        """
        Checks if a claim with the given preparation CID already exists.

        Args:
            prep_CID (str): The preparation CID to check for existing claims.

        Returns:
            (bool, str): Tuple of check status and message.
        """
        if claims_db.get_claim_by_prep_CID(prep_CID):
            return False, "Claim already exists"
        return True, ""

    def check_and_lock_funds(user_wallet_address: str):
        """
        Checks if the user has enough funds and locks the required collateral amount.

        Args:
            user_wallet_address (str): The wallet address of the user.

        Returns:
            (bool, str): Tuple of fund check status and message.
        """
        if bank_db.balance(user_wallet_address) < settings.COLLATERAL_AMOUNT:
            message = f"Insufficient funds for collateral in user's wallet. Current Balance: {bank_db.balance(user_wallet_address)}"
            return False, message

        try:
            bank_db.transfer(
                user_wallet_address,
                settings.LOCKED_ASSET_ADDRESS,
                settings.COLLATERAL_AMOUNT,
            )
            return True, ""
        except Exception as e:
            return False, f"Failed to lock collateral: {e}"

    def create_and_register_claim(
        prep_CID: str,
        user_address: str,
        timestamp: str,
        comp_proof: str,
        comp_CID: str,
        value: int,
    ):
        """
        Creates a new claim and registers it in the claims database.

        Args:
            prep_CID (str): Preparation CID of the claim.
            user_address (str): User's wallet address.
            timestamp (str): Timestamp of the claim.
            comp_proof (str): Computation proof of the claim.
            comp_CID (str): Computation CID of the claim.
            value (int): Collateral value of the claim.

        Returns:
            (int, Claim): Tuple of the new claim ID and the claim object.
        """
        new_claim_id = claims_db.get_next_claim_id()
        new_claim = claims_db.create_claim(
            prep_CID=prep_CID,
            user_address=user_address,
            timestamp_of_claim=timestamp,
            comp_proof=comp_proof,
            comp_CID=comp_CID,
            value=value,
        )
        return new_claim_id, new_claim

    def update_user_open_claims(user_wallet_address: str, new_claim_id: int):
        """
        Updates the user's open claims in the database.

        Args:
            user_wallet_address (str): The wallet address of the user.
            new_claim_id (int): The ID of the newly created claim.
        """
        user = users_db.get_user(user_wallet_address)
        if user:
            user.open_claims[str(new_claim_id)] = None
            users_db.update_user(user_wallet_address, open_claims=user.open_claims)

    @json_router.advance({"handle": "claim"})
    def handle_claim(rollup: Rollup, data: RollupData):
        """
        Handles the claim generation based on the provided Rollup data.
        This function processes the claim generation, updating databases, and handling collateral.

        Args:
            rollup (Rollup): The Rollup object managing blockchain state.
            data (RollupData): The data associated with the rollup event.

        Returns:
            bool: True if the claim is successfully generated, False otherwise.
        """
        LOGGER.info(f"Handling Claim: {data}")
        payload = ClaimInput.model_validate(data.json_payload())        

        # 1. Validate Collateral
        valid, message = validate_collateral(payload.collateral)
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
            return False
        LOGGER.info("✅ Collateral Validated")

        # 2. Check Existing Claim
        valid, message = check_existing_claim(payload.prep_CID)
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
            return False
        LOGGER.info("✅ Checked Existing Claims")

        # 3. Check and Lock Funds
        valid, message = check_and_lock_funds(data.metadata.msg_sender)
        if not valid:
            rollup.report(to_jsonhex({"error": message}))
            return False
        LOGGER.info("Funds locked")

        # 4. Create and Register Claim
        new_claim_id, new_claim = create_and_register_claim(
            payload.prep_CID,
            data.metadata.msg_sender,
            data.metadata.timestamp,
            payload.comp_proof,
            payload.comp_CID,
            int(payload.collateral),
        )
        LOGGER.info("✅ Claim created")

        # 5. Update User Open Claims
        update_user_open_claims(data.metadata.msg_sender, new_claim_id)
        LOGGER.info("Updated user database with open claim")

        # Generate a notice of claim generation
        rollup.notice(to_jsonhex({"key": new_claim_id, "claim": new_claim.dict()}))
        return True
