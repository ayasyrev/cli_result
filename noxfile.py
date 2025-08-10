import nox


nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.install("-e .[test]")
    session.run("pytest", *args)
