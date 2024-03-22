# from pydantic import BaseModel, Field
from typing import Dict, Optional

from .model import User

class UsersDatabase:
    """
    A class representing a database for storing and managing user data.

    Attributes:
        users (Dict[str, User]): A dictionary mapping user IDs to User objects.
    """

    def __init__(self):
        # Initializes an empty dictionary for storing users.
        self.users: Dict[str, User] = {}

    def create_user(self, user_id: str) -> User:
        """
        Creates a new user with default values and adds them to the database.

        Parameters:
            user_id (str): The unique identifier for the new user.

        Returns:
            User: The newly created User object.
        """
        new_user = User(
            open_claims={},
            open_disputes={},
            total_disputes=0,
            won_disputes=0,
            total_claims=0,
            correct_claims=0,
        )
        self.users[user_id] = new_user
        return new_user

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Updates the information of a specific user.

        Parameters:
            user_id (str): The unique identifier of the user to be updated.
            **kwargs: Variable keyword arguments for updating user attributes.

        Returns:
            Optional[User]: The updated User object if found, otherwise None.
        """
        user = self.users.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return user
        return None

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Parameters:
            user_id (str): The unique identifier of the user.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        return self.users.get(user_id)

    def get_all_users(self) -> Dict[str, User]:
        """
        Retrieves all users in the database.

        Returns:
            Dict[str, User]: A dictionary of all stored User objects.
        """
        return self.users
    
    def won_claim(self, user_id, claimID) -> Optional[User]:
        """
        Updates the user's statistics upon winning a claim.

        Parameters:
            user_id (str): The unique identifier of the user.
            claimID (str): The ID of the claim the user won.

        Returns:
            Optional[User]: The updated User object if found, otherwise None.
        """
        user = self.users.get(user_id)
        if user:
            user.total_claims += 1
            user.correct_claims += 1
            del user.open_claims[claimID]
            return user
        return None
    
    def lost_claim(self, user_id, claimID) -> Optional[User]:
        """
        Updates the user's statistics upon losing a claim.

        Parameters:
            user_id (str): The unique identifier of the user.
            claimID (str): The ID of the claim the user lost.

        Returns:
            Optional[User]: The updated User object if found, otherwise None.
        """
        user = self.users.get(user_id)
        if user:
            user.total_claims += 1
            del user.open_claims[claimID]
            return user
        return None

# Instantiate a UsersDatabase object for use.
users_db = UsersDatabase()
