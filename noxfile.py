import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.install("uv")
    session.run("uv", "pip", "install", ".[tests]")
    session.run("pytest", *args)
