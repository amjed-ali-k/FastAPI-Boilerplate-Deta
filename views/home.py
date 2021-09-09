import fastapi
from fastapi import responses
router = fastapi.APIRouter()


@router.get('/', include_in_schema=False)
def index():
    return responses.RedirectResponse(url='/docs')


@router.get('/favicon.ico', include_in_schema=False)
def favicon():
    return fastapi.responses.RedirectResponse(url='/static/icons/favicon.ico')
