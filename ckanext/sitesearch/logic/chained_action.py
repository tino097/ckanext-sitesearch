from ckan.plugins import toolkit

from ckanext.sitesearch.lib import index


@toolkit.chained_action
def organization_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_organization(data_dict)

    return data_dict


@toolkit.chained_action
def organization_update(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_organization(data_dict)

    return data_dict


@toolkit.chained_action
def organization_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_organization(data_dict["id"])

    return data_dict


@toolkit.chained_action
def group_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_group(data_dict)

    return data_dict


@toolkit.chained_action
def group_update(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_group(data_dict)

    return data_dict


@toolkit.chained_action
def group_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_group(data_dict["id"])

    return data_dict


@toolkit.chained_action
def user_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_user(data_dict)

    return data_dict


@toolkit.chained_action
def user_update(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_user(data_dict)


@toolkit.chained_action
def user_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_user(data_dict["id"])


@toolkit.chained_action
def pages_update(up_func, context, data_dict):

    up_func(context, data_dict)
    page = toolkit.get_action("ckanext_pages_show")(
        context, {"page": data_dict["page"]}
    )
    index.index_page(page)


@toolkit.chained_action
def pages_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_page(data_dict["id"])
