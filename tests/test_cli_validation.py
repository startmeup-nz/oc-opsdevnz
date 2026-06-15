import pytest

from oc_opsdevnz.cli import (
    _validate_collective_item,
    _validate_host_item,
    _validate_project_item,
)


def test_host_item_with_parent_slug_rejected():
    with pytest.raises(ValueError, match="Host item 'example-project' has parent_slug"):
        _validate_host_item(
            {
                "slug": "example-project",
                "name": "Example Project",
                "parent_slug": "example-collective",
            }
        )


def test_host_item_with_parent_slug_camel_case_rejected():
    with pytest.raises(ValueError, match="Host item 'example-project' has parent_slug"):
        _validate_host_item(
            {
                "slug": "example-project",
                "name": "Example Project",
                "parentSlug": "example-collective",
            }
        )


def test_host_item_with_host_slug_rejected():
    with pytest.raises(ValueError, match="Host item 'example-collective' has collective fields"):
        _validate_host_item(
            {
                "slug": "example-collective",
                "name": "Example Collective",
                "host_slug": "example-host",
                "apply_to_host": True,
            }
        )


def test_host_item_without_parent_slug_accepted():
    _validate_host_item({"slug": "example-host", "name": "Example Host"})


def test_collective_item_with_parent_slug_rejected():
    with pytest.raises(ValueError, match="Collective item 'example-project' has parent_slug"):
        _validate_collective_item(
            {
                "slug": "example-project",
                "name": "Example Project",
                "parent_slug": "example-collective",
            }
        )


def test_collective_item_with_host_fields_rejected():
    with pytest.raises(ValueError, match="Collective item 'example-org' has host-only fields"):
        _validate_collective_item(
            {
                "slug": "example-org",
                "name": "Example Org",
                "legal_name": "Example Org Ltd",
                "currency": "NZD",
            }
        )


def test_collective_item_without_parent_slug_accepted():
    _validate_collective_item({"slug": "example-collective", "name": "Example Collective"})


def test_project_item_without_parent_slug_rejected():
    with pytest.raises(ValueError, match="Project item 'example-project' is missing parent_slug"):
        _validate_project_item({"slug": "example-project", "name": "Example Project"})


def test_project_item_with_parent_slug_accepted():
    _validate_project_item(
        {"slug": "example-project", "name": "Example Project", "parent_slug": "example-collective"}
    )
