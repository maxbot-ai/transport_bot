"""Common methods."""

import functools
import logging

from flask import jsonify
from sqlalchemy import exc
from webargs import flaskparser

from transport_bot.api_service.schema import app

logger = logging.getLogger(__name__)

HEADERS = {"Content-Type": "application/json"}
use_body = functools.partial(flaskparser.use_args, location="json", error_status_code=400)


def resp(status=200, data=None):
    """Return response for http status."""
    logger.debug("response: status=%s, data=%s", status, data)
    return jsonify(data or {}), status


def conflict(error):
    """Return response for 409 (conflict) http status."""
    return resp(409, {"detail": error})


@app.errorhandler(exc.IntegrityError)
def storage_error(error):
    """Return response for 409 (conflict) http status."""
    return conflict(str(error))
