
from flask import request

from assemblyline.datastore.exceptions import SearchException
from assemblyline_ui.config import STORAGE
from assemblyline_ui.api.base import api_login, make_api_response, make_subapi_blueprint


SUB_API = 'error'
error_api = make_subapi_blueprint(SUB_API, api_version=4)
error_api._doc = "Perform operations on service errors"


@error_api.route("/<error_key>/", methods=["GET"])
@api_login(required_priv=['R'])
def get_error(error_key, **kwargs):
    """
    Get the error details for a given error key

    Variables:
    error_key         => Error key to get the details for

    Arguments:
    None

    Data Block:
    None

    Result example:
    {
        KEY: VALUE,   # All fields of an error in key/value pair
    }
    """
    user = kwargs['user']
    data = STORAGE.error.get(error_key, as_obj=False)

    if user and data:
        return make_api_response(data)
    else:
        return make_api_response("", "You are not allowed to see this error...", 403)


@error_api.route("/list/", methods=["GET"])
@api_login(require_type=['admin'])
def list_errors(**_):
    """
    List all error in the system (per page)

    Variables:
    None

    Arguments:
    offset            => Offset at which we start giving errors
    query             => Query to apply to the error list
    rows              => Numbers of errors to return
    sort              => Sort order
    use_archive       => List error from archive as well (Default: False)
    track_total_hits  => Track the total number of item that match the query (Default: 10 000)

    Data Block:
    None

    Result example:
    {"total": 201,                # Total errors found
     "offset": 0,                 # Offset in the error list
     "count": 100,                # Number of errors returned
     "items": []                  # List of error blocks
    }
    """
    offset = int(request.args.get('offset', 0))
    rows = int(request.args.get('rows', 100))
    query = request.args.get('query', "id:*") or "id:*"
    filters = request.args.getlist('filters', None) or None
    sort = request.args.get('sort', "created desc")
    use_archive = request.args.get('use_archive', "false").lower() in ['true', '']
    track_total_hits = request.args.get('track_total_hits', False)

    try:
        return make_api_response(STORAGE.error.search(query, offset=offset, rows=rows, as_obj=False,
                                                      sort=sort, use_archive=use_archive,
                                                      track_total_hits=track_total_hits, filters=filters))
    except SearchException as e:
        return make_api_response("", f"The specified search query is not valid. ({e})", 400)
