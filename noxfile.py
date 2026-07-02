import logging

import nox
import nox_poetry

# Reuse virtual environments to speed up subsequent runs and
# avoid unnecessary re-installation of dependencies.
nox.options.reuse_existing_virtualenvs = True

logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Reformat source files in-place (fixes, does not just check).
# To only check without modifying, run the lint session.
@nox_poetry.session(python="3.13", tags=["style", "fix"])
def format(session: nox_poetry.Session) -> None:
    session.run("make", "format", external=True)


@nox_poetry.session(python="3.13", tags=["style", "check"])
def lint(session: nox_poetry.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", "src", "tests")


@nox_poetry.session(python="3.13", tags=["tests"])
def tests(session: nox_poetry.Session) -> None:
    session.install(".", "pytest")
    session.env["PYTHONPATH"] = "src"
    session.run("pytest", "tests", "-v")
