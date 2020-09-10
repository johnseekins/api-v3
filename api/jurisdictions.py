from enum import Enum
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from .db import SessionLocal, get_db, models
from .schemas import Jurisdiction, JurisdictionClassification
from .pagination import Pagination
from .auth import apikey_auth
from .utils import jurisdiction_filter


class JurisdictionInclude(str, Enum):
    organizations = "organizations"
    legislative_sessions = "legislative_sessions"


class JurisdictionPagination(Pagination):
    ObjCls = Jurisdiction
    IncludeEnum = JurisdictionInclude
    include_map_overrides = {}  # no overrides


router = APIRouter()


@router.get(
    "/jurisdictions",
    response_model=JurisdictionPagination.response_model(),
    response_model_exclude_none=True,
    tags=["jurisdictions"],
)
async def jurisdiction_list(
    classification: Optional[JurisdictionClassification] = Query(
        None, description="Filter returned jurisdictions by type."
    ),
    include: List[JurisdictionInclude] = Query(
        [], description="Additional information to include in response."
    ),
    db: SessionLocal = Depends(get_db),
    pagination: JurisdictionPagination = Depends(),
    auth: str = Depends(apikey_auth),
):
    """
    Get list of supported Jurisdictions, a Jurisdiction is a state or municipality.
    """
    # TODO: remove this conversion once database is updated
    if classification == "state":
        classification = "government"
    query = db.query(models.Jurisdiction).order_by(models.Jurisdiction.name)

    # handle parameters
    if classification:
        query = query.filter(models.Jurisdiction.classification == classification)

    resp = pagination.paginate(query, includes=include)

    # TODO: this should be removed too (see above note)
    for result in resp["results"]:
        if result.classification == "government":
            result.classification = "state"

    return resp


@router.get(
    # we have to use the Starlette path type to allow slashes here
    "/jurisdictions/{jurisdiction_id:path}",
    response_model=Jurisdiction,
    response_model_exclude_none=True,
    tags=["jurisdictions"],
)
async def jurisdiction_detail(
    jurisdiction_id: str,
    include: List[JurisdictionInclude] = Query(
        [], description="Additional includes for the Jurisdiction response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """ Get details on a single Jurisdiction (e.g. state or municipality). """
    query = db.query(models.Jurisdiction).filter(
        jurisdiction_filter(jurisdiction_id, jid_field=models.Jurisdiction.id)
    )
    result = JurisdictionPagination.detail(query, includes=include)
    # TODO: this should be removed too (see above note)
    if result.classification == "government":
        result.classification = "state"
    return result
