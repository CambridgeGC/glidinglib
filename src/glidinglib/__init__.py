"""
GlidingLib: Shared library for gliding club operations and integrations.
"""

from glidinglib.models.combination_flight_model import CombinationFlight
from glidinglib.models.glidingapp_flight_model import GlidingAppFlight
from glidinglib.models.aerolog_flight_model import AerologFlight
from glidinglib.models.ktrax_flight_model import KtraxFlight
from glidinglib.models.glidingapp_account_model import GlidingAppAccount
from glidinglib.models.glidingapp_aircraft_model import GlidingAppAircraft
from glidinglib.models.aerolog_aircraft_model import AerologAircraft
from glidinglib.models.aerolog_tech_qualification import AerologTechQualification
from glidinglib.models.glidingapp_recency_model import (
    GlidingAppUserRecency,
    GlidingAppRecencyDetail,
    LaunchMethodSummary,
)

from glidinglib.mappers.glidingapp_recency_mapper import (
    map_glidingapp_recency,
    map_glidingapp_recency_detail,
)

from glidinglib.clients.glidingapp_client import GlidingAppClient
from glidinglib.clients.aerolog_client import AerologClient
from glidinglib.clients.ktrax_flight_client import KtraxFlightClient
from glidinglib.clients.ogn_ddb_client import OgnDdbClient
from glidinglib.clients.aerolog_aircraft_client import AerologAircraftClient

from glidinglib.services.glidingapp_flight_service import GlidingAppFlightService
from glidinglib.services.glidingapp_account_service import GlidingAppAccountService
from glidinglib.services.glidingapp_aircraft_service import GlidingAppAircraftService
from glidinglib.services.aerolog_flight_service import AerologFlightService
from glidinglib.services.ktrax_flight_service import KtraxFlightService

from glidinglib.auth.auth_service import GlidingAppAuthService
from glidinglib.auth.user_context import UserContext
from glidinglib.auth.fastapi_helpers import (
    get_current_user_from_request,
    create_user_dependency,
)

__version__ = "1.1.5"

__all__ = [
    # Version
    "__version__",
    # Models
    "CombinationFlight",
    "GlidingAppFlight",
    "AerologFlight",
    "KtraxFlight",
    "GlidingAppAccount",
    "GlidingAppAircraft",
    "AerologAircraft",
    "AerologTechQualification",
    "GlidingAppUserRecency",
    "GlidingAppRecencyDetail",
    "LaunchMethodSummary",
    # Mappers
    "map_glidingapp_recency",
    "map_glidingapp_recency_detail",
    # Clients
    "GlidingAppClient",
    "AerologClient",
    "KtraxFlightClient",
    "OgnDdbClient",
    "AerologAircraftClient",
    # Services
    "GlidingAppFlightService",
    "GlidingAppAccountService",
    "GlidingAppAircraftService",
    "AerologFlightService",
    "KtraxFlightService",
    # Auth
    "GlidingAppAuthService",
    "UserContext",
    "get_current_user_from_request",
    "create_user_dependency",
]
