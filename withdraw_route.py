import logging
from cartesi import Rollup, RollupData

from model.bank_db import bank_db
from helpers.setting import settings
from helpers.utils import str2hex, create_erc20_transfer_voucher
from helpers.inputs import WithdrawInput

# Configure logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# {'action': 'withdraw', 'amount': '500000000000000'}
def withdraw(json_router):
    """
    Registers a route for handling withdrawal requests in the JSON router.

    Args:
        json_router: The router object that manages JSON route handling.
    """
    @json_router.advance({'action': 'withdraw'})
    def withdraw(rollup: Rollup, data: RollupData) -> bool:
        """
        Handles a withdrawal request based on the provided Rollup data.

        Args:
            rollup (Rollup): The Rollup context.
            data (RollupData): Data related to the withdrawal request.

        Returns:
            bool: True if the withdrawal handling is successful, False otherwise.
        """
        LOGGER.info(f"Withdraw request: {data}")

        # Validate the withdrawal request payload
        payload = WithdrawInput.model_validate(data.json_payload())
        
        # Extract user and amount from the payload
        user = data.metadata.msg_sender
        amount = payload.amount

        # Attempt to withdraw the specified amount from the user's bank account
        try: 
            bank_db.withdraw(user,amount)
        except Exception as e:
            msg = f"Could not Withdraw {amount} for user {user}. Error: {e}"
            LOGGER.error(msg)
            rollup.report(str2hex(msg))
            return False

        # Generate a voucher for the ERC20 transfer
        voucher = create_erc20_transfer_voucher(settings.TOKEN_ERC20_ADDRESS,user,amount)
        rollup.voucher(voucher)

        # Send a notice with the current balance after withdrawal
        rollup.notice(str2hex(f"{{\"action\":\"withdraw\",\"address\":\"{user}\",\"balance\":\"{bank_db.balance(user)}\"}}"))

        LOGGER.info(f"Withdrawing {amount} for user {user}")

        return True
