import logging

from helpers.utils import (
    str2hex,
    hex2bin,
    create_erc20_transfer_voucher,
    decode_erc20_deposit,
)
from cartesi import Rollup, RollupData

from model.bank_db import bank_db
from model.user_db import users_db
from helpers.setting import settings

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def register_deposit(dapp):
    """
    Registers a route for handling deposits in the DApp.

    Args:
        dapp: The DApp object that manages route handling.
    """

    def process_deposit_and_add_user(rollup: Rollup, data):
        """
        Processes an ERC20 deposit and adds the user to the database if not present.

        Args:
            rollup (Rollup): The Rollup context.
            data: The data associated with the deposit request.

        Returns:
            bool: True if the deposit is processed successfully, False otherwise.
        """
        LOGGER.info("Processing Deposit")
        binary = hex2bin(data.payload)

        # Decode ERC20 deposit data
        erc20_deposit = decode_erc20_deposit(binary)

        # Extract necessary data from the deposit
        token_address = erc20_deposit["token_address"]
        depositor = erc20_deposit["depositor"]
        amount = erc20_deposit["amount"]

        # Check if the deposited token is accepted
        if token_address.lower() != settings.TOKEN_ERC20_ADDRESS.lower():
            # If not accepted, create a voucher to return the token
            voucher = create_erc20_transfer_voucher(token_address, depositor, amount)
            LOGGER.info(f"Token not accepted, sending it back, voucher {voucher}")
            rollup.voucher(voucher)
            return True

        # Check if user exists, if not, create a new user
        if not users_db.get_user(depositor):
            LOGGER.info(f"Creating new user for address: {depositor}")
            users_db.create_user(depositor)

        # Handle the deposit in the bank database
        try:
            LOGGER.info("Handling wallet deposit")
            bank_db.deposit(depositor, amount)
        except Exception as e:
            # Report any errors during the deposit process
            msg = f"Could not deposit {amount} for user {depositor}. Error: {e}"
            LOGGER.error(msg)
            rollup.report(str2hex(msg))
            return False

        # Send a notice about the successful deposit
        LOGGER.info(
            f'Sending notice for deposited amount: {{"action":"deposit","address":"{depositor}","balance":"{bank_db.balance(depositor)}"}}'
        )
        rollup.notice(
            str2hex(
                f'{{"action":"deposit","address":"{depositor}","balance":"{bank_db.balance(depositor)}"}}'
            )
        )

        return True

    @dapp.advance()
    def default_handler(rollup: Rollup, data: RollupData) -> bool:
        """
        The default handler for the deposit route.

        Args:
            rollup (Rollup): The Rollup context.
            data (RollupData): Data related to the deposit request.

        Returns:
            bool: True if a relevant action is performed, False otherwise.
        """
        LOGGER.info("Running Default Handler")

        # Process ERC20 deposit if the sender is the ERC20 portal address
        if data.metadata.msg_sender.lower() == settings.PORTAL_ERC20_ADDRESS.lower():
            LOGGER.info(f"Processing Erc20 deposit: {data}")
            return process_deposit_and_add_user(rollup, data)

        # Report if there's nothing to process
        msg = "Nothing to do here"
        LOGGER.warning(msg)
        rollup.report(str2hex(msg))
        return False
