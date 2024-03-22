from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class Status(str, Enum):
    """
    An enumeration class representing the possible statuses of a claim or dispute.

    Attributes:
        UNDEFINED: Represents an undefined status.
        OPEN: Represents an open status.
        DISPUTING: Indicates that the claim or dispute is currently being disputed.
        FINALIZED: Indicates that the claim or dispute has been finalized.
        DISPUTED: Represents a disputed status.
        VALIDATED: Indicates that the claim or dispute has been validated.
        CONTRADICTED: Indicates that the claim or dispute has been contradicted.
    """
    UNDEFINED = "undefined"
    OPEN = "open"
    DISPUTING = "disputing"
    FINALIZED = "finalized"
    DISPUTED = "disputed"
    VALIDATED = "validated"
    CONTRADICTED = "contradicted"

class User(BaseModel):
    """
    A class representing a user in the system.

    Attributes:
        open_claims (Dict[str, None]): A dictionary of open claims.
        open_disputes (Dict[str, None]): A dictionary of open disputes.
        total_disputes (int): The total number of disputes.
        won_disputes (int): The number of disputes won.
        total_claims (int): The total number of claims made.
        correct_claims (int): The number of claims that were correct.
    """
    open_claims: Dict[str, None] = Field(default_factory=dict)
    open_disputes: Dict[str, None] = Field(default_factory=dict)
    total_disputes: int
    won_disputes: int
    total_claims: int
    correct_claims: int

class Chunk(BaseModel):
    """
    Represents a data chunk.

    Attributes:
        data (bytes): The actual data in bytes.
    """

    data: bytes

    def __str__(self):
        """
        String representation of the chunk, showing its size in bytes.
        """
        return f"{len(self.data)}b"

class DataChunks(BaseModel):
    """
    A class representing a collection of data chunks.

    Attributes:
        chunks_data (Dict[int, Chunk]): A dictionary mapping chunk indices to their data.
        total_chunks (int): The total number of chunks.
    """

    chunks_data: Dict[int, Chunk]
    total_chunks: int

    def __str__(self):
        """
        String representation of the data chunks, showing total chunks and their size.
        """
        size = sum(len(chunk.data) for chunk in self.chunks_data.values())
        chunk_indexes = list(self.chunks_data.keys())
        return f"TotalChunks: {self.total_chunks}, CurrentSize: {size}, Chunks: {chunk_indexes}"

class Claim(BaseModel):
    """
    A class representing a claim in the system.

    Attributes:
        user_address (str): The address of the user making the claim.
        disputing_user_address (Optional[str]): The address of the user disputing the claim.
        timestamp_of_claim (str): The timestamp when the claim was made.
        status (Status): The current status of the claim.
        collateral (int): The collateral amount for the claim.
        compProof (str): The computation proof associated with the claim.
        compCID (str): The computation CID of the claim.
        prepCID (str): The preparation CID of the claim.
        lastUpdated (int): The last updated timestamp of the claim.
    """

    user_address: str
    disputing_user_address: Optional[str]
    timestamp_of_claim: str
    status: Status
    collateral: int
    compProof: str
    compCID: str
    prepCID: str
    lastUpdated: int

class SimplifiedClaim(BaseModel):
    """
    A simplified representation of a claim.

    Attributes:
        id (str): The unique identifier of the claim.
        status (Status): The current status of the claim.
        value (int): The value or amount of the claim.
    """
    id: str
    status: Status
    value: int

# New Models
class IoTDevice(BaseModel):
    """
    Represents an IoT device in the system.

    Attributes:
        device_id (str): The unique identifier of the device.
        location (str): The location of the device.
        device_type (str): The type of the IoT device.
        owner_wallet (str): The wallet address of the device's owner.
    """
    device_id: str
    location: str
    device_type: str
    owner_wallet: str

class WaterUsageRecord(BaseModel):
    """
    Represents a water usage record from an IoT device.

    Attributes:
        record_id (int): The unique identifier of the record.
        device_id (str): The ID of the device that generated the record.
        timestamp (int): The timestamp when the record was generated.
        water_usage (float): The amount of water used.
    """
    record_id: int
    device_id: str
    timestamp: int
    water_usage: float

class Dispute(BaseModel):
    """
    Represents a dispute in the system.

    Attributes:
        dispute_id (int): The unique identifier of the dispute.
        claim_id (int): The ID of the associated claim.
        challenger_wallet (str): The wallet address of the challenger.
        reason (str): The reason for the dispute.
        status (Status): The current status of the dispute.
    """
    dispute_id: int
    claim_id: int
    challenger_wallet: str
    reason: str
    status: Status

class ValidatorNode(BaseModel):
    """
    Represents a validator node in the network.

    Attributes:
        node_id (int): The unique identifier of the node.
        wallet (str): The wallet address associated with the node.
        reputation (int): The reputation score of the node.
    """
    node_id: int
    wallet: str
    reputation: int

class AggregatorNode(BaseModel):
    """
    Represents an aggregator node in the network.

    Attributes:
        node_id (int): The unique identifier of the node.
        wallet (str): The wallet address associated with the node.
        aggregated_records (List[WaterUsageRecord]): A list of aggregated water usage records.
    """
    node_id: int
    wallet: str
    aggregated_records: List[WaterUsageRecord] = []

# Additional classes and functions can be implemented as needed to support operations like CRUD operations, data validation, etc.
