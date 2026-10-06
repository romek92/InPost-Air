import os
from unittest.mock import AsyncMock, patch
import pytest
import pytest_socket
from custom_components.inpost_air.api import InPostApi
from custom_components.inpost_air.const import USER_AGENT
from custom_components.inpost_air.models import (
    InPostAirPoint,
    InPostAirPointCoordinates,
)


@pytest.fixture()
def _allow_inpost_requests():
    pytest_socket.enable_socket()
    pytest_socket.socket_allow_hosts(["inpost.pl"])


@pytest.mark.parametrize("expected_lingering_timers", [True])
@pytest.mark.api
async def test_parcel_lockers_list(hass, _allow_inpost_requests):
    response = await InPostApi(hass).get_parcel_lockers_list()
    assert response is not None


@pytest.mark.parametrize("expected_lingering_timers", [True])
@pytest.mark.api
async def test_parcel_locker_search(hass, _allow_inpost_requests):
    response = await InPostApi(hass).search_parcel_locker("AJE01BAPP")
    assert response is not None


@pytest.mark.skipif(
    os.environ.get("CI") == "true", reason="InPost blocks Github IP address"
)
@pytest.mark.parametrize("expected_lingering_timers", [True])
@pytest.mark.api
async def test_find_parcel_locker_id(hass, _allow_inpost_requests):
    response = await InPostApi(hass).find_parcel_locker_id(
        InPostAirPoint(
            "AJE01BAPP",
            1,
            "Market Dino",
            "",
            "",
            "006",
            "Andrzejewo",
            "andrzejewo",
            "Warszawska",
            "mazowieckie",
            "07-305",
            "62A",
            "24/7",
            "[]",
            InPostAirPointCoordinates(52.83679, 22.20968),
            0,
            1,
        )
    )
    assert response is not None


@pytest.mark.skipif(
    os.environ.get("CI") == "true", reason="InPost blocks Github IP address"
)
@pytest.mark.parametrize("expected_lingering_timers", [True])
@pytest.mark.api
async def test_air_data(hass, _allow_inpost_requests):
    response = await InPostApi(hass).get_parcel_locker_air_data("AJE01BAPP", "56311")
    assert response is not None


async def test_user_agent_header_in_requests(hass):
    api = InPostApi(hass)
    with patch.object(api.session, "request") as mock_request:
        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        mock_response.json = AsyncMock(return_value={"items": []})
        mock_request.return_value = mock_response

        await api.get_parcel_lockers_list()

        mock_request.assert_called_once()
        _, kwargs = mock_request.call_args
        assert kwargs["headers"]["User-Agent"] == USER_AGENT


async def test_user_agent_header_with_custom_headers(hass):
    api = InPostApi(hass)
    with patch.object(api.session, "request") as mock_request:
        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        mock_response.json = AsyncMock(
            return_value={
                "message": "ok",
                "air_index_level": "GOOD",
                "air_sensors": [],
            }
        )
        mock_request.return_value = mock_response

        await api.get_parcel_locker_air_data("AJE01BAPP", "56311")

        mock_request.assert_called_once()
        _, kwargs = mock_request.call_args
        assert kwargs["headers"]["User-Agent"] == USER_AGENT
        assert kwargs["headers"]["X-Requested-With"] == "XMLHttpRequest"
