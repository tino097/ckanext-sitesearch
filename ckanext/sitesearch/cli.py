import sys
import logging
import traceback

import click
from sqlalchemy.sql.expression import true, false

from ckan import model
from ckan.plugins import toolkit

from ckanext.sitesearch.lib.index import (
    index_organization,
    index_group,
    index_user,
    commit,
)

log = logging.getLogger(__name__)


def get_commands():
    return [sitesearch]


@click.group()
def sitesearch():
    """Search index utilities for CKAN entities."""
    pass


@sitesearch.command("rebuild")
@click.argument("entity_type")
@click.argument("entity_id", required=False)
@click.option(
    "-e",
    "--commit-each",
    is_flag=True,
    help="Perform a commit after indexing each dataset. This"
    "ensures that changes are immediately available on the"
    "search, but slows significantly the process. Default"
    "is false.",
)
@click.option(
    "-i", "--force", is_flag=True, help="Ignore exceptions when rebuilding the index"
)
@click.option(
    "-q", "--quiet", help="Do not output index rebuild progress", is_flag=True
)
def rebuild(entity_type, commit_each, force, quiet, entity_id=None):
    """Re-index all entitities of a particular type"""

    defer_commit = not commit_each

    if entity_type in ("orgs", "org", "organizations", "organisations"):
        _rebuild_orgs(defer_commit, force, quiet, entity_id)
    elif entity_type in ("groups", "group"):
        _rebuild_groups(defer_commit, force, quiet, entity_id)
    elif entity_type in ("users", "user"):
        _rebuild_users(defer_commit, force, quiet, entity_id)
    else:
        toolkit.error_shout("Unknown entity type: {}".format(entity_type))


def _rebuild_orgs(defer_commit, force, quiet, entity_id):

    if entity_id:
        org = model.Group.get(entity_id)
        if not org:
            raise click.UsageError("Organization not found: {}".format(entity_id))
        org_ids = [org.id]
    else:
        org_ids = [
            r[0]
            for r in model.Session.query(model.Group.id)
            .filter(model.Group.is_organization == true())
            .filter(model.Group.state != "deleted")
            .all()
        ]

    _rebuild_entities(org_ids, "organization", "organization_show", defer_commit, force)


def _rebuild_groups(defer_commit, force, quiet, entity_id):

    if entity_id:
        group = model.Group.get(entity_id)
        if not group:
            raise click.UsageError("Group not found: {}".format(entity_id))
        group_ids = [group.id]
    else:
        group_ids = [
            r[0]
            for r in model.Session.query(model.Group.id)
            .filter(model.Group.is_organization == false())
            .filter(model.Group.state != "deleted")
            .all()
        ]

    _rebuild_entities(group_ids, "group", "group_show", defer_commit, force)


def _rebuild_users(defer_commit, force, quiet, entity_id):

    if entity_id:
        user = model.User.get(entity_id)
        if not user:
            raise click.UsageError("User not found: {}".format(entity_id))
        user_ids = [user.id]
    else:
        user_ids = [
            r[0]
            for r in model.Session.query(model.User.id)
            .filter(model.User.state != "deleted")
            .all()
        ]

    _rebuild_entities(user_ids, "user", "user_show", defer_commit, force, quiet)


indexers = {
    "organization": index_organization,
    "group": index_group,
    "user": index_user,
}


def _rebuild_entities(entity_ids, entity_name, action_name, defer_commit, force, quiet):

    total_entities = len(entity_ids)
    context = {"ignore_auth": True}
    for counter, entity_id in enumerate(entity_ids):
        if not quiet:
            sys.stdout.write(
                "\rIndexing {} {}/{}".format(entity_name, counter + 1, total_entities)
            )
            sys.stdout.flush()
        try:
            data_dict = toolkit.get_action(action_name)(context, {"id": entity_id})
            indexers[entity_name](data_dict, defer_commit)
        except Exception as e:
            log.error(
                "Error while indexing {} {}: {}".format(entity_name, entity_id, repr(e))
            )
            if force:
                log.exception(traceback.format_exc())
                continue
            else:
                raise

    if defer_commit:
        commit()
