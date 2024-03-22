from helpers.utils import str2hex, to_jsonhex
from cartesi import Rollup, RollupData

def register_hello(url_router, json_router):
    """
    Registers 'hello' routes in both URL and JSON routers.

    Args:
        url_router: The router object that manages URL-based route handling.
        json_router: The router object that manages JSON-based route handling.
    """

    @url_router.advance("hello/")
    def hello_world_advance(rollup: Rollup, data: RollupData) -> bool:
        """
        Advances the state of the rollup machine upon accessing the 'hello/' URL.
        This function sends a 'Hello World' notice to the rollup machine.

        Args:
            rollup (Rollup): The Rollup context.
            data (RollupData): Data related to the request.

        Returns:
            bool: Always returns True, indicating successful handling.
        """
        rollup.notice(str2hex("Hello World"))
        return True

    @url_router.inspect("hello/")
    def hello_world_inspect(rollup: Rollup, data: RollupData) -> bool:
        """
        Inspects the state of the rollup machine upon accessing the 'hello/' URL.
        This function reports 'Hello World-Jhingalalahuhu' to the rollup machine.

        Args:
            rollup (Rollup): The Rollup context.
            data (RollupData): Data related to the request.

        Returns:
            bool: Always returns True, indicating successful handling.
        """
        rollup.report(str2hex("Hello World-Jhingalalahuhu"))
        return True

    # JSON route for 'hello' with specific payload handling
    @json_router.advance({"hello": "world"})
    def handle_advance_set(rollup: Rollup, data: RollupData):
        """
        Handles a specific JSON payload where 'hello' is set to 'world'.
        This function responds to the specific payload by reporting an action response.

        Args:
            rollup (Rollup): The Rollup context.
            data (RollupData): Data related to the request.

        Returns:
            bool: Always returns True, indicating successful handling.
        """
        payload_data = data.json_payload()
        rollup.report(to_jsonhex({"action": payload_data["action"]}))
        return True
