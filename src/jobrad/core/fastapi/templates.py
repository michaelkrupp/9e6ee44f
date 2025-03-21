from pathlib import Path
from typing import Final

from fastapi.templating import Jinja2Templates

FILE: Final[Path] = Path(__file__).resolve()
BASEDIR: Final[Path] = FILE.parents[2] / "templates"

print(BASEDIR)

templates: Final[Jinja2Templates] = Jinja2Templates(directory=str(BASEDIR))

CUSTOMER_TEMPLATE: Final[str] = "customer.html.j2"
AGENT_TEMPLATE: Final[str] = "agent.html.j2"
