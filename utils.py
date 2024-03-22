import json
from eth_abi import encode
from .setting import settings

def str2hex(string: str) -> str:
    """
    Encodes a string as a hex string.

    Parameters:
        string (str): The string to be encoded.

    Returns:
        str: The hex representation of the input string, prefixed with '0x'.
    """
    return "0x" + string.encode("utf-8").hex()

def to_jsonhex(data: dict) -> str:
    """
    Encodes a dictionary as a JSON string and then to a hex string.

    Parameters:
        data (dict): The dictionary to be encoded.

    Returns:
        str: The hex representation of the JSON-encoded dictionary.
    """
    return str2hex(json.dumps(data))

def hex2bin(hexstr: str) -> bytes:
    """
    Converts a hex string to binary.

    Parameters:
        hexstr (str): The hex string to be converted. Assumes the string starts with '0x'.

    Returns:
        bytes: The binary representation of the hex string.
    """
    return bytes.fromhex(hexstr[2:])

def bin2hex(binary: bytes) -> str:
    """
    Converts binary data to a hex string.

    Parameters:
        binary (bytes): The binary data to be converted.

    Returns:
        str: The hex representation of the binary data, prefixed with '0x'.
    """
    return "0x" + binary.hex()

def decode_erc20_deposit(binary: bytes) -> dict:
    """
    Decodes ERC20 deposit data from binary format.

    Parameters:
        binary (bytes): The binary data representing an ERC20 deposit transaction.

    Returns:
        dict: A dictionary containing the depositor's address, token address, amount, and additional data.
    """
    token_address = binary[1:21]
    depositor = binary[21:41]
    amount = int.from_bytes(binary[41:73], "big")
    data = binary[73:]
    return {
        "depositor": bin2hex(depositor),
        "token_address": bin2hex(token_address),
        "amount": amount,
        "data": data,
    }

def create_erc20_transfer_voucher(token_address: str, receiver: str, amount: int) -> dict:
    """
    Creates an ERC20 transfer voucher, which can be used for token transfers.

    Parameters:
        token_address (str): The ERC20 token address.
        receiver (str): The address of the receiver.
        amount (int): The amount of tokens to be transferred.

    Returns:
        dict: A dictionary containing the destination address and the payload for the transfer.
    """
    data = encode(["address", "uint256"], [receiver, amount])
    voucher_payload = bin2hex(settings.ERC20_TRANSFER_FUNCTION_SELECTOR + data)
    return {"destination": token_address, "payload": voucher_payload}
