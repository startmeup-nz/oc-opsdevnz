import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from oc_opsdevnz import OpenCollectiveClient, upsert_collective, upsert_host, upsert_project


@respx.mock
def test_upsert_host_creates_and_updates():
    long_desc = "Long copy"

    def _edit_account(request):
        payload = json.loads(request.content)
        account = payload["variables"]["account"]
        assert account["longDescription"] == long_desc
        return Response(
            200,
            json={
                "data": {
                    "editAccount": {
                        "id": "org1",
                        "slug": "example-org",
                        "name": "Example Org",
                        "description": "Platform team",
                        "currency": "NZD",
                        "longDescription": long_desc,
                        "tags": ["ops"],
                        "website": "https://example.org/",
                        "socialLinks": [{"type": "WEBSITE", "url": "https://example.org/"}],
                    }
                }
            },
        )

    responses = [
        Response(200, json={"data": {"account": None}}),  # lookup
        Response(
            200,
            json={
                "data": {
                    "createOrganization": {
                        "id": "org1",
                        "slug": "example-org",
                        "name": "Example Org",
                        "type": "ORGANIZATION",
                    }
                }
            },
        ),
        _edit_account,
    ]
    respx.post().mock(side_effect=responses)

    client = OpenCollectiveClient(token="t")
    result = upsert_host(
        client,
        {
            "name": "Example Org",
            "slug": "example-org",
            "description": "Platform team",
            "long_description": long_desc,
            "website": "https://example.org",
            "tags": ["ops"],
            "currency": "NZD",
        },
    )

    assert result.created is True
    assert result.updated is True
    assert result.warnings == []
    assert result.account["slug"] == "example-org"
    client.close()


@respx.mock
def test_upsert_host_no_update_when_same():
    respx.post().mock(
        side_effect=[
            Response(
                200,
                json={
                    "data": {
                        "account": {
                            "__typename": "Organization",
                            "id": "org1",
                            "slug": "example-org",
                            "name": "Example Org",
                            "type": "ORGANIZATION",
                            "isHost": True,
                            "description": "Platform team",
                            "longDescription": "Long copy",
                            "currency": "NZD",
                            "tags": ["ops"],
                            "website": "https://example.org/",
                            "socialLinks": [{"type": "WEBSITE", "url": "https://example.org/"}],
                            "stats": {"balance": {"currency": "NZD"}},
                        }
                    }
                },
            )
        ]
    )

    client = OpenCollectiveClient(token="t")
    result = upsert_host(
        client,
        {
            "name": "Example Org",
            "slug": "example-org",
            "description": "Platform team",
            "long_description": "Long copy",
            "website": "https://example.org",
            "tags": ["ops"],
            "currency": "NZD",
        },
    )

    assert result.created is False
    assert result.updated is False
    assert result.warnings == []
    assert result.account["slug"] == "example-org"
    client.close()


@respx.mock
def test_collective_create_and_apply_to_host():
    responses = [
        Response(
            200,
            json={
                "data": {
                    "account": {
                        "id": "host1",
                        "slug": "example-host",
                        "name": "Example Host",
                        "type": "ORGANIZATION",
                        "isHost": True,
                    }
                }
            },
        ),  # host check
        Response(200, json={"data": {"account": None}}),  # collective lookup
        Response(
            200,
            json={
                "data": {
                    "createCollective": {
                        "id": "col1",
                        "slug": "example-collective",
                        "name": "Example Collective",
                        "type": "COLLECTIVE",
                    }
                }
            },
        ),
        Response(
            200,
            json={
                "data": {
                    "editAccount": {
                        "id": "col1",
                        "slug": "example-collective",
                        "name": "Example Collective",
                        "description": "Example collective",
                        "tags": ["ops"],
                        "host": None,
                    }
                }
            },
        ),
        Response(
            200,
            json={
                "data": {
                    "applyToHost": {
                        "id": "col1",
                        "slug": "example-collective",
                        "host": {"slug": "example-host", "name": "Example Host"},
                    }
                }
            },
        ),
    ]
    respx.post().mock(side_effect=responses)

    client = OpenCollectiveClient(token="t")
    result = upsert_collective(
        client,
        {
            "name": "Example Collective",
            "slug": "example-collective",
            "description": "Example collective",
            "tags": ["ops"],
            "host_slug": "example-host",
            "apply_to_host": True,
            "host_apply_message": "Please host us for staging.",
        },
    )

    assert result.created is True
    assert result.updated is True
    assert result.applied_to_host is True
    assert result.account.get("host", {}).get("slug") == "example-host"
    client.close()


@respx.mock
def test_project_create_and_update():
    responses = [
        Response(
            200,
            json={
                "data": {
                    "account": {
                        "id": "col-parent",
                        "slug": "example-collective",
                        "name": "Example Collective",
                        "type": "COLLECTIVE",
                    }
                }
            },
        ),  # parent lookup
        Response(200, json={"data": {"account": None}}),  # project lookup
        Response(
            200,
            json={
                "data": {
                    "createProject": {
                        "id": "proj1",
                        "slug": "example-project",
                        "name": "Example Project",
                        "type": "PROJECT",
                        "parent": {"slug": "example-collective"},
                    }
                }
            },
        ),
        Response(
            200,
            json={
                "data": {
                    "editAccount": {
                        "id": "proj1",
                        "slug": "example-project",
                        "name": "Example Project",
                        "description": "Example project",
                        "tags": ["jobs"],
                    }
                }
            },
        ),
    ]
    respx.post().mock(side_effect=responses)

    client = OpenCollectiveClient(token="t")
    result = upsert_project(
        client,
        {
            "name": "Example Project",
            "slug": "example-project",
            "parent_slug": "example-collective",
            "description": "Example project",
            "tags": ["jobs"],
        },
    )

    assert result.created is True
    assert result.updated is True
    assert result.account["slug"] == "example-project"
    client.close()


def test_load_items_requires_list(tmp_path: Path):
    from oc_opsdevnz.operations import load_items

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"slug": "not-a-list"}))

    with pytest.raises(ValueError):
        load_items(bad)
