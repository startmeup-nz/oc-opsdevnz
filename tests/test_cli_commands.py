from pathlib import Path
from types import SimpleNamespace

import respx
from httpx import Response

from oc_opsdevnz.cli import cmd_collectives, cmd_hosts, cmd_projects, cmd_whoami


def _args(file: Path) -> SimpleNamespace:
    return SimpleNamespace(
        config=None,
        file=str(file),
        token="mock-token",
        auth_mode="personal",
        log_requests=False,
        api_url="http://localhost:8765/graphql/v2",
        staging=False,
        test=False,
        prod=False,
        only=None,
    )


@respx.mock
def test_cmd_hosts_creates_organization(tmp_path: Path):
    respx.post("http://localhost:8765/graphql/v2").mock(
        side_effect=[
            Response(200, json={"data": {"account": None}}),
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
            Response(
                200,
                json={
                    "data": {
                        "editAccount": {
                            "id": "org1",
                            "slug": "example-org",
                            "name": "Example Org",
                            "description": "An example host",
                            "tags": ["example"],
                        }
                    }
                },
            ),
        ]
    )

    path = tmp_path / "hosts.yaml"
    path.write_text(
        "- name: Example Org\n"
        "  slug: example-org\n"
        "  description: An example host\n"
        "  tags: [example]\n"
    )
    assert cmd_hosts(_args(path)) == 0


@respx.mock
def test_cmd_collectives_creates_and_applies(tmp_path: Path):
    respx.post("http://localhost:8765/graphql/v2").mock(
        side_effect=[
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
            ),
            Response(200, json={"data": {"account": None}}),
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
                            "description": "An example collective",
                            "tags": ["example"],
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
    )

    path = tmp_path / "collectives.yaml"
    path.write_text(
        "- name: Example Collective\n"
        "  slug: example-collective\n"
        "  description: An example collective\n"
        "  tags: [example]\n"
        "  host_slug: example-host\n"
        "  apply_to_host: true\n"
    )
    assert cmd_collectives(_args(path)) == 0


@respx.mock
def test_cmd_projects_creates_project(tmp_path: Path):
    respx.post("http://localhost:8765/graphql/v2").mock(
        side_effect=[
            Response(
                200,
                json={
                    "data": {
                        "account": {
                            "id": "col1",
                            "slug": "example-collective",
                            "name": "Example Collective",
                            "type": "COLLECTIVE",
                        }
                    }
                },
            ),
            Response(200, json={"data": {"account": None}}),
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
                                "description": "An example project",
                                "tags": ["example"],
                            }
                        }
                    },
                ),
            ]
        )


    path = tmp_path / "projects.yaml"
    path.write_text(
        "- name: Example Project\n"
        "  slug: example-project\n"
        "  parent_slug: example-collective\n"
        "  description: An example project\n"
        "  tags: [example]\n"
    )
    assert cmd_projects(_args(path)) == 0


@respx.mock
def test_cmd_whoami_prints_account(tmp_path: Path):
    respx.post("http://localhost:8765/graphql/v2").mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "account": {
                        "id": "col1",
                        "slug": "example-collective",
                        "name": "Example Collective",
                        "type": "COLLECTIVE",
                    }
                }
            },
        )
    )

    args = _args(tmp_path / "unused.yaml")
    args.slug = "example-collective"
    assert cmd_whoami(args) == 0


@respx.mock
def test_cmd_hosts_missing_file_returns_error(tmp_path: Path):
    args = _args(tmp_path / "does-not-exist.yaml")
    assert cmd_hosts(args) == 2
