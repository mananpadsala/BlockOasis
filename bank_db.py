from pydantic import BaseModel
import logging

# Set up the logger for this module.
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Wallet(BaseModel):
    """
    A simple Wallet class to manage the balance of an asset.
    Currently, it is designed to handle a single asset type.

    Attributes:
        owner (str): The owner of the wallet.
        balance (int): The balance of the wallet. Defaults to 0.

    TODO: Add functionality to store public keys.
    """

    owner: str
    balance: int = 0


class BankDatabase:
    """
    A class representing a simplistic bank database.
    Manages wallets and their transactions.

    Attributes:
        wallets (dict[str, Wallet]): A dictionary of wallets with addresses as keys.
    """

    def __init__(self):
        # Initializes an empty dictionary to store wallets.
        self.wallets: dict[str, Wallet] = {}

    def _get_wallet(self, address: str) -> Wallet:
        """
        Retrieves the wallet associated with the given address.
        If the wallet doesn't exist, a new one is created.

        Parameters:
            address (str): The address of the wallet.

        Returns:
            Wallet: The wallet object.
        """
        addr = address.lower()
        wallet = self.wallets.get(addr)
        if wallet is None:
            new_wallet = Wallet(owner=addr)
            self.wallets[addr] = new_wallet
            wallet = new_wallet
        return wallet

    def deposit(self, address: str, amount: int):
        """
        Deposits the specified amount into the wallet of the given address.

        Parameters:
            address (str): The address to deposit to.
            amount (int): The amount to deposit.

        Raises:
            Exception: If the deposit amount is less than or equal to zero.
        """
        if amount <= 0:
            raise Exception("invalid amount")
        LOGGER.info(f"Depositing amount: {amount} to address: {address}")
        wallet = self._get_wallet(address)
        wallet.balance += amount

    def withdraw(self, address: str, amount: int):
        """
        Withdraws the specified amount from the wallet of the given address.

        Parameters:
            address (str): The address to withdraw from.
            amount (int): The amount to withdraw.

        Raises:
            Exception: If the withdraw amount is invalid or insufficient funds.
        """
        if amount <= 0:
            raise Exception("invalid amount")
        wallet = self._get_wallet(address)
        if wallet.balance < amount:
            raise Exception("insufficient funds")
        wallet.balance -= amount

    def transfer(self, sender: str, receiver: str, amount: int):
        """
        Transfers the specified amount from the sender's wallet to the receiver's wallet.

        Parameters:
            sender (str): The address of the sender.
            receiver (str): The address of the receiver.
            amount (int): The amount to transfer.

        Raises:
            Exception: If the transfer amount is less than or equal to zero.
        """
        if amount <= 0:
            raise Exception("invalid amount")
        self.withdraw(sender, amount)
        self.deposit(receiver, amount)

    def balance(self, address: str) -> int:
        """
        Returns the balance of the wallet associated with the given address.

        Parameters:
            address (str): The address of the wallet.

        Returns:
            int: The balance of the wallet.
        """
        wallet = self._get_wallet(address)
        return wallet.balance


# Instantiate a BankDatabase object for use.
bank_db = BankDatabase()
