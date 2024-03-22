import logging
from cartesi import Rollup, RollupData
import pandas as pd
import hashlib
from io import StringIO

from model.bank_db import bank_db
from model.claims_db import claims_db, Status
from model.user_db import users_db
from helpers.setting import settings
from helpers.inputs import ValidateInput

# Configure logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def validate_and_finalize(json_router):
    def calculate_endpoint_usage(csv_data):
        """
        Calculates water usage at endpoints within the entire dataset and returns the SHA-256 hash of the calculated data.

        Parameters:
        - csv_data (str): String containing CSV formatted data.
        """
        
        # Read the dataset from the CSV string
        data = pd.read_csv(StringIO(csv_data))

        # Filter data to include only 'Endpoint' type
        filtered_data = data[data["type"] == "Endpoint"]

        # Grouping the data by sensor ID and calculating total water usage for each endpoint
        grouped_data = (
            filtered_data.groupby("sensor_id")["water_usage"].sum().reset_index()
        )

        # Convert the grouped data to a CSV string and calculate its hash (without index and header)
        grouped_data_csv = grouped_data.to_csv(index=False, header=False)
        hash_result = hashlib.sha256(grouped_data_csv.encode()).hexdigest()

        return hash_result

    @json_router.advance({"handle": "validate"})
    def handle_validate(rollup: Rollup, data: RollupData):
        LOGGER.info(f"Validating finalize: {data}")

        # claim_id, claim_data = decode_validate_input(data)
        payload = ValidateInput.parse_obj(data.json_payload())

        # Parameters Check
        if not payload.claimID or not payload.preprocessed_data:
            msg = "❌ Not enough parameters, you must provide 'claimId' and 'Preprocessed data'"
            rollup.report(msg)
            raise ValueError(msg)

        # Claim existance Check
        claim = claims_db.get_claim(payload.claimID)
        if not claim:
            msg = "❌ Claim doesn't exist"
            rollup.report(msg)
            raise ValueError(msg)

        # Claim Status Check
        if claim.status not in [Status.OPEN, Status.DISPUTING]:
            msg = "❌ Can only validate Open and Disputing claims"
            rollup.report(msg)
            raise ValueError(msg)

        # Claim ownership Check
        if claim.user_address != data.metadata.sender:
            msg = "❌ Can only validate own claims"
            rollup.report(msg)
            raise ValueError(msg)

        valid, msg = validate_and_finalize_claim(
            payload.claimID,
            payload.preprocessed_data,
            data.metadata.timestamp,
            payload.computation_proof,
        )
        
        if valid:
            rollup.notice(msg)
            return True

    def validate_and_finalize_claim(claimID, preprocessed_data, timestamp, comp_proof):
        is_claim_valid = validate_claim(
            preprocessed_data, comp_proof
        )  # This needs implementation

        claim = claims_db.get_claim(claimID)

        if is_claim_valid: # Claimer won
            # Check if claim is disputing, if so, get disputing user addr and transfer fund and update user db
            if claim.status == Status.DISPUTING: # -> Disputing user lost
                users_db.lost_claim(
                    user_id=claim.disputing_user_address, claimID=claimID
                )

            # Update claim_db
            claims_db.validate_or_contradict_claim(
                claim_id=claimID, claim_status=Status.VALIDATED
            )

            # Update user_db
            users_db.won_claim(claim.user_address, claimID)
            
            # Amount Transfered to claimer
            bank_db.transfer(settings.LOCKED_ASSET_ADDRESS, claim.user_address, settings.COLLATERAL_AMOUNT+settings.VALIDATOR_STAKING+settings.CLAIM_INCENTIVE)
        

        else: # Disputer Won
            if claim.status == Status.DISPUTING:
                users_db.won_claim(
                    user_id=claim.disputing_user_address, claimID=claimID
                )

            # Updating the claim
            claims_db.validate_or_contradict_claim(
                claim_id=claimID, claim_status=Status.CONTRADICTED
            )
            
            # Updating the user
            users_db.lost_claim(user_id=claim.user_address, claimID=claimID)
            
            # Updating the Bank
            bank_db.transfer(settings.LOCKED_ASSET_ADDRESS, claim.disputing_user_address, settings.COLLATERAL_AMOUNT+settings.VALIDATOR_STAKING+settings.CLAIM_INCENTIVE)
        
        msg = f"Claim {claimID} {'validated' if is_claim_valid else 'contradicted'}: {claim}"
        # rollup.report(msg)
        LOGGER.info(msg)

        return True, msg

    def validate_claim(preprocessed_data, comp_proof):
        # Calculate total water usage

        calculated_hash = calculate_endpoint_usage(preprocessed_data)

        is_claim_valid = calculated_hash == comp_proof

        return is_claim_valid
