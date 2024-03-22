import logging
from cartesi import DApp, JSONRouter, URLRouter

from routes.hello_route import register_hello
from routes.register_deposite_route import register_deposit
from routes.generate_claim_route import generate_claim
from routes.withdraw_route import withdraw
from routes.finalize_claim_route import finalize_claim
from routes.generate_dispute_route import generate_dispute
from routes.validate_claim_route import validate_and_finalize


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

dapp = DApp()
json_router = JSONRouter()
dapp.add_router(json_router)
url_router = URLRouter()
dapp.add_router(url_router)


##################
# Testing Routes #
##################

register_hello(url_router, json_router)

#######################################
# default register and deposite route #
#######################################

register_deposit(dapp)

#################
# Claim Handler #
#################

generate_claim(json_router)

####################
# Withdraw Handler #
####################

withdraw(json_router=json_router)

##################
# Finalize Claim #
##################

finalize_claim(json_router=json_router)

####################
# Generate Dispute #
####################

generate_dispute(json_router=json_router)

###################
# Handle Validate #
###################

validate_and_finalize(json_router=json_router)

if __name__ == "__main__":
    dapp.run()
